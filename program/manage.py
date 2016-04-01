import boto3
def list(bucket):

    print "The following files on S3 denote a backup and can be restored:"

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    for obj in bucket.objects.filter(Prefix='meta_'):
        print "  " + obj.key