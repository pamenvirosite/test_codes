#!usr/bin/env python
# encoding: utf-8

import requests
from requests.adapters import HTTPAdapter
import psycopg2
import re
import sys
import time

start_time = time.time()

# define requests http, https adapters
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=5))
session.mount('https://', HTTPAdapter(max_retries=5))


# Get the arguments list 
userinputs = sys.argv

# module-level vars
inputfile = "'"+userinputs[1]+"'"
lng = float(userinputs[2])
lat = float(userinputs[3])
city = "'"+userinputs[4]+"'"
state = "'"+userinputs[5]+"'"
meterdist = float(sys.argv[6])/0.000621371

class StreetNameGetter(object): 
    def __init__(self):
            
        # define PG connection
        self.pgconn = psycopg2.connect("host='10.200.2.90' dbname='standard_admin' port= 5433 user='standard_admin'  password='PRF20555'")
        self.rows = []
        self.verticeslist = []
        self.rings = [[]]   
        self.streetnamelist = [] 
        

    def getstreetnamelist(self, lng, lat, meterdist):
        """Queries a Postgres-Postgis table"""

        curs = self.pgconn.cursor()
        # execute query                   
        curs.execute("SELECT st_astext(st_buffer(st_setsrid(st_point( %s, %s), 4326) :: geography, %s) ) " % (lng, lat, meterdist) )
        
        
        # fetch records as a python list
        self.rows = curs.fetchall()

        polygontext = self.rows[0][0]
        
        self.verticeslist = re.findall('[-+]?[0-9]*\.[0-9]+ [-+]?[0-9]*\.[0-9]+' , polygontext)

        for i in self.verticeslist:
            longitude = float(i.split(' ')[0])
            latitude = float(i.split(' ')[1])
            coord = [longitude,latitude]
            self.rings[0].append(coord)

        
        request_string = 'http://10.200.2.168:6080/arcgis/rest/services/US_Streets/MapServer/0/query?geometryType=esriGeometryPolygon&geometry={"rings":[' \
        + str(self.rings[0]) + ',],"spatialReference" : {"wkid":4326}}&spatialRel=esriSpatialRelIntersects&returnGeometry=false&outFields=StreetNamePrefix,StreetNameBase&f=json'
        request_string = request_string.replace(' ', '')

        r = session.get(request_string)
        rest_response = r.json()
        features = rest_response['features']
        self.streetnamelist = []
        for i in features:
            streetnameprefix = i['attributes']['StreetNamePrefix']
            streetnamebase   = i['attributes']['StreetNameBase']
            streetname = ''
            if streetnameprefix == '': streetname = streetnamebase
            else:   streetname = streetnameprefix + ' ' + streetnamebase
            dct = dict({'streetname': streetname}) 
            if dct not in self.streetnamelist:
                self.streetnamelist.append(dct)
        
        curs.close()

        # print self.streetnamelist
        return self.streetnamelist

    



    def getunmap(self, inputfile,lng, lat, city, state, meterdist):
        #convert list to tuple
        streetnametuple = tuple(self.streetnamelist)
        

        roadtbl = '_' + re.findall('[0-9]+' , inputfile)[0] + '_roads'
        createtblcmd = 'CREATE TABLE ' + roadtbl + '(gid serial primary key, streetname varchar(100))'
        executemanycmd = 'INSERT INTO ' + roadtbl + '(streetname) VALUES (%(streetname)s)'
        droptablcmd = 'DROP TABLE ' + roadtbl + ' CASCADE'
    
        curs = self.pgconn.cursor()

        curs.execute('SET ROLE TO admin;')
        curs.execute( createtblcmd ) # create table
        curs.executemany(executemanycmd, streetnametuple) #insert rows
        curs.execute("SELECT * FROM  fx.getunmap_navteq(%s, %s, %s, %s, %s, %s) " % (inputfile , lng , lat , city , state , meterdist ) )
        print 'Finished executing function ...'

        curs.execute(droptablcmd)
      
        self.pgconn.commit()
        curs.close()
        self.pgconn.close()

        # report run interval
        print('ran in', time.time() - start_time, 'seconds')

        return




if __name__ == '__main__':
    instance = StreetNameGetter()
    instance.getstreetnamelist(lng, lat, meterdist)
    instance.getunmap(inputfile , lng , lat , city , state , meterdist)


