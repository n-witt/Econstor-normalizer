#! /usr/bin/env python3

import os
import json
import sys

lukeDir = u'json'
hanDir = 'json-20160105'
resultDir = 'json-20160122'

lukeFiles = set(os.listdir(lukeDir))
hanFiles = set(os.listdir(hanDir))

for i, fileName in enumerate(lukeFiles & hanFiles):
    with open(os.path.join(os.curdir, lukeDir, fileName), 'r') as lf:
            lukeJson = json.load(lf)
    with open(os.path.join(os.curdir, hanDir, fileName), 'r') as hf:
            hanJson = json.load(hf)

    lukeJson.update(hanJson)
    with open(os.path.join(os.curdir, resultDir, fileName), 'w') as rf:
            json.dump(lukeJson, rf)
