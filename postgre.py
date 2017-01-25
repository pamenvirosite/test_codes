#!usr/bin/env python
# encoding: utf-8

import psycopg2
import sys
import pprint
import psycopg2.extras
import requests
import pprint
import json
from requests.adapters import HTTPAdapter

conn_webapp_test = psycopg2.connect("host='10.200.2.90' dbname= 'webapp_test' port= '5433' user= 'ptorres' password= 'crave16'")

cursor = conn_webapp_test.cursor(cursor_factory=psycopg2.extras.DictCursor)
if cursor:
	print 'connected'
	
else: 'fix your code'

cursor.execute("SELECT objectid, prop_addr1, prop_city, prop_state from pmt.ny15e where status = %s order by objectid LIMIT %s",('M',5,))
records = cursor.fetchall()
pprint.pprint(records)

request_str = """http://qai-gis.envirositecorp.com:6080/arcgis/rest/services/USA_ZIP4/GeocodeServer/geocodeAddresses?addresses={"records":"""
records_list = []

for record in records:
	dct = {"attributes": {
		"OBJECTID": record['objectid'],
		"SingleLine" : record['prop_addr1'] + ' ' + record['prop_city']  + ' ' + record['prop_state']
		}
		}
	records_list.append(dct)

request_str +=  str(records_list) + '}&sourceCountry=USA&f=json'

print request_str

# var json = JSON.stringify(request_str)

# request = requests.get('http://qai-gis.envirositecorp.com:6080/arcgis/rest/services/USA_ZIP4/GeocodeServer/geocodeAddresses?addresses={"records":[{"attributes":{"OBJECTID":1,"SingleLine":"9, 2772 BROADWAY, CHEEKTOWAGA, NY"}},{"attributes":{"OBJECTID":2,"SingleLine":"10, 55 WATER STREET, NEW YORK, NY"}},{"attributes":{"OBJECTID":3,"SingleLine":"11, 44 10TH AVENUE, HUNTINGTON STATION, NY"}},{"attributes":{"OBJECTID":4,"SingleLine":"12, 3341 98TH ST., EAST ELMHURST, NY"}},{"attributes":{"OBJECTID":5,"SingleLine":"13, 112 TRADE RD, PLATTSBURGH, NY"}}]}&sourceCountry=USA&f=pjson')

# request = requests.get('http://qai-gis.envirositecorp.com:6080/arcgis/rest/services/USA_ZIP4/GeocodeServer/geocodeAddresses?addresses={"records":[{'attributes': {'SingleLine': '2772 BROADWAY CHEEKTOWAGA NY', 'OBJECTID': 9}}, {'attributes': {'SingleLine': '55 WATER STREET NEW YORK NY', 'OBJECTID': 10}}, {'attributes': {'SingleLine': '44 10TH AVENUE HUNTINGTON STATION NY', 'OBJECTID': 11}}, {'attributes': {'SingleLine': '3341 98TH ST. EAST ELMHURST NY', 'OBJECTID': 12}}, {'attributes': {'SingleLine': '112 TRADE RD PLATTSBURGH NY', 'OBJECTID': 13}}]}&sourceCountry=USA&f=json')


# print request.status_code
# print request.status_code == requests.codes.ok
# print requests.codes['temporary_redirect']
# print requests.codes.teapot
# print requests.codes['o/']
# print request.text
# print request.headers['Content-Type']
# print request.encoding

conn_webapp_test.commit()

cursor.close()
# conn_aerial.close()
conn_webapp_test.close()