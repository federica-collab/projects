#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 17:22:03 2019
@author: federica
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request, jsonify
from flask import Response
import os
import json
import jsonschema
from jsonschema import validate
import sys

from data_import import *
from filter_func import *
from fdd_class import *
from outdict_func import *
from data_by_id import *
from schema import *
from acc_2_integration import *
from acc_integration import *

import pandas as pd

app = Flask(__name__)

@app.route('/FDD', methods=['GET','POST'])


def main():

    data = pd.DataFrame()
    par_dict = {}
    result,msg = {},{}

    par = request.get_json()
    '''parameters validation'''
    try:
        schema = fdd_schema
        # And validate the result
        validate(instance=par, schema=schema)
        code = 0
        success = True

    except jsonschema.exceptions.ValidationError:
        msg = sys.exc_info()[1]
        "well-formed but invalid JSON:"
        success = 'False'
        code, msg = -4, msg.message

    except json.decoder.JSONDecodeError:
        msg = sys.exc_info()[1]
        "poorly-formed text, not JSON:"
        success = 'False'
        code, message = -5, msg.message
    details=[]
    if code == 0:

        freqs = []
        d,cont, details = [],[],[]
        length = []
        for device in par["device_id"]:
            current_x = str(device)+"_x"
            current_y = str(device)+"_y"
            current_z = str(device)+"_z"
            data_current = pd.DataFrame()

            try:
                '''Extraction of accelerometric data from devices
                '''
                x, y, z, freq = GetTimedSamplesByKey(device, par['time_min'], par['time_max'])
                d.append(1)

                if len(x) != 0:

                    length.append(len(x))
                    if "x" in par['axis']:
                        data_current[current_x] = x

                    if "y" in par['axis']:
                        data_current[current_y] = y

                    if "z" in par['axis']:
                        data_current[current_z] = z

                    '''Creation of the input dataset for analysis
                    '''
                    data = pd.concat([data, data_current], axis = 1)

            except TypeError:
                '''Failure to extract from the device
                '''
                d.append(0)
                cont.append(1)
                details.append(str(device))

        if not length:
            '''No data available for all devices.
            '''
            code = -3
        else:
            minumum_length = min(length)
            data = data[0:minumum_length]

            s = sum(d)

            if s < 2:
                success = "False"
                code = -2
                '''No data available for the FDD application. Not enough.
                '''
            if s >= 2:
                success = "True"
                if "filtering" in par:
                    filtering = par["filtering"]
                    if filtering == "lowpass":
                        fmin, fmax, order = par["fmin"],None, par["order"]
                    else:
                        fmin, fmax, order = par["fmin"],par["fmax"], par["order"]
                else:
                    filtering = None

                a = Data(data, freq,len(par['device_id']), 2, fmin, fmax, order, rotation = None, filtering = filtering, plot_singularValues = None)
                result['S'] = a.S.tolist()
                result['U'] = a.U.tolist()
                result['f'] = a.f.tolist()
                result['Frq'] = a.Frq.tolist()
                result['peaks'] = a.peaks.tolist()

                if cont != []:
                    '''IDs in details do not respond.
                    '''
                    code = -1
                else:
                    '''Data available for the FDD application.
                    '''
                    code = 0
            '''return acceleration data'''
            if "acceleration" in par:
                data = np.round(data,4)
                result['acc'] = data.to_dict(orient='list')

    out_dict = fdd_out_dict(success, code, result, msg, details)

    return json.dumps(out_dict)

@app.route('/integration_ids', methods=['GET','POST'])

def integrate2():
    '''integration of a data chunk
    '''
    par = request.get_json()
    '''parameters validation'''
    result,msg = {},{}
    try:
        schema = displacemt_ids_schema
        # And validate the result
        validate(instance=par, schema=schema)
        code = 0
        success = 'True'

    except jsonschema.exceptions.ValidationError:
        msg = sys.exc_info()[1]
        "well-formed but invalid JSON:"
        success = 'False'
        code, msg = -4, msg.message

    except json.decoder.JSONDecodeError:
        msg = sys.exc_info()[1]
        "poorly-formed text, not JSON:"
        success = 'False'
        code, message = -5, msg.message

    if code == 0:
        try:
            result_x, result_y, result_z, freq, r = getDataByKey(par['ids'])

            result = displacement2(par['ids'],par['filtering'],par["fmin"],par["fmax"],par["order"])

            code = 0
        except:
            success = 'False'
            code = -1
            msg = "error in getDataByKey"


    out_dict = integrate_out_dict2(success, code, result, msg)

    return json.dumps(out_dict)

@app.route('/displacement_device', methods=['GET','POST'])

def integrate():
    '''integration data by device
    '''
    par = request.get_json()
    '''parameters validation'''
    result,msg = {},{}
    try:
        schema = displacemt_device_schema
        # And validate the result
        validate(instance=par, schema=schema)
        code = 0
        success = 'True'

    except jsonschema.exceptions.ValidationError:
        msg = sys.exc_info()[1]
        "well-formed but invalid JSON:"
        success = 'False'
        code, msg = -4, msg.message

    except json.decoder.JSONDecodeError:
        msg = sys.exc_info()[1]
        "poorly-formed text, not JSON:"
        success = 'False'
        code, msg = -5, msg.message

    if code == 0:
        try:
            '''Extraction of accelerometric data from device
            '''
            x, y, z, freq = GetTimedSamplesByKey(par["device_id"], par['time_min'], par['time_max'])

            vel_x, shift_x= np.round(displacement(x, freq, par["timestep"]),4)
            vel_y, shift_y = np.round(displacement(y, freq, par["timestep"]),4)
            vel_z, shift_z = np.round(displacement(z, freq, par["timestep"]),4)

            x, y, z= np.round(np.array(x),4),np.round(np.array(y),4),np.round(np.array(z),4)

            velocity,acceleration,shift = {},{},{}

            velocity['x'], velocity['y'], velocity['z'] = vel_x.tolist(),vel_y.tolist(),vel_z.tolist()
            shift['x'],shift['y'],shift['z'] = shift_x.tolist(),shift_y.tolist(),shift_z.tolist()
            acceleration['x'], acceleration['y'], acceleration['z'] = x.tolist(),y.tolist(),z.tolist()
            result['velocity'], result['displacement'], result['acceleration'] = velocity, shift, acceleration

            '''Application completed
            '''
            success = "True"

            code = 0
        except:
            success = 'False'
            code = -1
            msg = "error in GetTimedSamplesByKey"


    out_dict = integrate_out_dict1(success, code, result, msg)

    return json.dumps(out_dict)

@app.route('/PSD', methods=['GET','POST'])

def powerSpectrDens():
    '''parameters validation'''
    result,msg = {},{}
    par = request.get_json()
    try:
        schema = psd_schema
        # And validate the result
        validate(instance=par, schema=psd_schema)
        code = 0
        success = 'True'

    except jsonschema.exceptions.ValidationError:
        msg = sys.exc_info()[1]
        "well-formed but invalid JSON:"
        success = 'False'
        code, msg = -4, msg.message

    except json.decoder.JSONDecodeError:
        msg = sys.exc_info()[1]
        "poorly-formed text, not JSON:"
        success = 'False'
        code, message = -5, msg.message

    if code == 0:
        try:
            '''Extraction of accelerometric data from device
            '''
            x, y, z, freq = GetTimedSamplesByKey(par['device_id'], par['time_min'], par['time_max'])
            acceleration = {}
            acceleration['x'], acceleration['y'], acceleration['z'] = (np.around(x,4)).tolist(), (np.around(y,4)).tolist(), (np.around(z,4)).tolist()

            f, Pxx_spec = sc.signal.welch(x, fs=freq, window='hanning', nperseg=1024, noverlap=None,
                                   nfft=None, detrend='constant', return_onesided=True,
                                   scaling='density', axis=-1)

            _, Pyy_spec = sc.signal.welch(y, fs=freq, window='hanning', nperseg=1024, noverlap=None,
                                   nfft=None, detrend='constant', return_onesided=True,
                                   scaling='density', axis=-1)

            _, Pzz_spec = sc.signal.welch(z, fs=freq, window='hanning', nperseg=1024, noverlap=None,
                                  nfft=None, detrend='constant', return_onesided=True,
                                  scaling='density', axis=-1)

            result['freq'] =(np.round(f,8)).tolist()
            result['psd_x'] = (np.round(Pxx_spec,8)).tolist()
            result['psd_y'] =(np.round(Pyy_spec,8)).tolist()
            result['psd_z'] =(np.round(Pzz_spec,8)).tolist()
            result['acceleration'] = acceleration

            '''"PSD computed"
            '''
            success = True
            code = 0

        except:
            '''Extraction error from device id.
            '''
            success = "False"
            code = -1
            msg = "Extraction error"
    out_dict = psd_out_dict(success, code, result, msg)

    return json.dumps(out_dict)


if __name__ == '__main__':

    print (os.getenv('CAPI'))
    app.run(debug=True, host='0.0.0.0', port=5000)


# export CAPI=https://www.quake.cloud
