#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 16:02:16 2019
@author: federica
"""
from scipy import signal

def butter_lowpass(cutoff, fs, order):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype ='low')
        return b, a

def butter_bandpass(lowcut, highcut, fs, order):
        nyq = 0.5*fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = signal.butter(order, [low, high], btype = 'band')
        return b, a

def butter_lowpass_filter(data, cutoff, fs, order):
        b, a = butter_lowpass(cutoff, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y
