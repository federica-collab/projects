#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 14:32:54 2019
@author: federica
"""
import numpy as np
import os

def getDataByKey(ids):

    import requests

    url_get_data_key = "[server]/api/services/app/deviceData/GetDeviceDatasByKey"
    url_get_samples = "[server]/api/services/app/deviceData/GetSamplesByKey"

    headers = ""
    key = "L5kDSHwxPavISqxmPQ98DWt1HejSn7XKWPfwmiwc"
    deviceDataId = 0
    skipCount = 0
    maxResultCount = 1000
    deviceId = 100
    filterLevel = 0

    output_x = []
    output_y = []
    output_z = []
    #sampletime = []
    data={"key": key, "deviceDataId": ids, "filterLevel": 0}
    r = requests.post(json=data, url=url_get_samples.replace('[server]', os.getenv('CAPI')), headers=headers).json()
    
    result_x = np.array(r['result']['data']['x'])
    result_y = np.array(r['result']['data']['y'])
    result_z = np.array(r['result']['data']['z'])
    freq = r['result']['data']['frequency']
    print(result_x.shape)

    return result_x, result_y, result_z, freq, r
