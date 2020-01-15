#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 09:34:49 2019

@author: federica
"""
import pandas as pd
import requests
import xmltodict
import datetime
from obspy.clients.fdsn.client import Client
import numpy as np
import math
from Seismic_Network_IV_extraction import *

SeismicNetworkIV,_,_ = seismic_network_IV(URL).get()

# starttime = "2019-09-01T00:01:00" #our starttime in str
# endtime ="2019-09-01T00:04:00"
# lat = 42.5327 #our
# lon = 12.3853 #our
client=Client("INGV")

class stream:
    '''
    Extracts the requested acceleration data from the INGV National Seismic Network.

    Parameters
    ----------
    lat: float, Size:1. Example: 42.5327

    long: float, Size:1. Example: 12.3853

    starttime: str, Size:1. Example: "2019-09-01T00:01:00"

    endtime: str, Size:1. Example: "2019-09-01T00:03:00"

    SeismicNetworkIV: DataFrame, size(562,7). Value: Column names:
        code, name, start_date, end_date, lat, lon, url

    Attributes
    ----------
    starttime

    endtime

    client: example, 'INGV'

    lat

    lon

    Methods
    -------
    __init__

    get()

    Network_list()

    Extraction()

    get_distance()


    '''

    def __init__(self, SeismicNetworkIV, lat, lon, starttime, endtime, client='INGV'):

        self.starttime = starttime
        self.endtime = endtime
        self.client = client
        self.lat = lat
        self.lon = lon

    def get(self):
        '''
        select the nearest available station,
        select the available channels,
        return the seismic stream object and calculate the distance
        between our coordinates and those of the station

        '''

        Network = self.Network_list()

        Network.replace(to_replace=[None], value='v', inplace=True)
        Network.index = np.arange(len(Network))

        stream, Station,info_0, info_1, info_2, ii = self.Extraction(Network)
        info_ = [info_0, info_1, info_2]


        stream.merge(method=1, fill_value=0)
        pre_filt = [0.01, 0.01, 25, 50]
        stream.remove_response( pre_filt=pre_filt, output="acc")
        startaim = max([tr.stats.starttime for tr in (stream)])
        endtaim = min([tr.stats.endtime for tr in (stream)])
        stream.trim(startaim, endtaim, nearest_sample=True)


        Station.index = np.arange(len(Station))

        destination = (float(Network['lat'][ii]), float(Network['lon'][ii]))
        origin = (self.lat,self.lon)

        distance = self.get_distance(origin, destination)
        self.distance = distance
        return Station, stream, info_, distance

    def Network_list(self):
        '''
        Sort the SeismicNetworkIV stations from the nearest to the furthest.

        Returns
        -------
        Network: DataFrame, Size(562,10). Value: Columns names: code, name, start_date, end-date, lat, lon, url,
        available, delta_lat, delta_lon

        '''

        Network = SeismicNetworkIV.copy()

        Network['start_date'] = [datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%S') for x in Network["start_date"]]

        Network['end_date'] = Network.end_date.mask(Network.end_date.isnull(), self.endtime)


        Network['end_date'] = [datetime.datetime.strptime(x,'%Y-%m-%dT%H:%M:%S') for x in Network["end_date"]]
        starttime = datetime.datetime.strptime(self.starttime, '%Y-%m-%dT%H:%M:%S')
        endtime = datetime.datetime.strptime(self.endtime, '%Y-%m-%dT%H:%M:%S')

        timedelta1 = endtime - starttime

        Network["available"] = [x + timedelta1 <= y for x,y in zip(Network['start_date'], Network['end_date'])]
        Network = Network.query('available == True')
        Network["delta_lat"] = [abs(x) for x in [float(x) - self.lat for x in Network['lat']]]
        Network["delta_lon"] = [abs(x) for x in [float(x) - self.lon for x in Network['lon']]]

        Network = Network.sort_values(["delta_lat", "delta_lon"], ascending=[True, True])

        return Network

    def Extraction(self, Network):
        '''
        Returns che nearest available station.

        Parameters
        ---------
        Network: DataFrame, Size(number of channels, 10). Value: Columns names: code, name, start_date, end_date, lat, lon, url, available, delta_lat, delta_lon

        Return
        ------
        st: core.stream.Stream, Size = 1. Value: Stream object of obspy.stream module

        Station: DataFrame, Size(number of channels, 6). Value: Columns names: channels, start_date, end_date, sample_rate, azimuth, kind

        info_: list, Size(3). Info about available channels(N-S, E-W, Z)

        ii: int, Size:1. The station's index in Network data frame

        '''
        for ii in range(len(Network)):

            channel, start_date, end_date, sample_rate, azimuth, kind = [],[],[],[],[],[]
            Station = pd.DataFrame()

            url = Network["url"][ii] #get url

            response = requests.get(url)
            xpars = xmltodict.parse(response.content)

            if isinstance(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"], dict):
                    channel.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"]["@code"])
                    start_date.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"]["@startDate"])
                    sample_rate.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"]["SampleRate"])
                    azimuth.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"]["Azimuth"])
                    kind.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"]["Response"]["InstrumentSensitivity"]["InputUnits"]["Name"])
                    end_date.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"]["@endDate"])
            else:
            #creando i canali se ce ne sono diversi per stazione
                for xx in range(len(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"])):
                    startdate_x = datetime.datetime.strptime(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"][xx]["@startDate"], '%Y-%m-%dT%H:%M:%S')
                    endate_x = datetime.datetime.strptime(self.endtime,'%Y-%m-%dT%H:%M:%S')

                    if '@endDate' in xpars["FDSNStationXML"]["Network"]["Station"]["Channel"][xx]:
                        endate_x = datetime.datetime.strptime(xpars['FDSNStationXML']['Network']['Station']["Channel"][xx]['@endDate'],'%Y-%m-%dT%H:%M:%S')
                    else:
                        endate_x = endate_x

                    delta = (endate_x - startdate_x).days
                    if delta > 0:
                        start_date.append(datetime.datetime.strptime(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"][xx]["@startDate"],'%Y-%m-%dT%H:%M:%S'))
                        end_date.append(endate_x)
                        azimuth.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"][xx]["Azimuth"])
                        channel.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"][xx]["@code"])
                        kind.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"][xx]["Response"]["InstrumentSensitivity"]["InputUnits"]["Name"])
                        sample_rate.append(xpars["FDSNStationXML"]["Network"]["Station"]["Channel"][xx]["SampleRate"])

            Station["channels"] = channel
            Station["start_date"] = start_date
            Station["end_date"] = end_date
            Station["sample_rate"] = sample_rate
            Station["azimuth"] = azimuth
            Station["kind"] = kind

            Station = Station.sort_values(["start_date","end_date","sample_rate"], ascending=[True,True,True])

            print('Station Code:'+Network['code'][ii]+', Station Name:'+Network['name'][ii])

            starttime = datetime.datetime.strptime(self.starttime, '%Y-%m-%dT%H:%M:%S')
            endtime = datetime.datetime.strptime(self.endtime, '%Y-%m-%dT%H:%M:%S')

            yy = 0
            for k in range(int(len(Station["channels"])/3)):
                sensore = Station["channels"][yy][:2]
                try:
                    st = client.get_waveforms('IV', Network["code"][ii],'*',sensore+'*',starttime, endtime, attach_response=True)
                    print('available response, '+'sensor: '+sensore)
                    control = True
                    break
                except Exception as FDSNNoDataException:
                    control = False
                    print(FDSNNoDataException)
                break
            yy += 3
            if control == True:
                info_0 = st.traces[0].stats
                info_1 = st.traces[1].stats
                info_2 = st.traces[2].stats
                break
        return st, Station, info_0, info_1, info_2, ii

    def get_distance(self, origin, destination):
        '''
        Calculate distance between two points using latitude and longitude.

        Parameters
        ----------
        origin: tuple, Size:2. Point A

        destination: tuple, Size:2. Point B

        Return
        ------
        distance: float, Size:1. Calculated distance(in Km) between A and B

        '''
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371 #km

        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = radius * c
        return distance
#
# a = stream(SeismicNetworkIV,lat,lon,starttime,endtime, client='INGV')
# Network = a.Network_list()
# Station, stream, info_, distance = a.get()
# st = stream
