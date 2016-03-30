#!/usr/bin/python

import os
import boto3
import encryptionlib as lib
import datetime
import time
import ConfigParser
import sys
import getopt

def main(argv):
    sourcefolder = ""
    destbucket = ""
    try:
        opts, args = getopt.getopt(argv,"hf:b:",["folder=","bucket="])
    except getopt.GetoptError:
        print 'Usage: s3backup.py -f <folder> -b <bucket>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Usage: s3backup.py -f <folder> -b <bucket>'
            sys.exit()
        elif opt in ("-f", "--folder"):
            sourcefolder = arg
        elif opt in ("-b", "--bucket"):
            destbucket = arg
    print 'Source folder: ' + sourcefolder
    print 'Destination bucket: ' + destbucket

    if not os.path.isdir(sourcefolder):
        print "Source folder doesn't exist"
        sys.exit(0)

    if len(destbucket) == 0:
        print "No bucket provided"
        sys.exit(0)

    if not os.path.isfile("../config.ini"):
        print "Missing config file ../config.ini"

        print "Sample config:"
        print ""
        print "[main]"
        print "tempfolder=/place/of/temp/folder"
        print "password=mypass"
        print ""
        sys.exit(0)

    def ConfigSectionMap(section):
        dict1 = {}
        options = Config.options(section)
        for option in options:
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    Config = ConfigParser.ConfigParser()
    Config.read("../config.ini")

    def getConfig(config):
        try:
            val = ConfigSectionMap("main")[config]
            print config + ": " + val
            return val;
        except:
            print("Missing '" + config + "' in config file")
            sys.exit(0)


    #config
    temp_folder = getConfig("tempfolder")
    password = getConfig("password")
    print ""

    #Run the backup
    s3 = boto3.resource('s3')

    s3files = set()
    bucket = s3.Bucket(destbucket)
    for obj in bucket.objects.all():
        s3files.add(obj.key)

    localFiles = []
    for root, dirnames, filenames in os.walk(sourcefolder):
        for filename in filenames:
            localFiles.append(os.path.join(root, filename))

    metadata = ""
    anyNewfiles = False

    for file in localFiles:
        sum = lib.md5file(file)
        metadata += sum + " " + file + "\n"

        if sum not in s3files:
            encfile = temp_folder + "/" + sum
            with open(file, 'rb') as in_file, open(encfile, 'wb') as out_file:
                lib.encrypt(in_file, out_file, password)
            data = open(encfile, 'rb')
            bucket.put_object(Key=sum, Body=data)
            os.remove(encfile)
            print("Uploaded: " + file)
            anyNewfiles = True

    if anyNewfiles :
        millis = int(round(time.time() * 1000))
        metafile = "meta_" + str(datetime.date.today()) + "_" + str(millis)
        metapath = temp_folder + "/" + metafile
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

if __name__ == "__main__":
    main(sys.argv[1:])