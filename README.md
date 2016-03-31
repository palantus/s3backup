# Unofficial Amazon S3 Folder Backup Script
Backs up a folder to an Amazon S3 bucket after encrypting it

##Usage

```
Usage: s3backup.py -f <folder> -b <bucket> -a <action>

Parameters:
-f, --folder   source folder to back up
-b, --bucket   S3 bucket to back up to
-a, --action   action to perform:
                 "backup": backs up data
                 "restore": restores data
                 "list": lists all backups on S3
-c             run action without any prompts
               (useful for running in cron jobs).
```

It requires a s3backup.ini config file located in the current working folder or the parent with content like this:

```bash
[main]
tempfolder=/path/of/temp/directory
password=mypass
```

##How does it work?

###Backup
1. Find all local files and all files currently on S3.
2. Generates MD5 sums of all local files.
3. Find all MD5 sums which doesn't exist on S3 as files.
4. Encrypt the local files with the supplied password
5. Upload the files to S3 with the MD5 sum as key
6. Write a meta file which has one line of `<MD5sum> <filepath>` for each file
7. Encrypt the meta file
8. Upload the meta file to S3

###Restore
TBD

###List
Lists all files on S3 starting with `meta_`.