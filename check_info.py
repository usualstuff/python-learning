#!/usr/bin/env python
__author__ = 'Alex Moskalenko'


import time
from urlparse import urlparse
from wand.image import Image
import hashlib
import os
import sys

def md5_for_file(f, block_size=2**20):
        md5 = hashlib.md5()
        while True:
                data = f.read(block_size)
                if not data:
                        break
                md5.update(data)
        return md5.digest()

def percentage(part, whole):
        return 100 * float(part)/float(whole)

StorageDir = "/storage/www/"
BrokenFileList = "broken.list"
MissingList = "missing.list"
BrokenCount = 0
TotalCount = 0
MissingCount = 0
TypesDict = {}

not_images = ["mp4", "flv", "tmp", "pdf"]

with open("new_missing_on_both", "r") as f:
    for row in f:
        #while os.path.exists("collectwait"):
        #	time.sleep(1)

        try:
            row = row.rstrip().split(",")
            prod_id = row[0]
            path =  row[1]
        except IndexError:
            continue
        ftype = path.split(".", 1)[-1]

        if not ftype in TypesDict:
            TypesDict[ftype] = 1
        else:
            TypesDict[ftype] += 1

        if os.path.exists(StorageDir + path):
            if not ftype in not_images:
                try:
                    with Image(filename=StorageDir + path) as im:
                        idle = 1
                except:
                    with open(BrokenFileList, "a") as w:
                        w.write(str(prod_id) + "," + path + "\n")
                        BrokenCount += 1
        else:
            with open(MissingList, "a") as w:
                w.write(str(prod_id) + "," + path + "\n")
                MissingCount +=1

        TotalCount += 1
        sys.stdout.write("\rBroken: %d, MissingCount: %d,  Total: %d" % (BrokenCount, MissingCount, TotalCount))
        sys.stdout.flush()

print TypesDict
