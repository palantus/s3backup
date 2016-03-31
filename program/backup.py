import datetime
import time
import boto3
import os
from program import encryption as lib

def run(sourcefolder, destbucket, tempfolder, password):

    print "Running backup..."

    #Run the backup
    s3 = boto3.resource('s3')

    print "Getting list of files from S3..."

    s3files = set()
    bucket = s3.Bucket(destbucket)
    for obj in bucket.objects.all():
        s3files.add(obj.key)

    print "Got a list of " + str(len(s3files)) + " files from S3 (including meta files)"
    print "Finding all local files in source directory..."

    localFiles = []
    for root, dirnames, filenames in os.walk(sourcefolder):
        for filename in filenames:
            localFiles.append(os.path.join(root, filename))

    print "Found " + str(len(localFiles)) + " files in source directory"
    print "Iterating through local files and finding differences..."

    metadata = ""
    anyNewfiles = False

    for file in localFiles:
        try:
            sum = lib.md5file(file)
            metadata += sum + " " + file + "\n"

            if sum not in s3files:
                encfile = tempfolder + "/" + sum
                with open(file, 'rb') as in_file, open(encfile, 'wb') as out_file:
                    lib.encrypt(in_file, out_file, password)
                data = open(encfile, 'rb')
                bucket.put_object(Key=sum, Body=data)
                os.remove(encfile)
                print("Uploaded: " + file)
                anyNewfiles = True
        except:
            print "Warning: Could not read file: " + file

    if anyNewfiles :
        millis = int(round(time.time() * 1000))
        metafile = "meta_" + str(datetime.date.today()) + "_" + str(millis)
        metapath = tempfolder + "/" + metafile
        text_file = open(metapath, "w")
        text_file.write(metadata)
        text_file.close()

        encfile = metapath + ".enc"
        with open(metapath, 'rb') as in_file, open(encfile, 'wb') as out_file:
            lib.encrypt(in_file, out_file, password)

        data = open(encfile, 'rb')
        bucket.put_object(Key=metafile, Body=data)
        print("Finished. Uploaded new meta file: " + metafile)
    else :
        print "Finished. No new files to upload."