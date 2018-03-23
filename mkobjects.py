from boto.s3.key import Key
import argparse
import traceback
import random
import logging
import sys
import string
from boto.s3.connection import S3Connection
import boto
import datetime
import csv
import time

"""
Populate a bucket with objects following a specified size distribution

Authors:
  w.frost@lancaster.ac.uk
  p.love@lancaster.ac.uk
"""

def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bucket', help='name of target bucket')
    parser.add_argument('-m', '--mean', type=int,  help='mean size of file in bytes')
    parser.add_argument('-s', '--stddev', type=int,  help='stddev of file in bytes')
    parser.add_argument('-n', '--num', help='number of files',type=int)
    parser.add_argument('-t', '--duration', help='duration of test',type=int)
    parser.add_argument('--seed', dest='seed', help='optional seed for the random number generator')
    parser.add_argument('-k', '--key', dest='access_key', help='access key')
    parser.add_argument('-e', '--secret', dest='secret_key', help='access secret')
    parser.add_argument('-d', '--hostname', dest='hostname', default='localhost', help='hostname of endpoint')
    parser.add_argument("--profile", dest="profile", default='default', help="profile name")
    parser.add_argument('-p', '--port', dest='port', type=int, default=443, help='port number')
    parser.add_argument("-c", "--insecure", dest="is_secure", default=True, action="store_false", help="use http")
    parser.add_argument("-f", "--filename", dest="filename", help='[csv file name].csv')
    return parser.parse_args()

def put_objects(name_generator, bucket, files):
    keys = []
#    print('sending file with size %dB' % len(files),file=sys.stderr)
    key = Key(bucket)
    key.key = name_generator
#    print(key.key, file=sys.stderr)
    key.set_contents_from_string(files)
    key.set_acl('public-read')
    keys.append(key)
    return keys

def main():
    args = getargs()
    filenamedata=[datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year, args.num, args.mean, args.stddev]
    for i in range(0,len(filenamedata)):
        filenamedata[i] = str(filenamedata[i])
        if len(filenamedata[i])==1:
            filenamedata[i]='0' + filenamedata[i]
    outputwriter = csv.writer(sys.stdout)
    outputwriter.writerow(['Time_Stamp','Dest_Host', 'Dest_Bucket', 'File_Size','Duration'])
    random.seed(args.seed if args.seed else None)
    conn = S3Connection(aws_access_key_id = args.access_key,
                        aws_secret_access_key = args.secret_key,
                        host = args.hostname,
                        port = args.port,
                        is_secure = args.is_secure,
                        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
                        profile_name = args.profile)
    bucket = conn.create_bucket(args.bucket)
    bucket.set_acl('public-read')
    for i in range(args.num):
        size = int(random.normalvariate(args.mean, args.stddev))
        randname = ''.join(random.choice(string.ascii_lowercase) for _ in range(20))
        randfile = ''.join(random.choice(string.ascii_lowercase) for _ in range(size))
        starttime = time.time()
        put_objects(randname, bucket, randfile)
        ts = time.time()
        elapsed = ts - starttime
        outputwriter = csv.writer(sys.stdout)
        outputwriter.writerow([ts, args.hostname, args.bucket, size, elapsed])
        sys.stdout.flush()

if __name__ == '__main__':
    main()
