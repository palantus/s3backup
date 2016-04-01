#!/usr/bin/python

import os
import ConfigParser
import sys
import getopt
from program import backup as backup
from program import restore as restore
from program import manage as manage
from program import tools as tools

def printOptions():
    print 'Usage: s3backup.py -f <folder> -b <bucket> -a <action>'
    print ''
    print 'Parameters:'
    print '-f, --folder   source folder to backup and dest folder for restore'
    print '-b, --bucket   S3 bucket to back up to and to restore from'
    print '-a, --action   action to perform:'
    print '                 "backup": backs up data'
    print '                 "restore": restores data'
    print '                 "list": lists all backups on S3'
    print '-c             run action without any prompts (useful for running in cron jobs).'
    print '-n, --name     a backup name (optional). Will be part of metafile filename'
    print '-s             simulate. No files will be uploaded to S3.'
    print '-m, --meta     meta file name from which the backup will be restored'

def main(argv):
    folder = ""
    bucket = ""
    action = "";
    metafilename = "";
    confirmAction = True
    backupName = "";
    simulate = False
    delete = False

    try:
        opts, args = getopt.getopt(argv,"hf:b:a:cn:sdm:",["folder=","bucket=","action=", "name=", "meta="])
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
            folder = arg
        elif opt in ("-b", "--bucket"):
            bucket = arg
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-m", "--meta"):
            metafilename = arg
        elif opt in ("-c"):
            confirmAction = False
        elif opt in ("-s"):
            simulate = True
        elif opt in ("-d"):
            delete = True


        elif opt in ("-n", "--name"):
            backupName = tools.slugify(arg)

    print 'Source folder: ' + folder
    print 'Destination bucket: ' + bucket

    if not os.path.isdir(folder):
        print "Source folder doesn't exist"
        sys.exit(0)

    if len(bucket) == 0:
        print "No bucket provided"
        sys.exit(0)

    if not os.path.isfile("../s3backup.ini") and not os.path.isfile("s3backup.ini"):
        print "Missing config file s3backup.ini"

        print "Sample config:"
        print ""
        print "[main]"
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

    password = getConfig("password")

    if backupName != "":
        print 'Backup name: ' + backupName

    if action == "restore":
        print 'Meta file to restore: ' + metafilename

    if simulate:
        print 'Simulation: Yes. No files will be sent to S3.'

    if delete:
        print 'Delete: Yes. Files deleted locally will also be deleted on S3!'

    print "Action: " + action
    print ""

    if confirmAction:
        raw_input("Press Enter to continue...")
        print '';

    if action == "backup":
        backup.run(folder, bucket, password, backupName, simulate, delete)
    elif action == "restore":
        restore.run(folder, bucket, password, metafilename, simulate, delete)
    elif action == "list":
        manage.list(bucket)
    else:
        print "No action provided or unknown action"

if __name__ == "__main__":
    main(sys.argv[1:])