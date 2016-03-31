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

```
[main]
tempfolder=/path/of/temp/directory
password=mypass
```

##How does it work?

My main goal is to NOT be dependant on some 3rd party tool (like this), so all files can always be restored using standard Linux functionality (like a shell script with openssl).

When the backup is finished the following files will be in the S3 bucket:
  * All source files named as MD5 sums (no folders)
  * A meta file describing where the file was located and its name paired with the MD5 sum (S3 filename). The format is simply a line of `<MD5sum> <filepath>` for each file (without <>).

The MD5 sum makes it easy to identify files already on S3 and, more importantly, changes to local files.

A nice benefit is that all files are deduplicated - i.e. if you have a movie two places locally, it will only be uploaded once to S3. When restored, it'll still be placed in both of the original local folders!

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
Full restore functionality hasn't been implemented yet.

However, you can always restore files like this:

1. Download meta file of the relevant backup.
2. Decrypt it using: `openssl aes-256-cbc -d -in <metafile> -out <outputfile>`. You will be prompted for the password.
3. Find the files you want to restore from it and note the MD5 sums
4. Download those files and decrypt them using the same command.

This can easily be scripted using the AWS CLI.

###List
Lists all files on S3 starting with `meta_`.