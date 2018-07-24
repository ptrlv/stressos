import boto
import boto.s3.connection

"""
Dump all keys in bucket (expensive!)
"""

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
