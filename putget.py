import boto
import boto.s3.connection
from boto.s3.key import Key
# import numpy as np
import os
import random
import string
import argparse

# np.random.normal()

"""
Put and Get unit tests
"""

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--profile", help="boto credential profile")
parser.add_argument("-k", "--key", dest="accesskey", help="access key")
parser.add_argument("-s", "--secret", dest="secretkey", help="access secret")
parser.add_argument("-j", "--hostname", dest="hostname", help="hostname of endpoint")
args = parser.parse_args()

conn = boto.connect_s3(
        aws_access_key_id = args.accesskey,
        aws_secret_access_key = args.secretkey,
        host = args.hostname,
        is_secure = True,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

print(conn)

bname = 'plove-bkt-' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
bucket = conn.create_bucket(bname)
print(bucket)

# test unit
k = Key(bucket)
kname = 'plove-key-' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
k.key = kname
k.set_contents_from_string(os.urandom(2000000))

k.get_contents_to_filename(k.name)
k.delete()

# test unit
# safe because exception raised if the bucket is not empty
conn.delete_bucket(bname)

