#!/usr/bin/python

import os
import ConfigParser
import sys
import getopt
from lib import backup as backup
from lib import manage as manage

def main(argv):
    sourcefolder = ""
    destbucket = ""
    action = "";
    try:
        opts, args = getopt.getopt(argv,"hf:b:a:",["folder=","bucket=","action="])
    except getopt.GetoptError:
        print 'Usage: s3backup.py -f <folder> -b <bucket>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Usage: s3backup.py -f <folder> -b <bucket> -a <action>'
            print "Action can be: backup, restore, list"
            print '  backup: backs up data'
            print '  restore: restores data'
            print '  list: lists all backups on S3'
            sys.exit()
        elif opt in ("-f", "--folder"):
            sourcefolder = arg
        elif opt in ("-b", "--bucket"):
            destbucket = arg
        elif opt in ("-a", "--action"):
            action = arg

    print 'Source folder: ' + sourcefolder
    print 'Destination bucket: ' + destbucket

    if not os.path.isdir(sourcefolder):
        print "Source folder doesn't exist"
        sys.exit(0)

    if len(destbucket) == 0:
        print "No bucket provided"
        sys.exit(0)

    if not os.path.isfile("../s3backup.ini") and not os.path.isfile("s3backup.ini"):
        print "Missing config file s3backup.ini"

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
    if os.path.isfile("s3backup.ini"):
        Config.read("s3backup.ini")
    else:
        Config.read("../s3backup.ini")

    def getConfig(config):
        try:
            val = ConfigSectionMap("main")[config]
            print config + ": " + val
            return val;
        except:
            print("Missing '" + config + "' in config file")
            sys.exit(0)

    temp_folder = getConfig("tempfolder")
    password = getConfig("password")
    print "Action: " + action
    print ""

    if action == "backup":
        backup.run(sourcefolder, destbucket, temp_folder, password)
    elif action == "list":
        manage.list(destbucket)
    else:
        print "No action provided or unknown action"

if __name__ == "__main__":
    main(sys.argv[1:])