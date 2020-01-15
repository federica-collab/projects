#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 10:53:17 2019

@author: federica
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import wasserstein_distance
import statistics
import entropy
import numpy as np
from scipy import signal
from scipy.signal import periodogram, welch, resample
from scipy import stats
from scipy.signal import decimate
import json
import pywt
import matplotlib.pyplot as plt
from scipy.fftpack import fft

def spectral_entropy(x, sf, method='fft', nperseg=None, normalize=False):
    """Spectral Entropy.

    Parameters
    ----------
    x : list or np.array
        One-dimensional time series of shape (n_times)
    sf : float
        Sampling frequency, in Hz.
    method : str
        Spectral estimation method:

        * ``'fft'`` : Fourier Transform (:py:func:`scipy.signal.periodogram`)
        * ``'welch'`` : Welch periodogram (:py:func:`scipy.signal.welch`)
    nperseg : int or None
        Length of each FFT segment for Welch method.
        If None (default), uses scipy default of 256 samples.
    normalize : bool
        If True, divide by log2(psd.size) to normalize the spectral entropy
        between 0 and 1. Otherwise, return the spectral entropy in bit.

    Returns
    -------
    se : float
        Spectral Entropy

    Notes
    -----
    Spectral Entropy is defined to be the Shannon entropy of the power
    spectral density (PSD) of the data:

    .. math:: H(x, sf) =  -\\sum_{f=0}^{f_s/2} P(f) log_2[P(f)]

    Where :math:`P` is the normalised PSD, and :math:`f_s` is the sampling
    frequency.

    References
    ----------
    Inouye, T. et al. (1991). Quantification of EEG irregularity by
    use of the entropy of the power spectrum. Electroencephalography
    and clinical neurophysiology, 79(3), 204-210.

    https://en.wikipedia.org/wiki/Spectral_density

    https://en.wikipedia.org/wiki/Welch%27s_method

    Examples
    --------
    Spectral entropy of a pure sine using FFT

    >>> from entropy import spectral_entropy
    >>> import numpy as np
    >>> sf, f, dur = 100, 1, 4
    >>> N = sf * dur # Total number of discrete samples
    >>> t = np.arange(N) / sf # Time vector
    >>> x = np.sin(2 * np.pi * f * t)
    >>> np.round(spectral_entropy(x, sf, method='fft'), 2)
    0.0

    Spectral entropy of a random signal using Welch's method

    >>> from entropy import spectral_entropy
    >>> import numpy as np
    >>> np.random.seed(42)
    >>> x = np.random.rand(3000)
    >>> spectral_entropy(x, sf=100, method='welch')
    6.980045662371389

    Normalized spectral entropy

    >>> spectral_entropy(x, sf=100, method='welch', normalize=True)
    0.9955526198316071
    """
    x = np.array(x)
    # Compute and normalize power spectrum
    if method == 'fft':
        _, psd = periodogram(x, sf)
    elif method == 'welch':
        _, psd = welch(x, sf, nperseg=nperseg)
    psd_norm = np.divide(psd, psd.sum())
    se = -np.multiply(psd_norm, np.log2(psd_norm)).sum()
    if normalize:
        se /= np.log2(psd_norm.size)

    return se

########OPERATIONS ON DATAFRAME#########################
ii = 0
n = 2766

columns = ["streams","corr", "peak", "mean", "std","frq","distance(km)","entropy"]
Data= pd.DataFrame(index = range(ii,n,1), columns= columns)

fact = 0.101972*1000 #from m s^-2 to mG
fact = int(fact)

for ii in range(ii,n,1):
    try:
        with open('/home/federica/Script/Seismic_extraction/Store/dict'+str(ii)+'.json') as json_file:
            data = json.load(json_file)

            data[str(ii)]['E'][0] = resample(data[str(ii)]['E'][0],20*60*5)
            data[str(ii)]['E'][0] = [float(np.format_float_scientific(c, unique=False, precision=2)) for c in data[str(ii)]['E'][0]]
            '''data'''
            Data['streams'][ii] = data[str(ii)]['E'][0]

            '''autocorr zero lag'''
            E = pd.Series(data[str(ii)]['E'][0])
            # N = pd.Series(data[str(ii)]['N'][0])
            # Z = pd.Series(data[str(ii)]['Z'][0])

            Data['corr'][ii] = float(np.format_float_scientific(E.autocorr(), unique=False, precision=4))
            # float(np.format_float_scientific(N.autocorr(), unique=False, precision=4)),
            # float(np.format_float_scientific(Z.autocorr(), unique=False, precision=4))]

            '''peak'''
            Data['peak'][ii]= float(np.format_float_scientific(max(data[str(ii)]['E'][0]), unique=False, precision=4))
            # float(np.format_float_scientific(max(data[str(ii)]['N'][0]), unique=False, precision=4)),
            # float(np.format_float_scientific(max(data[str(ii)]['Z'][0]), unique=False, precision=4))]

            # '''meanpeak'''
            # Data['meanpeak'][ii] = np.mean(Data['peak'][ii])

            '''mean'''
            Data['mean'][ii]= float(np.format_float_scientific(statistics.mean(data[str(ii)]['E'][0]), unique=False, precision=4))
            # float(np.format_float_scientific(statistics.mean(data[str(ii)]['N'][0]), unique=False, precision=4)),
            # float(np.format_float_scientific(statistics.mean(data[str(ii)]['Z'][0]), unique=False, precision=4))]

            '''standard deviation'''
            Data['std'][ii] = float(np.format_float_scientific(statistics.stdev(data[str(ii)]['E'][0]), unique=False, precision=4))
            # float(np.format_float_scientific(statistics.stdev(data[str(ii)]['N'][0]), unique=False, precision=4)),
            # float(np.format_float_scientific(statistics.stdev(data[str(ii)]['Z'][0]), unique=False, precision=4))]
            Data['frq'][ii] = 20

            '''distance(km)'''
            Data['distance(km)'][ii] = data[str(ii)]['distance from source (km)']

            '''entropy'''
            entropy = spectral_entropy(data[str(ii)]['E'][0], data[str(ii)]['E'][4], method='fft', nperseg=None, normalize=False)
            # y = spectral_entropy(data[str(ii)]['N'][0], data[str(ii)]['N'][4], method='fft', nperseg=None, normalize=False)
            # z= spectral_entropy(data[str(ii)]['Z'][0], data[str(ii)]['Z'][4], method='fft', nperseg=None, normalize=False)
            Data['entropy'][ii] = entropy

    except:
            a = 1

Data = Data.dropna()

Data = Data[Data['distance(km)'] <= 500]

Data = Data[Data['peak']>=0.01]

Data

js = json.dumps(Data.to_dict())
f = open("/home/federica/Script/Seismic_extraction/streams_dataframe/streams.json","w")
f.write(js)
f.close()
############################################################################################
ii = 0
n = 2766

columns = ["streams","corr", "peak", "mean", "std","frq","distance(km)","entropy"]
Data= pd.DataFrame(index = range(ii,n,1), columns= columns)

fact = 0.101972*1000 #from m s^-2 to mG
fact = int(fact)

for ii in range(ii,n,1):
    try:
        with open('/home/federica/Script/Seismic_extraction/Store_noise/noisedict'+str(ii)+'.json') as json_file:
            data = json.load(json_file)

            data[str(ii)]['E'][0] = resample(data[str(ii)]['E'][0],20*60*5)
            data[str(ii)]['E'][0] = [float(np.format_float_scientific(c, unique=False, precision=2)) for c in data[str(ii)]['E'][0]]
            '''data'''
            Data['streams'][ii] = data[str(ii)]['E'][0]

            '''autocorr zero lag'''
            E = pd.Series(data[str(ii)]['E'][0])
            # N = pd.Series(data[str(ii)]['N'][0])
            # Z = pd.Series(data[str(ii)]['Z'][0])

            Data['corr'][ii] = float(np.format_float_scientific(E.autocorr(), unique=False, precision=4))
            # float(np.format_float_scientific(N.autocorr(), unique=False, precision=4)),
            # float(np.format_float_scientific(Z.autocorr(), unique=False, precision=4))]

            '''peak'''
            Data['peak'][ii]= float(np.format_float_scientific(max(data[str(ii)]['E'][0]), unique=False, precision=4))
            # float(np.format_float_scientific(max(data[str(ii)]['N'][0]), unique=False, precision=4)),
            # float(np.format_float_scientific(max(data[str(ii)]['Z'][0]), unique=False, precision=4))]

            # '''meanpeak'''
            # Data['meanpeak'][ii] = np.mean(Data['peak'][ii])

            '''mean'''
            Data['mean'][ii]= float(np.format_float_scientific(statistics.mean(data[str(ii)]['E'][0]), unique=False, precision=4))
            # float(np.format_float_scientific(statistics.mean(data[str(ii)]['N'][0]), unique=False, precision=4)),
            # float(np.format_float_scientific(statistics.mean(data[str(ii)]['Z'][0]), unique=False, precision=4))]

            '''standard deviation'''
            Data['std'][ii] = float(np.format_float_scientific(statistics.stdev(data[str(ii)]['E'][0]), unique=False, precision=4))
            # float(np.format_float_scientific(statistics.stdev(data[str(ii)]['N'][0]), unique=False, precision=4)),
            # float(np.format_float_scientific(statistics.stdev(data[str(ii)]['Z'][0]), unique=False, precision=4))]
            Data['frq'][ii] = 20

            '''distance(km)'''
            Data['distance(km)'][ii] = data[str(ii)]['distance from source (km)']

            '''entropy'''
            entropy = spectral_entropy(data[str(ii)]['E'][0], data[str(ii)]['E'][4], method='fft', nperseg=None, normalize=False)
            # y = spectral_entropy(data[str(ii)]['N'][0], data[str(ii)]['N'][4], method='fft', nperseg=None, normalize=False)
            # z= spectral_entropy(data[str(ii)]['Z'][0], data[str(ii)]['Z'][4], method='fft', nperseg=None, normalize=False)
            Data['entropy'][ii] = entropy

    except:
            a = 1

Data = Data.dropna()

Data = Data[Data['peak']<=0.01]

Data

js = json.dumps(Data.to_dict())
f = open("/home/federica/Script/Seismic_extraction/noise_dataframe/noise_dataframe.json","w")
f.write(js)
f.close()
