#!usr/bin/env python
# encoding: utf-8

import psycopg2
import sys
import pprint
import psycopg2.extras
import requests

# conn_aerial = psycopg2.connect("host='10.200.2.90' dbname= 'aerial' port= '5433' user= 'ptorres' password= 'crave16'")
conn_webapp_test = psycopg2.connect("host='10.200.2.90' dbname= 'webapp_test' port= '5433' user= 'ptorres' password= 'crave16'")

# cur = conn_aerial.cursor()
# cur1 = conn_webapp_test.cursor()
cur1 = conn_webapp_test.cursor(cursor_factory=psycopg2.extras.DictCursor)

# if cur1:
# 	print 'connected'
# else: 'you have a problem'
# createcmd = "CREATE TABLE public.test3 (gid serial PRIMARY KEY, num integer, data varchar(100), date_today date) "

# insertmanycmd = """INSERT INTO test3 (num, data) VALUES (%(num)s, %(data)s)"""

# # cur.execute(createcmd)

# data_name = ({"num":123, "data":"keep"},
# 			 {"num":456, "data":"on"},
# 			 {"num":789, "data":"practicising"})
# cur.executemany( insertmanycmd, data_name )

# createtable = "CREATE TABLE sample (objectid integer, prop_addr1 varchar, prop_city varchar, prop_state varchar )"
# cur.execute(createtable)
cur1.execute("SELECT objectid, prop_addr1, prop_city, prop_state from pmt.ny15e where status = %s order by objectid LIMIT %s",('M',5,))
records = cur1.fetchall()
pprint.pprint(records)

# re = requests.get(http://qai-gis.envirositecorp.com:6080/arcgis/rest/services/USA_ZIP4/GeocodeServer/geocodeAddresses?addresses={"records":[{"attributes":{"OBJECTID":1,"SingleLine":"9, 2772 BROADWAY, CHEEKTOWAGA, NY"}},{"attributes":{"OBJECTID":2,"SingleLine":"10, 55 WATER STREET, NEW YORK, NY"}},{"attributes":{"OBJECTID":3,"SingleLine":"11, 44 10TH AVENUE, HUNTINGTON STATION, NY"}},{"attributes":{"OBJECTID":4,"SingleLine":"12, 3341 98TH ST., EAST ELMHURST, NY"}},{"attributes":{"OBJECTID":5,"SingleLine":"13, 112 TRADE RD, PLATTSBURGH, NY"}}]}&sourceCountry=USA&f=pjson)


# Make the changes to the database persistent
# conn_aerial.commit()
conn_webapp_test.commit()

cur1.close()
# conn_aerial.close()
conn_webapp_test.close()