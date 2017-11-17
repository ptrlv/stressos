from __future__ import print_function
import argparse
import random
import string

import boto
from boto.s3.connection import S3Connection

"""
Check boto connection to s3
Authors:
p.love@lancaster.ac.uk
"""

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", dest="access_key", help="access key")
parser.add_argument("-s", "--secret", dest="secret_key", help="access secret")
parser.add_argument("-d", "--hostname", dest="hostname", help="hostname of endpoint")
parser.add_argument("-c", "--secure", dest="is_secure", action="store_true", help="use https")
parser.add_argument("-p", "--port", dest="port", type=int, default=443, help="port number")

args = parser.parse_args()

def get_connection(access_key, secret_key, host, port, is_secure):
    
    conn = S3Connection(
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
    print(conn.get_path())
    buckets = conn.get_all_buckets()
    print(*buckets, sep='\n')

if __name__ == '__main__':
    main()
