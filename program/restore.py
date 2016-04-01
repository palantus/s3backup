import datetime
import time
import boto3
import os
import tempfile
import sys
from program import encryption as lib
from tempfile import mkstemp

def run(folder, bucket, password, metafile, simulate, delete):

    if(simulate or delete):
        print "Simulate and delete aren't supported yet. Exiting..."
        sys.exit(0);

    # Remove / in the end of path if given
    if folder.endswith("/"):
        sourcefolder = folder[:folder.rfind('/')]

    if metafile == "":
        print "Meta file not provided."
        sys.exit(0);

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    _, temp_path = mkstemp()
    bucket.download_file(metafile, temp_path)

    with open(temp_path) as meta_enc, tempfile.SpooledTemporaryFile(max_size=100000000) as meta_plain:

        lib.decrypt(meta_enc, meta_plain, password)

        meta_plain.flush()
        meta_plain.seek(0)
        content = meta_plain.readlines()
        content = [x.strip('\n') for x in content]

        # Find unique paths
        uniquePaths = set()
        for line in content:
            _, _, filepath = line.partition(' ')
            if(filepath.find("/") >= 0):
                uniquePaths.add(filepath[:filepath.rfind('/')])

        # Create unique paths
        for path in uniquePaths:
            fullpath = os.path.join(folder, path)
            if not os.path.isdir(fullpath):
                os.makedirs(fullpath)
                print "Created folder: " + fullpath

        # Create files
        for line in content:
            md5sum, _, filepath = line.partition(' ')
            fullfilepath = os.path.join(folder, filepath)

            # Check if file already exists
            if os.path.isfile(fullfilepath):
                if lib.md5file(fullfilepath) == md5sum:
                    continue
                else:
                    print "Deleting modified file: " + fullfilepath
                    os.remove(fullfilepath)

            _, temp_file = mkstemp()

            bucket.download_file(md5sum, temp_file)

            with open(temp_file) as file_enc, open(fullfilepath, "wb") as file_plain:
                lib.decrypt(file_enc, file_plain, password)

            print "Created file: " + fullfilepath

            if (os.path.isfile(temp_file)):
                os.remove(temp_file)


    if(os.path.isfile(temp_path)):
        os.remove(temp_path)

    print ""