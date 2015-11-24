'''
Created on 19.11.2015

@author: nils witt
'''

import json
import os
import urllib2
import logging

logging.getLogger().setLevel(logging.INFO)
with open("./econstore.xml", "r") as data_file:
    data = json.load(data_file)
    if data.has_key("hits") and data["hits"].has_key("hits"):
        data = data["hits"]["hits"]
    else:
        raise Exception("unknown Datastructure")
# create directory if not there
directory = os.getcwd() + os.sep + "files"
if not os.path.exists(directory):
    os.makedirs(directory)

u = ""
failedDownloads = []
for item in data:
    try:
        url = item["identifier_url"][0]
        filename = url.split("/")[-1]        
        if not os.path.exists(directory + os.sep + filename):
            u = urllib2.urlopen(url)
            localFile = open(directory + os.sep + filename, 'w')
            localFile.write(u.read())
            localFile.close() 
            logging.log(logging.INFO, filename + " successfully downloaded.")
        else:
            logging.log(logging.INFO, filename + " skipped. already downloaded.")        
        
    except Exception, e:
        logging.log(logging.INFO, url + " couldn't be opened.") 
        failedDownloads.append(item)
        print e
        continue

if len(failedDownloads) > 0:
    handler = open(directory + os.sep + "failedToDownload.json", "w")
    handler.write(json.dumps(failedDownloads))
logging.log(logging.INFO, "Downloads complete.")