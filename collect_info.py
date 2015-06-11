#!/usr/bin/env python
__author__ = 'Alex Moskalenko'



import MySQLdb
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

GlusterDir = "/var/data/www/"
ImagesDir = "/images/www/"
BrokenFileList = "broken.list"
MissingOnImagesList = "missing_on_images"
MissingOnBothList = "missing_on_both"
BrokenImagesList= "broken_on_images"
Log = "finished.log"

data = { 'product' : [ 'low_pic' , 'high_pic' , 'thumb_pic' , 'medium_pic' ] ,
        'product_gallery' : [ 'link' , 'thumb_link' , 'low_link' , 'medium_link' , 'link_raw' ] ,
        'product_multimedia_object' : [ 'link' , 'preview_link' , 'converted_link' , 'thumb_link' ] ,
        'product_bullet' : [ 'icon_url' ] ,
        'category' :  [ 'low_pic' , 'thumb_pic' ] ,
        'supplier' :  [ 'low_pic' , 'thumb_pic' ] ,
        'product_description' :  [ 'pdf_url' , 'manual_pdf_url' ] }

id_retrieve = { 'product' : 'product_id',
    'product_gallery' : 'product_id',
    'product_multimedia_object' : 'product_id',
    'product_bullet' : 'product_id',
    'product_description' : 'product_id',
    'category' : 'catid',
    'supplier' : 'supplier_id' }


not_images = ["mp4", "flv", "tmp", "pdf"]


db = MySQLdb.connect(host="HOST", db="DB", user="USER", passwd="PASSWD")

cur = db.cursor()

TempList = []
TypesDict = {}
TotalCount = 0
BrokenCount = 0
MissingOnImages = 0
MissingOnBoth = 0

for table in data:
        for column in data[table]:
            print "Reading " + table + "." + column
            moi_list = table + "." + column + "." + MissingOnImagesList
            mob_list = table + "." + column + "." + MissingOnBothList
            boi_list = table + "." + column + "." + BrokenImagesList
            l = 10000
            o = 0

            sql = "SELECT {0},{2} FROM {1} where {0} like '%icecat.biz%' and {0} not like '%bo.icecat.biz%' LIMIT {3} OFFSET {4}".format(column, table, id_retrieve[table], l, o)
            cur.execute(sql)
            rows = cur.fetchall()

            while len(rows) > 0:
                for row in rows:
                    while os.path.exists("collectwait"):
                        time.sleep(1)

                    url = urlparse(row[0])
                    prod_id = row[1]
                    path =  url.path
                    ftype = path.split("/", 2)[1]

                    if not ftype in TypesDict:
                        TypesDict[ftype] = 1
                    else:
                        TypesDict[ftype] += 1

                    if os.path.exists(GlusterDir + path) and os.path.exists(ImagesDir + path):
                        with open(GlusterDir + path, "rb") as fsrc, open(ImagesDir + path, "rb") as fdst:
                            SrcHash = md5_for_file(fsrc)
                            DstHash = md5_for_file(fdst)
                            if not SrcHash == DstHash and not ftype in not_images:
                            try:
                                with Image(filename=ImagesDir + path) as im:
                                    idle = 1
                            except:
                                with open(boi_list, "a") as w:
                                    w.write(str(prod_id) + "," + path + "\n")
                                    BrokenCount += 1

                    elif os.path.exists(GlusterDir + path) and not os.path.exists(ImagesDir + path):
                        with open(moi_list, "a") as w:
                            w.write(str(prod_id) + "," + path + "\n")
                            MissingOnImages += 1

                    elif not os.path.exists(GlusterDir + path) and not os.path.exists(ImagesDir + path):
                        with open(mob_list, "a") as w:
                            w.write(str(prod_id) + "," + path + "\n")
                            MissingOnBoth += 1

                    TotalCount += 1
                    sys.stdout.write("\rBroken: %d, MissingOnImages: %d, MissingOnBoth: %d, Total: %d" % ( BrokenCount, MissingOnImages, MissingOnBoth, TotalCount))
                    sys.stdout.flush()
                o += l
                sql = "SELECT {0},{2} FROM {1} where {0} like '%icecat.biz%' and {0} not like '%bo.icecat.biz%' LIMIT {3} OFFSET {4}".format(column, table, id_retrieve[table], l, o)
                cur.execute(sql)
                rows = cur.fetchall()
            with open(Log, "a") as a:
                a.write("Finished" + table + "." + column + "\n")


print '\n' + str(TypesDict)
