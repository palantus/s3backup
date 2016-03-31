#!/usr/bin/python

import os
import ConfigParser
import sys
import getopt
from program import backup as backup
from program import manage as manage
from program import tools as tools

def printOptions():
    print 'Usage: s3backup.py -f <folder> -b <bucket> -a <action>'
    print ''
    print 'Parameters:'
    print '-f, --folder   source folder to back up'
    print '-b, --bucket   S3 bucket to back up to'
    print '-a, --action   action to perform:'
    print '                 "backup": backs up data'
    print '                 "restore": restores data'
    print '                 "list": lists all backups on S3'
    print '-c             run action without any prompts (useful for running in cron jobs).'
    print '-n, --name     a backup name (optional). Will be part of metafile filename'

def main(argv):
    sourcefolder = ""
    destbucket = ""
    action = "";
    confirmAction = True
    backupName = "";

    try:
        opts, args = getopt.getopt(argv,"hf:b:a:cn:",["folder=","bucket=","action=", "name="])
    except getopt.GetoptError:
        printOptions()
        sys.exit(2)

    if len(opts) == 0:
        printOptions()
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            printOptions()
            sys.exit()
        elif opt in ("-f", "--folder"):
            sourcefolder = arg
        elif opt in ("-b", "--bucket"):
            destbucket = arg
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-c"):
            confirmAction = False
        elif opt in ("-n", "--name"):
            backupName = tools.slugify(arg)

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

    if confirmAction:
        raw_input("Press Enter to continue...")
        print '';

    if action == "backup":
        backup.run(sourcefolder, destbucket, temp_folder, password, backupName)
    elif action == "list":
        manage.list(destbucket)
    else:
        print "No action provided or unknown action"

if __name__ == "__main__":
    main(sys.argv[1:])