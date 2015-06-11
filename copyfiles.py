__author__ = 'Alex Moskalenko'

#!/usr/bin/env python
import shutil,os
import time,sys
import hashlib

SrcDir = "/var/data/www/"
DstDir = "/storage/www/"

FileList = "new_missing_on_images"
ProgressFile = "new_missing_on_images.progress"

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def percentage(part, whole):
        return 100 * float(part)/float(whole)

def md5_for_file(f, block_size=2**20):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()

def filecopy(src, dst):
    shutil.copy2(src, dst)
    with open(src, "rb") as fsrc, open(dst, "rb") as fdst:
        SrcHash = md5_for_file(fsrc)
        DstHash = md5_for_file(fdst)
    if SrcHash == DstHash:
        return True
    else:
        return False

p = open(ProgressFile)
Progress = int(p.read().rstrip())
p.close

TotalCount = file_len(FileList)
SkipCount = 0

f = open(FileList)
for File in f:
    File = File.split(",")[1]
    if not SkipCount == Progress:
        SkipCount += 1
        continue

    if not os.path.isfile(SrcDir + File.rstrip()):
        print "Src file not exists: " + File.rstrip()
        continue

    if not os.path.isfile(DstDir + File.rstrip()):
        if not filecopy(SrcDir + File.rstrip(), DstDir + File.rstrip()):
            print "Error for " + File.rstrip()
            break
    else:
        print "File " + File.rstrip() + " exists, skipping"

    Progress += 1
    SkipCount += 1
    with open(ProgressFile, "w") as w:
        w.write(str(Progress))

    sys.stdout.write("\r%d/%d - %.2f%%" % (Progress, TotalCount, percentage(Progress, TotalCount)))
    sys.stdout.flush()
