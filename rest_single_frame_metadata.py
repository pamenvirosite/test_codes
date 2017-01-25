#!usr/bin/env python
# encoding: utf-8

''' This script takes in 2 arguments: Project value and username.
To use this script, as example, type into the terminal:
$ python rest_single_frame_metatata.py PVD09 ltramos
The code will export the metadata and extent in csv format for you.
Just make sure that /home/<username>/envirosite/csv/ exists. '''

import requests
from requests.adapters import HTTPAdapter
import csv
import os
import sys



# define requests http, https adapters
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=10))
session.mount('https://', HTTPAdapter(max_retries=10))

# Get the arguments list 
userinputs = sys.argv

#assign arguments to module-level vars
project = userinputs[1]
user = userinputs[2]


maxquerycount = 6000 # maxquerycount of the service

url_query = "http://10.200.2.168:6080/arcgis/rest/services/Historical_Aerial_Metadata/MapServer/1/query?"

OUTFIELDS = 'Alias,Agency,Vendor_ID,Recording_Technique,Project,Event,Roll,Frame,Acquisition_Date,Scale,Strip_Number,Image_Type,Quality,Cloud_Cover,Photo_ID,Flying_Height_in_Feet,Film_Length_and_Width,Focal_Length,Stereo_Overlap,Other,Center_Latitude,Center_Longitude,NW_Corner_Lat,NW_Corner_Long,NE_Corner_lat,NE_Corner_Long,SE_Corner_Lat,SE_Corner_Long,SW_Corner_Lat,SW_Corner_Long,Center_Latitude_dec,Center_Longitude_dec,NW_Corner_Lat_dec,NW_Corner_Long_dec,NE_Corner_Lat_dec,NE_Corner_Long_dec,SE_Corner_Lat_dec,SE_Corner_Long_dec,SW_Corner_Lat_dec,SW_Corner_Long_dec,Display_ID,Ordering_ID,Download_Link'

request_count = url_query + "where=Project='" + project + "'" +'&returnIdsOnly=true&outFields=Alias&returnDistinctValues=true&returnCountOnly&f=json'

r = session.get(request_count)
jsonresult = r.json()
objectidcount = len(jsonresult['objectIds'])
if objectidcount <= maxquerycount: #6000 is the maxquerycount of the service
    objectidlist = jsonresult['objectIds']
    objectidlist_str = ','.join(str(e) for e in objectidlist)[1:-1]

    request_all_columns = url_query + "where=OBJECTID IN (" + objectidlist_str + ')&returnGeometry=false&outFields=' + OUTFIELDS+'&returnCountOnly=false&f=json'

    r = session.get(request_all_columns)
    jsonresult = r.json()
    features = jsonresult['features']


    attrib_list = []
    for i in features:
        attrib_list.append(i['attributes'])
        

    project_dir = os.path.join('/home',user, 'envirosite/csv',project)

    if not os.path.exists(project_dir):
        os.mkdir(project_dir)

    filename1 = project_dir + '/' + project + '_metadata.csv'
   

    f = csv.writer(open(filename1, "wb+"))

    # # Write CSV Header
    f.writerow(["entity_id","agency","vendor_id","recording_technique","project","event","roll","frame","acquisition_date","scale","strip_number","image_type","quality","cloud_cover","photo_id","flying_height_in_feet","film_length_and_width","focal_length","stereo_overlap","other","center_latitude","center_longitude","nw_corner_lat","nw_corner_long","ne_corner_lat","ne_corner_long","se_corner_lat","se_corner_long","sw_corner_lat","sw_corner_long","center_latitude_dec","center_longitude_dec","nw_corner_lat_dec","nw_corner_long_dec","ne_corner_lat_dec","ne_corner_long_dec","se_corner_lat_dec","se_corner_long_dec","sw_corner_lat_dec","sw_corner_long_dec","display_id","ordering_id","download_link"])
    
    
    
    for x in attrib_list:
        f.writerow([ x[ "Alias" ],
            x["Agency" ], 
            x["Vendor_ID" ],
            x["Recording_Technique"],
            x["Project"],
            x["Event"],
            x["Roll"],
            x["Frame"],
            x["Acquisition_Date"],
            x["Scale"],
            x["Strip_Number"],
            x["Image_Type"],
            x["Quality"],
            x["Cloud_Cover"],
            x["Photo_ID"],
            x["Flying_Height_in_Feet"],
            x["Film_Length_and_Width"],
            x["Focal_Length"],
            x["Stereo_Overlap"],
            x["Other"],
            str(x["Center_Latitude"].encode('utf-8)') ),
            str(x["Center_Longitude"].encode('utf-8)') ),
            str(x["NW_Corner_Lat"].encode('utf-8)') ),
            str(x["NW_Corner_Long"].encode('utf-8)') ),
            str(x["NE_Corner_lat"].encode('utf-8)') ),
            str(x["NE_Corner_Long"].encode('utf-8)') ),
            str(x["SE_Corner_Lat"].encode('utf-8)') ),
            str(x["SE_Corner_Long"].encode('utf-8)') ),
            str(x["SW_Corner_Lat"].encode('utf-8)') ),
            str(x["SW_Corner_Long"].encode('utf-8)') ),
            x["Center_Latitude_dec"],
            x["Center_Longitude_dec"],
            x["NW_Corner_Lat_dec"],
            x["NW_Corner_Long_dec"],
            x["NE_Corner_Lat_dec"],
            x["NE_Corner_Long_dec"],
            x["SE_Corner_Lat_dec"],
            x["SE_Corner_Long_dec"],
            x["SW_Corner_Lat_dec"],
            x["SW_Corner_Long_dec"],
            x["Display_ID"],
            x["Ordering_ID"],
            x["Download_Link"]
            ])

 


    filename2 = project_dir + '/' + project + '_extent.csv'
   

    g = csv.writer(open(filename2, "wb+"))
    
    #  Write without CSV Header
    for x in attrib_list:
        g.writerow([ x[ "Alias" ],
            x["NW_Corner_Long_dec"],
            x["NW_Corner_Lat_dec"],
            x["NE_Corner_Long_dec"],
            x["NE_Corner_Lat_dec"],
            x["SE_Corner_Long_dec"],
            x["SE_Corner_Lat_dec"],
            x["SW_Corner_Long_dec"],
            x["SW_Corner_Lat_dec"],
            ])

    print 'Done exporting 2 files to: {}...'.format(project_dir) # status report

        
 

else: print 'Returned rows exceed maxQueryCount parameter of REST service.'

