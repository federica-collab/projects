#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 10:41:44 2019
@author: federica
"""

from scipy import signal, integrate
import numpy as np
import scipy as sc

def displacement(data, fs, timestep): #data = np.array
    '''
    Parameters
    ----------
    data: float64, size: (samples,)
    Array of acceleration(mG).
    fs: sampling frequency
    timestep: int, size:1
    Step in minutes
    Returns
    -------
    vel: float64, size: (len(data),)
    Array of velocity(mms-1).
    shift: float64, size: (len(data),)
    Array of displacements(mm).
    + acceleration (mG)
    Example: vel, shift = displacement(data, 62, 1)
    '''
    nsamples = len(data)
    dt = 1/fs
    tax = np.linspace(0, dt*nsamples, num=nsamples)
    data = [a*9.8065 for a in data]#from mG to mms-2

    vel,shift =np.array([]),np.array([])

    k1=0
    k2 = int(k1+len(data)/(60/timestep))
    for ii in range(int(60/timestep)):
        c = np.array(signal.detrend(sc.integrate.cumtrapz(data[k1:k2],tax[k1:k2], initial=0)))
        vel = np.concatenate((vel,c))

        s = np.array(signal.detrend(sc.integrate.cumtrapz(c,tax[k1:k2], initial=0)))
        shift = np.concatenate((shift,s))

        k1 = k2
        k2 = int(k1+len(data)/60)

    return vel, shift
