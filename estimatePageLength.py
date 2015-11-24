'''
Created on 23.11.2015

@author: user
'''
import os
from pdfTools import pdf2txt
import random
import datetime
import math

wd = "data/files"
docs = os.listdir(wd)
randomness = random.seed(str(datetime.datetime.now()))

for i in range(10):
    sampleNumber = int(math.floor(random.random()*len(docs)))
    sampleDoc = docs[sampleNumber]
    print sampleDoc
    for j in range(10):
        try:
            print "   " + str(j) + "th page length -> " + str(len(pdf2txt.pdf_to_txt(wd + os.sep + sampleDoc, j, j)))
        except Exception as e:
            print "error"
            pass
        
