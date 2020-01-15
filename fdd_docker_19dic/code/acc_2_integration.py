#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 14:31:22 2019
@author: federica
"""

import numpy as np
import scipy as sc
from filter_func import *
from data_by_id import *


def displacement2(ids, filtering, fmin, fmax, order):
    '''
    Parameters
    ----------
    ids: int, Size: 1. deviceID
    Example: ids = 2000000

    filtering: batterworth filter. filtering = ["bandpass",[f1,f2],order]. If filtering = None, no data filtering.
    Example: filtering = ["bandpass",[5,10],4]

    Returns
    -------
    data: dict, Size:3. data reports velocity, displacement and metrics. + acceleration
    '''
    try:

        result_x, result_y,result_z, fs, API_info = getDataByKey(ids)
    except:
        result_x = []

        data, error = {},{}

        data['success'] = 'False'
        error['code'] = -1
        error['message'] = 'error in getDataByKey'
        data['error'] = error

    else:
        try:
            result_x !=[]
            if filtering != []:

                   if filtering == 'lowpass':
                      #define lowpass filt (butterworth):
                      cutoff = fmin # desired cutoff frequency of the filter, Hz
                      order = order  # desired the order of the filter
                      #Get the filter coefficients so we can check its frequency response.
                      b, a = butter_lowpass(cutoff, fs, order)
                      #apply filter to row data
                      result_x = butter_lowpass_filter(result_x, cutoff, fs, order)
                      result_y = butter_lowpass_filter(result_y, cutoff, fs, order)
                      result_z = butter_lowpass_filter(result_z, cutoff, fs, order)

                   if filtering == 'bandpass':

                      #define bandpass filt(butterworth):
                      lowcut = fmin #desired the low cutoff frequency of the filter, Hz
                      highcut = fmax#desired the high cutoff frequency of the filter, Hz
                      if highcut >=fs/2:
                          highcut = (fs/2)-0.005
                      order = order# desired the order of the filter
                      #Get the filter coefficients so we can check its frequency response.
                      b, a = butter_bandpass(lowcut, highcut, fs, order)

                      #apply filter to row data
                      result_x = butter_bandpass_filter(result_x, lowcut, highcut, fs, order)
                      result_y = butter_bandpass_filter(result_y, lowcut, highcut, fs, order)
                      result_z = butter_bandpass_filter(result_z, lowcut, highcut, fs, order)

            nsamples = len(result_x)
            dt = 1/fs
            tax = np.linspace(0, dt*nsamples, num=nsamples)

            shift_x, shift_y, shift_z = np.array([]),np.array([]),np.array([])
            '''speed calculation
            '''
            velx, vely, velz = np.array([]),np.array([]),np.array([])
            velx = [(a)*9.80665 for a in np.array(signal.detrend(sc.integrate.cumtrapz(result_x,tax, initial=0)))]
            vely = [(a)*9.80665 for a in np.array(signal.detrend(sc.integrate.cumtrapz(result_y,tax, initial=0)))]
            velz = [(a)*9.80665 for a in np.array(signal.detrend(sc.integrate.cumtrapz(result_z,tax, initial=0)))]
            '''displacement calculation
            '''
            shift_x = np.array(signal.detrend(sc.integrate.cumtrapz(velx,tax, initial=0)))
            shift_y = np.array(signal.detrend(sc.integrate.cumtrapz(vely,tax, initial=0)))
            shift_z = np.array(signal.detrend(sc.integrate.cumtrapz(velz,tax, initial=0)))

            '''metrics: max velocity and displacement'''
            max_vel, max_shift = {},{}
            velx_max, vely_max, velz_max = max(velx), max(vely), max(velz)
            sh_x_max, sh_y_max, sh_z_max = max(shift_x),max(shift_y),max(shift_z)

            max_vel['x'], max_vel['y'], max_vel['z']  = velx_max.tolist(), vely_max.tolist(), velz_max.tolist()
            max_shift['x'], max_shift['y'], max_shift['z'] = sh_x_max.tolist(), sh_y_max.tolist(), sh_z_max.tolist()

            '''Rounding of data to output
            '''
            result_x, result_y, result_z = np.round(result_x,4), np.round(result_y,4), np.round(result_z,4)
            velx, vely, velz = np.round(velx,4), np.round(vely,4), np.round(velz,4)
            shift_x, shift_y, shift_z = np.round(shift_x,4), np.round(shift_y,4), np.round(shift_z,4)
            '''dict in output
            '''
            velocity, shift, acceleration, metric = {}, {}, {}, {}
            shift['x'], shift['y'], shift['z'] = shift_x.tolist(), shift_y.tolist(), shift_z.tolist()
            velocity['x'], velocity['y'], velocity['z']  = velx.tolist(), vely.tolist(), velz.tolist()
            acceleration['x'],acceleration['y'],acceleration['z'] = result_x.tolist(),result_y.tolist(),result_z.tolist()
            metric['max_velocity'], metric['max_displacement'] = max_vel, max_shift

            result= {}

            result['velocity'], result['displacement'], result['metrics'], result['API_info'] = velocity, shift, metric, API_info
            result['acceleration'] = acceleration

        except:
            result
        return result
