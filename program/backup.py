import datetime
import time
import boto3
import os
import tempfile
from program import encryption as lib

def run(sourcefolder, destbucket, password, backupName):

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
                with open(file, 'rb') as in_file, tempfile.SpooledTemporaryFile(max_size=100000000) as out_file:
                    lib.encrypt(in_file, out_file, password)
                    out_file.flush()
                    out_file.seek(0)
                    bucket.put_object(Key=sum, Body=out_file)

                print("Uploaded: " + file)
                anyNewfiles = True
        except:
            print "Warning: Could not read file: " + file

    if anyNewfiles :
        millis = int(round(time.time() * 1000))

        metafile = "meta_"

        if backupName != '':
            metafile += backupName + "_"

        metafile += str(datetime.date.today()) + "_" + str(millis)

        with tempfile.SpooledTemporaryFile(max_size=100000000) as meta_plain:
            meta_plain.write(metadata)
            meta_plain.flush()
            meta_plain.seek(0)

            with tempfile.SpooledTemporaryFile(max_size=100000000) as meta_enc:
                lib.encrypt(meta_plain, meta_enc, password)
                meta_enc.flush()
                meta_enc.seek(0)
                bucket.put_object(Key=metafile, Body=meta_enc)

        print("Finished. Uploaded new meta file: " + metafile)
    else :
        print "Finished. No new files to upload."