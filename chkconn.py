from __future__ import print_function
import argparse

import boto
import boto.s3.connection

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
    
    #create the connection to the S3 server
    conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host,
        port = port,
        is_secure = is_secure,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )
    print('Make connection to remote host {}'.format(host))
    
    return conn


def main():
    conn = get_connection(args.access_key,
                          args.secret_key,
                          args.hostname,
                          args.port,
                          args.is_secure)

    print(conn)
    print(conn.get_path())

if __name__ == '__main__':
    main()
