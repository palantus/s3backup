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
-n, --name     a backup name (optional).
               Will be part of metafile filename
-s             simulate. No files will be uploaded to S3.
```

It requires a s3backup.ini config file located in the current working folder or the parent with content like this:

```
[main]
password=mypass
```

##How does it work?

My main goal is to NOT be dependant on some 3rd party tool (like this), so all files can always be restored using standard Linux functionality (like a shell script with openssl).
Additionally, it is important to note that the source directory is completely untouched (ie. it can be mounted read-only!).

When the backup is finished the following files will be in the S3 bucket:
  * All source files named as MD5 sums (no folders)
  * A meta file describing where the file was located and its name paired with the MD5 sum (S3 filename). The format is simply a line of `<MD5sum> <filepath>` for each file (without <>).

The MD5 sum makes it easy to identify files already on S3 and, more importantly, changes to local files.

A nice benefit is that all files are deduplicated - i.e. if you have a movie two places locally, it will only be uploaded once to S3. When restored, it'll still be placed in both of the original local folders!

###Backup
1. Find all local files and all files currently on S3.
2. Generate MD5 sums of all local files.
3. Find all MD5 sums which doesn't exist on S3 as files.
4. For each local file not on S3:
    1. Encrypt the local file with the supplied password to a temporary file in memory.
    2. Upload the file to S3 with the MD5 sum as key
    3. Write a a line to the meta file with`<MD5sum> <filepath>`
5. Encrypt the meta file
6. Upload the meta file to S3

###Restore
Full restore functionality hasn't been implemented yet.

However, you can always restore files like this:

1. Download meta file of the relevant backup manually from S3. It can be found using `--action list`.
2. Decrypt it using: `openssl aes-256-cbc -d -in <metafile> -out <outputfile>`. You will be prompted for the password.
3. Find the files you want to restore from it and note the MD5 sums
4. Download those files and decrypt them using the same command.

This can easily be scripted using the AWS CLI while looping through the meta file.

###List
Lists all files on S3 starting with `meta_`.