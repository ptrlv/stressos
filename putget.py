import boto
import boto.s3.connection
from boto.s3.key import Key
import numpy as np
import os
import random
import string
# np.random.normal()

"""
Put and Get unit tests
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
#secure = True

access_key = ''
secret_key = ''
host_base = 's3.echo.stfc.ac.uk'
#host_base = 'ceph-gw1.gridpp.rl.ac.uk'
host_port = 443
secure = True

conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host_base,
        is_secure = secure,
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

