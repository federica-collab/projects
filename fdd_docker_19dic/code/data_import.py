#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 10:40:35 2019
@author: federica
"""

import requests
import os

def GetTimedSamplesByKey(deviceId, sampleTimeMin, sampleTimeMax, maxResultCount = 1000, filterLevel = 0, headers = ""):
        input_parameters = {}
        input_parameters['deviceId'], input_parameters['sampleTimeMin'], input_parameters['sampleTimeMax'] = deviceId,sampleTimeMin,sampleTimeMax


        url = "[server]/api/services/app/deviceData/GetTimedSamplesByKey"
        key = "L5kDSHwxPavISqxmPQ98DWt1HejSn7XKWPfwmiwc"
        data = {"key": key, "deviceId": deviceId, "filterLevel": filterLevel, "sampleTimeMin": sampleTimeMin, "sampleTimeMax": sampleTimeMax, 'maxResultCount': maxResultCount}

        r = requests.post(json=data, url=url.replace('[server]', os.getenv('CAPI')), headers=headers).json()

        return r['result']['data']['x'], r['result']['data']['y'], r['result']['data']['z'], r['result']['data']['frequency']

#x, y, z, freq = GetTimedSamplesByKey(par['deviceId'], par['timeMin'], par['timeMax'])
