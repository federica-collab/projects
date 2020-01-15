#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 11:24:08 2019

@author: federica
"""
import pandas as pd
import datetime
from datetime import timedelta
from obspy.clients.fdsn.client import Client
import time 
import matplotlib.pyplot as plt 
import json

from Stream_extraction import *

df = pd.read_csv('/home/federica/Script/Seismic_extraction/code/data_for_ML.csv')

class ML_data:
    '''
    Extracts the dataset of seismic and noise traces
    
    Parameters
    ----------
    df: DataFrame, Size:(2776,3), Column names: UTCtime, lat, lon. Dataset of the parameters of the examples to be downloaded
    
    Attributes
    ----------
    df
    
    Methods
    -------
    get()
    
    '''
    def __init__(self, df):
        
        self.df = df
    
    def get(self, mins, num):
        '''
        Parameters
        ----------
        mins: int, Size:1, length traces in mins
        
        num: int, Size:1, Number of samples to be extracted for the neural network
        
        Return
        ------
        DATA: dict, Size: num. Dataset of seismic traces
        
        DATA_Noise: dict, Size: num. Seismic noise data set
        '''
        DATA, DATA_Noise = {},{}
        for ii in range(num):
            '''extract seismic data.
            '''
            starttime = datetime.datetime.strptime(df['UTCtime'][ii],'%Y-%m-%dT%H:%M:%S') - timedelta(minutes=1)
        
            nextdate = datetime.datetime.strptime(df['UTCtime'][ii+1],'%Y-%m-%dT%H:%M:%S')
        
            halftime = starttime + (nextdate - starttime)/2
            noise_timeend = halftime + timedelta(minutes=mins)
            
            lat = float(df['lat'][ii])
            lon = float(df['lon'][ii])
            
        #    a = stream(SeismicNetworkIV,lat,lon,starttime,endtime, client='INGV')
            Station, st, info_, distance = stream(SeismicNetworkIV,lat,lon, df['UTCtime'][ii], datetime.datetime.strftime(starttime+timedelta(minutes=mins),'%Y-%m-%dT%H:%M:%S'), client='INGV').get()
            
            x = {
                        "E": [st.traces[0].data.tolist(), info_[0].network, info_[0].station, info_[0].channel, info_[0].sampling_rate],
                        "N": [st.traces[1].data.tolist(), info_[1].network, info_[1].station, info_[1].channel, info_[1].sampling_rate],
                        "Z": [st.traces[2].data.tolist(), info_[2].network, info_[2].station, info_[2].channel, info_[2].sampling_rate],
                       "starttime": df['UTCtime'][ii],
                           "endtime": datetime.datetime.strftime(starttime+timedelta(minutes=mins),'%Y-%m-%dT%H:%M:%S'),
                               "lat": lat,
                                   "lon": lon,
                                       "distance from source (km)": distance}
            DATA[ii] = x
            
            if nextdate - starttime >timedelta(minutes=30):
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
            time.sleep(30)
            print(ii)
        return DATA, DATA_Noise
    
DATA, DATA_Noise = ML_data(df).get(5,10)



hh, ll = 200,205

for k in range(37,100,1):
    df1 = df[hh:ll]
    df1.index = range(5)
    DATA, DATA_Noise = ML_data(df1).get(1,1)
      
    js = json.dumps(DATA)
    f = open("/home/federica/Script/Seismic_extraction/Store/dict"+str(k)+".json","w")
    f.write(js)
    f.close()
    
    json2 = json.dumps(DATA_Noise)
    f2 = open("/home/federica/Script/Seismic_extraction/Store_noise/noisedict"+str(k)+".json","w")
    f2.write(json2)
    f2.close()   
    
    print('-------------')
    print('saved'+str(k))
    print('-------------')    
    hh=ll
    ll=hh+5







#    
#fig, axs = plt.subplots(DATA.keys(), 1, figsize=(10, 50))
#
#for i in DATA.keys():
#    axs[i].plot(DATA[i]["N"][0], label = 'ex.'+str(i))
#    axs[i].legend()
#
#with open('data_for_ML.json', 'w') as outfile:
#    json.dump(DATA, outfile)
#    
#with open('data_for_ML.json') as json_file:
#    data = json.load(json_file)