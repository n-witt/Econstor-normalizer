#! /usr/bin/env python2

import os
import json

wd = 'json-20160122'
fileList = os.listdir(wd)
numFiles = len(fileList)
hasInfo = 0

for fn in fileList:
    with open(os.path.join(wd, fn)) as fd:
        try:
            data = json.load(fd)
        except ValueError:
            pass
        else:
            try:
                if data['citedBy'] != None:
                    hasInfo += 1
            except KeyError:
                print(fn + ' has no citedBy field')

print('{} of {} file have citation count information. this corresponds to {:.2}%'.format(str(hasInfo), str(numFiles), str((float(hasInfo)/numFiles)*100)))
