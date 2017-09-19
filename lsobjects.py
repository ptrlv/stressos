import boto
import boto.s3.connection

"""
Dump all keys in bucket (expensive!)
"""

#access_key = ''
#secret_key = ''
#host_base = 'storage.datacentred.io'
#host_port = 443
#secure = True
#bucket_name = 'atlas-es'

#access_key = ''
#secret_key = ''
#host_base = 'cs3.cern.ch'
#host_port = 443
#secure = True
#bucket_name = 'atlas-eventservice'

#access_key = ''
#secret_key = ''
#host_base = 'ceph-s3.mwt2.org'
#host_port = 80
#secure = False
#bucket_name = 'atlas-eventservice'

access_key = ''
secret_key = ''
host_base = 'cephgw.usatlas.bnl.gov'
host_port = 8443
secure = False
bucket_name = 'atlas_eventservice'

#access_key = ''
#secret_key = ''
#host_base = 's3.echo.stfc.ac.uk'
##host_base = 'ceph-gw1.gridpp.rl.ac.uk'
#host_port = 443
#secure = False
#bucket_name = 'atlas-eventservice'

conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host_base,
        port = host_port,
        is_secure = secure,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

print(conn)

bucket = conn.get_bucket(bucket_name, validate=True)

for key in bucket.list():
    print key.size, key.last_modified, key.name
