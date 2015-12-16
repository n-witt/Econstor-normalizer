'''
Created on 19.11.2015

@author: nils witt
'''

import json
import os
import urllib2
import logging

logging.getLogger().setLevel(logging.INFO)
#wd = os.getcwd()
wd = '../../data'

def mkDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

with open("./econstore.xml", "r") as data_file:
    data = json.load(data_file)
    if data.has_key("hits") and data["hits"].has_key("hits"):
        data = data["hits"]["hits"]
    else:
        raise Exception("unknown Datastructure")
# create directory if not there
pdfDir = wd + os.sep +  u'pdf'
jsonDir = wd  + os.sep + u'json'
failDir = wd + os.sep + os.sep + u'fail'
for f in (pdfDir, jsonDir, failDir):
    mkDir(f)
    
u = ""
failedDownloads = []
for item in data:
    url = item["identifier_url"][0]
    filename = url.split("/")[-1]        
    try:
        # download the pdf file
        if not os.path.exists(pdfDir + os.sep + filename):
            u = urllib2.urlopen(url)
            localFile = open(pdfDir + os.sep + filename, 'w')
            localFile.write(u.read())
            localFile.close() 
            logging.log(logging.INFO, filename + " successfully downloaded.")
        else:
            logging.log(logging.INFO, filename + " skipped. already downloaded.")        
    
    except Exception as e:
        logging.log(logging.INFO, url + " couldn't be opened.") 
        failedDownloads.append(item)
        print e
        continue
    
    else:
        #write meta data in json file
        metadata = json.dumps(item)
        if os.path.exists(filename):
            logging.log(logging.INFO, filename + u'.json' + "exists already. skipping file.")
        else:
            localFile = open(jsonDir + os.sep + filename + u'.json', 'w')
            localFile.write(metadata)
            localFile.close() 
            logging.log(logging.INFO, filename + u'.json' + " meta data file written")


if len(failedDownloads) > 0:
    handler = open(failDir + os.sep + "failedToDownload.json", "w")
    handler.write(json.dumps(failedDownloads))
logging.log(logging.INFO, "Downloads complete.")