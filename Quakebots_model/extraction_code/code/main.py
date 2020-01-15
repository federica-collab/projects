#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 15:59:29 2019

@author: federica
"""
import pandas as pd
from Seismic_Network_IV_extraction import *
from Stream_extraction import *
import datetime
import json
import time

df = pd.read_csv('/home/federica/Script/Seismic_extraction/code/data_for_ML.csv')

DATA, DATA_Noise = {},{}
mins = 5
for ii in range(0,178,1):
    '''extract seismic data.
    '''
    try:
            
        starttime = datetime.datetime.strptime(df['UTCtime'][ii],'%Y-%m-%dT%H:%M:%S') - datetime.timedelta(minutes=1)
    
        nextdate = datetime.datetime.strptime(df['UTCtime'][ii+1],'%Y-%m-%dT%H:%M:%S')
    
        halftime = starttime + (nextdate - starttime)/2
        noise_timeend = halftime + datetime.timedelta(minutes=mins)
        
        lat = float(df['lat'][ii])
        lon = float(df['lon'][ii])
        
    #    a = stream(SeismicNetworkIV,lat,lon,starttime,endtime, client='INGV')
        Station, st, info_, distance = stream(SeismicNetworkIV,lat,lon, df['UTCtime'][ii], datetime.datetime.strftime(starttime+datetime.timedelta(minutes=mins),'%Y-%m-%dT%H:%M:%S'), client='INGV').get()
        
        x = {
                    "E": [st.traces[0].data.tolist(), info_[0].network, info_[0].station, info_[0].channel, info_[0].sampling_rate],
                    "N": [st.traces[1].data.tolist(), info_[1].network, info_[1].station, info_[1].channel, info_[1].sampling_rate],
                    "Z": [st.traces[2].data.tolist(), info_[2].network, info_[2].station, info_[2].channel, info_[2].sampling_rate],
                   "starttime": df['UTCtime'][ii],
                       "endtime": datetime.datetime.strftime(starttime+datetime.timedelta(minutes=mins),'%Y-%m-%dT%H:%M:%S'),
                           "lat": lat,
                               "lon": lon,
                                   "distance from source (km)": distance}
        DATA[ii] = x
        
        if nextdate - starttime >datetime.timedelta(minutes=30):
            control = True
            print('No seismic sequence')
            print('Take noise')
            Station2, stream2, info_2, distance2 = stream(SeismicNetworkIV,lat,lon, datetime.datetime.strftime(halftime,'%Y-%m-%dT%H:%M:%S'), datetime.datetime.strftime(noise_timeend,'%Y-%m-%dT%H:%M:%S'), client='INGV').get()
    
            xi = {
                    "E": [stream2.traces[0].data.tolist(), info_2[0].network, info_2[0].station, info_2[0].channel, info_2[0].sampling_rate],
                    "N": [stream2.traces[1].data.tolist(), info_2[1].network, info_2[1].station, info_2[1].channel, info_2[1].sampling_rate],
                    "Z": [stream2.traces[2].data.tolist(), info_2[2].network, info_2[2].station, info_2[2].channel, info_2[2].sampling_rate],
                   "starttime": datetime.datetime.strftime(halftime,'%Y-%m-%dT%H:%M:%S'),
                       "endtime": datetime.datetime.strftime(noise_timeend,'%Y-%m-%dT%H:%M:%S'),
                           "lat": lat,
                               "lon": lon,
                                   "distance from source (km)": distance2}
        
        else:
            control = False
            print('I am in Seismic sequence.')
        
        if control == True:
            DATA_Noise[ii]=xi
        else:
            DATA_Noise[ii]= []
        time.sleep(30)
        print(ii)
        
        js = json.dumps(DATA)
        f = open("/home/federica/Script/Seismic_extraction/Store/dict"+str(ii)+".json","w")
        f.write(js)
        f.close()
        
        json2 = json.dumps(DATA_Noise)
        f2 = open("/home/federica/Script/Seismic_extraction/Store_noise/noisedict"+str(ii)+".json","w")
        f2.write(json2)
        f2.close()   
        
        print('-------------')
        print('saved'+str(ii))
        print('-------------')
    except: 
        a = 1
    else: 
        
        DATA = {}
        DATA_Noise = {}

            
