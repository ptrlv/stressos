from __future__ import print_function
import argparse
import random
import string

import boto
from boto.s3.connection import S3Connection

"""
Check content of bucket, create if doesn't exist
Authors:
p.love@lancaster.ac.uk
"""

parser = argparse.ArgumentParser(description='Check content of bucket, create if doesn\'t exist')
parser.add_argument('-k', '--key', dest='access_key', help='access key')
parser.add_argument('-s', '--secret', dest='secret_key', help='access secret')
parser.add_argument('-d', '--hostname', dest='hostname', default='localhost', help='hostname of endpoint')
parser.add_argument("-c", '--insecure', dest='is_secure', default=True, action="store_false", help="use http")
parser.add_argument('-p', '--port', dest='port', type=int, default=443, help='port number')
parser.add_argument("--profile", dest="profile", default='default', help="profile name")
parser.add_argument('bucketname', help='name of bucket to list or create')

args = parser.parse_args()

def get_connection(access_key, secret_key, host, port, is_secure):
    conn = S3Connection(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host,
        port = port,
        is_secure = is_secure,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        profile_name = args.profile,
        )
    
    return conn

def main():
    conn = get_connection(args.access_key,
                          args.secret_key,
                          args.hostname,
                          args.port,
                          args.is_secure)

    print(conn)
    if args.bucketname:
        bname = args.bucketname
    else:
        bname = 'stressos-' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
    bucket = conn.lookup(bname)
    if bucket:
        for key in bucket.list():
            print(key.size, key.last_modified, key.name)
    else:
        bucket = conn.create_bucket(bname)
        print("Created: {}".format(bucket))


if __name__ == '__main__':
    main()
