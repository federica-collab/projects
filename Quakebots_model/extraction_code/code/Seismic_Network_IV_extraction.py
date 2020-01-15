#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:47:36 2019

@author: federica
"""
import requests
import xmltodict
import pandas as pd

URL = "http://webservices.ingv.it/fdsnws/station/1/query?nodata=404&authoritative=any&level=station&net=IV"


class seismic_network_IV:

    '''
       Creates the seismic station dataset of the National Seismic Network,
       consulting FDSN Web Services

        Parameters
        ----------
        URL: "http://webservices.ingv.it/fdsnws/station/1/query?nodata=404&authoritative=any&level=station&net=IV"
        %web address%

        Attributes
        ----------
        list: Type:DataFrame, Size: (564,7), Value: Column names: code, name, start_date, end_date, lat, lon, url
        %List of the seismic stations%

        code: Type: int, Size:1, example: 0
        %Code error%

        message: Type. str, Size: 1, example: Application completed
        %Success or failure message of the application%

        Methods
        -------
        get_list()

    '''

    def __init__(self, URL):

        self.url = URL

    def get(self):
        '''get list of the seismic stations
        '''
        try:
            response = requests.get(self.url)
            code = 0
            message = 'available response from url'
        except:
            code = -1
            message = 'error in request.get'+'('+self.url+')'
            SeismicNetwork = pd.DataFrame()
        else:
            try:
                COLUMN_NAMES = ['code', 'name', 'start_date', 'end_date', 'lat', 'lon','url']

                '''FDSNStationXML parsing
                '''
                xpars = xmltodict.parse(response.content)
                '''initialization of the outgoing dataframe
                '''
                SeismicNetwork = pd.DataFrame(index=range(len(xpars['FDSNStationXML']['Network']['Station'])), columns=COLUMN_NAMES)

                for ii in range(SeismicNetwork.shape[0]):
                    SeismicNetwork['code'][ii] = xpars['FDSNStationXML']['Network']['Station'][ii]['@code']
                    SeismicNetwork['url'][ii] = 'http://webservices.ingv.it/fdsnws/station/1/query?nodata=404&authoritative=any&&level=channel&net=IV&sta='+ SeismicNetwork['code'][ii]
                    SeismicNetwork['name'][ii] = xpars['FDSNStationXML']['Network']['Station'][ii]['Site']['Name']
                    SeismicNetwork['start_date'][ii] = xpars['FDSNStationXML']['Network']['Station'][ii]['@startDate']
                    SeismicNetwork['lat'][ii] = xpars['FDSNStationXML']['Network']['Station'][ii]['Latitude']
                    SeismicNetwork['lon'][ii] = xpars['FDSNStationXML']['Network']['Station'][ii]['Longitude']

                    if '@endDate' in xpars['FDSNStationXML']['Network']['Station'][ii]:
                        SeismicNetwork['end_date'][ii] = xpars['FDSNStationXML']['Network']['Station'][ii]['@endDate']
                    else:
#                        SeismicNetwork['end_date'][ii] = 'no-end-date'
                        SeismicNetwork['end_date'][ii] = SeismicNetwork['end_date'][ii]
                code = 0
                message = 'Application completed'

            except:
                code = -2
                message = 'error in FDSNStationXML parsing'

        return SeismicNetwork, code, message

#c = seismic_network_IV(URL).get()
