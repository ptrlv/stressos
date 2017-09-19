import random
import string
import boto
import boto.s3.connection
from boto.s3.key import Key
import os

"""
Bucket related unit tests
"""

#access_key = ''
#secret_key = ''
#host_base = 'storage.datacentred.io'
#host_port = 443
#secure = True

#access_key = ''
#secret_key = ''
#host_base = 'cs3.cern.ch'
#host_port = 443
#secure = True

#access_key = ''
#secret_key = ''
#host_base = 'ceph-s3.mwt2.org'
#host_port = 80
#secure = False

#access_key = ''
#secret_key = ''
#host_base = 'cephgw.usatlas.bnl.gov'
#host_port = 8443
#secure = False

access_key = ''
secret_key = ''
host_base = 's3.echo.stfc.ac.uk'
host_port = 443
secure = True

conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host_base,
        port = host_port,
        is_secure = secure,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

print(conn)

bname = 'plove-bkt-' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))

## test unit
bucket = conn.create_bucket(bname)
print(bucket)
#
## test unit
k = Key(bucket)
kname = 'plove-key-' + ''.join(random.choice(string.ascii_lowercase) for i in range(6))
k.key = kname
k.set_contents_from_string(urandom(2000000))


# test unit
# safe because exception raised if the bucket is not empty
#conn.delete_bucket(bname)

buckets = conn.get_all_buckets() 

print('###')
for bucket in buckets:
    print(bucket.name)

