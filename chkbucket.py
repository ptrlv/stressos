from __future__ import print_function
import argparse
import boto
import boto.s3.connection
import random
import string


"""
Check content of bucket, create if doesn't exist
Authors:
p.love@lancaster.ac.uk
"""

parser = argparse.ArgumentParser(description='Check content of bucket, create if doesn\'t exist')
parser.add_argument('-k', '--key', dest='access_key', help='access key')
parser.add_argument('-s', '--secret', dest='secret_key', help='access secret')
parser.add_argument('-d', '--hostname', dest='hostname', default='localhost', help='hostname of endpoint')
parser.add_argument('-c', '--secure', dest='is_secure', action='store_true', help='use https')
parser.add_argument('-p', '--port', dest='port', type=int, default=443, help='port number')
parser.add_argument('bucketname', help='name of bucket to list or create')

args = parser.parse_args()

def get_connection(access_key, secret_key, host, port, is_secure):
    conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host,
        port = port,
        is_secure = is_secure,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
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
        bname = 'plove-bkt-' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
    bucket = conn.lookup(bname)
    print(bucket)
    if bucket:
        for key in bucket.list():
            print(key.size, key.last_modified, key.name)
    else:
        print(conn.create_bucket(bname))
        


if __name__ == '__main__':
    main()
