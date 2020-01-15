import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt


with open('/home/federica/Script/Seismic_extraction/streams_dataframe/streams.json') as json_file:
    data = json.load(json_file)

with open('/home/federica/Script/Seismic_extraction/noise_dataframe/noise_dataframe.json') as json_file:
    data1 = json.load(json_file)

data = pd.DataFrame.from_dict(data)
data = data[data['peak'] <= 1]
data.index = range(len(data))

data1=pd.DataFrame.from_dict(data1)
data1.index = range(len(data1))


plt.plot(data['peak'])
max = data['peak'].max()
max

max1 = data1['peak'].max()
max1

data1= data1[:len(data)]

df = pd.DataFrame(columns = ['norm','tag'],index = data.index)
df1 = pd.DataFrame(columns = ['norm','tag'],index = data1.index)

df['tag'] = np.ones((len(data),), dtype=int)
df1['tag']= np.zeros((len(data),), dtype=int)


fact = 0.101972*1000 #from m s^-2 to mG
fact = int(fact)

for ii in range(len(data)):
    values = data['streams'][ii]
    values =[x/max for x in values]
    df['norm'][ii]=values

for ii in range(len(data1)):
    values = data1['streams'][ii]
    values =[x/max for x in values]
    df1['norm'][ii]=values

####output######
outdict = df.append(df1, ignore_index=True)
len(outdict)
outdict

js = json.dumps(outdict.to_dict())
f = open("/home/federica/Script/Seismic_extraction/dataframe.json","w")
f.write(js)
f.close()


dict = outdict[10:20]
dict.index = range(10)
fig, axs = plt.subplots(10,figsize=(10,10))
fig.suptitle('streams')

for ii in range(10):
    axs[ii].plot(dict['norm'][ii],label=str(ii))
    # axs[ii].set_ylim(-0.5, 0.5)
    plt.legend()

kk = 0
e = outdict['norm'][kk]
N = len(e)
N
t0=0
dt=1/20
dt
time = np.arange(0, N) * dt + t0
time
signal = e

cmap = 'cmor'
scales = np.arange(1, 500)#frequency resolution
[coefficients, frequencies] = pywt.cwt(signal, scales, 'cmor', dt)
frequencies
coefficients

im = plt.imshow(np.absolute(coefficients),aspect='auto')
ax = plt.gca()
yticks = frequencies

ax.set_yticklabels(2*frequencies)
plt.colorbar()
