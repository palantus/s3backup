# Unofficial Amazon S3 Folder Backup Script
Backs up a folder to an Amazon S3 bucket after encrypting it

##Usage

`s3backup.py -f <folder> -b <bucket> -a <action>`

It requires a s3backup.ini config file located in the current working folder or the parent.

Sample content:

```python
[main]
tempfolder=/path/of/source/directory
password=mypass
```

`action` can be:
  * `backup`: backs up all files in source directory (recursive) to the S3 bucket specified as argument.
  * `restore`
  * `list`: lists all backups currently on S3

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