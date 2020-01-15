#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 10:22:25 2019
@author: federica
"""
from scipy import signal
import pandas as pd
import numpy as np
from scipy.signal import butter, lfilter
from pyquaternion import Quaternion
import matplotlib.pyplot as plt
from scipy import integrate
from filter_func import *

#rotation = np.matlib.repmat(random.randint(0, 1), n_sensors, 3) #azimuth,pitch,roll for each n.channel
#filtering = ('lowpass',5, 5)
# filtering = ('bandpass', [5,8], 5)
#n_coordinates = 2
#n_sensor = 6
#data = pd.read_csv('/home/federica/Script/colonna_terremoto.csv', delimiter = ',')
#l'estrazione del dataframe è a monte
class Data:

    '''
    Parameters
    ----------
    data: DataFrame, Size = (n_samples, n_sensors*n_coordinates)
    Time history data.

    fs: float
    Sampling frequency.

    n_sensors: int
    Number of sensors.

    n_coordinates: int
    Number of spatial coordinates. Example: 2 stands for x,y
                                            3 stands for x,y,z

    rotation: float64 if sensor rotation is required, Size = (n_sensors, 3)
              otherwise 'None'
    Azimuth, pitch, roll for n_sensors.

    filtering: tuple, Size = 3 if filtering is required
               otherwise 'None'
    Filter parameters. Example: filtering('lowpass', cutoff, order)
                                filtering = ('lowpass', 20, 5)

                                filtering('bandpass', [lowcut, highcut], order)
                                filtering = ('bandpass', [0.5,20], 5)

    plot_singularValues: 'True' if the results plot is required
                         otherwise 'False'

    Attributes
    ----------
    channel: float64, Size = (nsamples, n_sensors*n_coordinates)
    Time history data at the end of the elaboration (rotation and filtering)

    S: float64, Size = (channel.shape[1], Pxy)
    Matrix of the Singular values.

    U: float64, Size = (channel.shape[1], channel.shape[1], PXY.shape[2])
    Matrix of the Modal shapes

    f: float64, Size = (Pxy,)
    Array of sample frequencies.

    Frq: float64, Size = (peaks,)
    Estimated frequencies (Hz) of the modal analysis.

    peaks: float64
    Peaks position in samples.

    fs, n_sensors

    Methods
    -------
    __init__

    butter_lowpass

    butter_bandpass

    butter_lowpass_filter

    butter_bandpass_filter

    '''

    def FDD_analysis(self, filtering = None, psd_window = 1024):
            '''
            Compute the FDD analysis.

            Parameters
            ----------
            psd_window: float
            Length of each segment of the estimated
            cross power spectral density, Pxy,
            using Welch’s method.
            if window is str or tuple, is set to 256, and if window is array_like,
            is set to the length of the window.

            Returns
            -------
            S, U, f, Frq, peaks

            '''

            ''' Compute Power Spectral Density (PSD) matrix.'''
            k = int(psd_window/2+1)
            PXY = np.zeros((self.channel.shape[1],self.channel.shape[1],k))
            for ii in range(self.channel.shape[1]):
                for jj in range(self.channel.shape[1]):
                    f, Pxy = signal.csd(self.channel[:,ii], self.channel[:,jj], self.fs, window='hann', nperseg = 1000, noverlap=900, nfft=psd_window,
                    detrend='constant', return_onesided=True, scaling='density', axis=-1)
                    PXY[ii,jj,:] = Pxy

            '''Compute SVD of the PSD at each frequency'''
            U = np.zeros((self.channel.shape[1],self.channel.shape[1],PXY.shape[2]))
            S = np.zeros((self.channel.shape[1],PXY.shape[2]))

            for ii in range(PXY.shape[2]):
                matrix = PXY[:,:,ii]
                u, s, _ = np.linalg.svd(matrix, full_matrices=True)
                U[:,:,ii] = u #mode shapes
                # S[:,ii] = s
                S[:,ii] = [float(np.format_float_scientific(num, unique=False, precision=4)) for num in s]

            SN = S[0,:]/np.max(S[0,:])
            '''Peak selection'''
            peaks, _ = signal.find_peaks(SN, height=0.01, threshold=0.001, distance=10)
            Frq = ((peaks/(PXY.shape[2]))*(self.fs/2))
            return S, U, f, Frq, peaks

    def __init__(self, data, fs, n_sensors, n_coordinates, fmin, fmax, order, rotation = None,
                 filtering = None, plot_singularValues = None):
        self.fs = fs
        self.n_sensors = n_sensors

        channel = np.zeros((len(data),len(data.keys())))
        for k in range(channel.shape[1]):
            channel[:,k] = data[data.keys()[k]]

        z = np.zeros(len(channel))

        if rotation != None:
            '''rotate channels'''
            for k in range(n_sensors): #sceglie sensore
                q1 = Quaternion(axis=[1, 0, 0], angle=rotation[k,:][0])
                q2 = Quaternion(axis=[0, 1, 0], angle=rotation[k,:][1])
                q3 = Quaternion(axis=[0, 0, 1], angle=rotation[k,:][2])
                Q = q1*q2*q3#definisce il quaternione

                for n in range(channel.shape[0]):#per ogni coppia x,y,z
                    v = [channel[:,k][n], channel[:,k+1][n], z[n]] #definisce il vettore da ruotare
                    v_prime = Q.rotate(v)#calcola il vettore ruotato
                    #riassegna le variabili
                    channel[:,k][n] = v_prime[0]
                    channel[:,k+1][n] = v_prime[1]
                    channel[:,k+2][n] = v_prime[2]
                k = k+n_coordinates

        if filtering != None:
           '''filter channels'''
           if filtering == 'lowpass':

              #define lowpass filt (butterworth):
              cutoff = fmin # desired cutoff frequency of the filter, Hz
              order = order  # desired the order of the filter
              #Get the filter coefficients so we can check its frequency response.
              b, a = butter_lowpass(cutoff, fs, order)
              #apply filter to row data
              for k in range(channel.shape[1]):
                  channel[:,k] = butter_lowpass_filter(channel[:,k], cutoff, fs, order)

           if filtering == 'bandpass':
              #define bandpass filt(butterworth):
              lowcut = fmin #desired the low cutoff frequency of the filter, Hz
              highcut = fmax#desired the high cutoff frequency of the filter, Hz
              if highcut >= fs/2:
                  highcut = (fs/2)-1
              else:
                  highcut
              order = order# desired the order of the filter
              #Get the filter coefficients so we can check its frequency response.
              b, a = butter_bandpass(lowcut, highcut, fs, order)

              #apply filter to row data
              for k in range(channel.shape[1]):
                  channel[:,k] = butter_bandpass_filter(channel[:,k], lowcut, highcut, fs, order)

        self.channel = channel

        S, U, f, Frq, peaks = self.FDD_analysis()

        self.S = S
        self.U = np.round(U,4)
        self.f = np.round(f,4)
        self.Frq = np.round(Frq,4)
        self.peaks = peaks

        if plot_singularValues == True:
           '''Plot first singular values of the PSD matrix'''
           for ii in range(self.channel.shape[1]):
               plt.plot(self.f,self.S[ii,:])
           plt.plot(self.f[self.peaks], self.S[0,:][self.peaks], "x")
           plt.xlabel('frequency[Hz]')
           plt.ylabel('Singular values of the PSD matrix')
           plt.show()

#a = Data(data, 62, 6, 2, rotation = None, filtering = None, plot_singularValues = True)
##print(a.f)
