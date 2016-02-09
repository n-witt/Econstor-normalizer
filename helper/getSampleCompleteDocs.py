#! /usr/bin/env python2

import random
import os
import shutil
import sys

numDocsDefault = 100
if len(sys.argv) > 1:
    try:
        numDocs = int(sys.argv[1])
    except ValueError:
        numDocs = numDocsDefault
else:
    numDocs = numDocsDefault

sourceDir = 'json-20160122'
sinkDir = 'samples'
wd = os.getcwd()

if not os.path.exists(wd + os.sep + sourceDir): 
    raise Exception('Source dir or journal doesn\'t exist')

if not os.path.exists(sinkDir):
    os.mkdir(sinkDir)

keys = os.listdir(sourceDir)
docs = []

for i in xrange(numDocs):
    randKey = random.randrange(0, len(keys))
    docs.append(keys[randKey])

for doc in docs:
    shutil.copy(os.path.join(wd, sourceDir, doc), os.path.join(wd, sinkDir, doc))
