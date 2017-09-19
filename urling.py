import boto
import boto.s3.connection
#access_key = ''
#secret_key = ''
#host_base = 'cephgw-test.usatlas.bnl.gov'

"""
Test temporary URL generation
"""

access_key = ''
secret_key = ''
host_base = 'storage.datacentred.io'

conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host_base,
        is_secure = True,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )

print(conn)

bucket_name = 'temp123'
s3_key = 'tempfile123'
temp_url = conn.generate_url(300, 'PUT', bucket_name, s3_key)
print(temp_url)
