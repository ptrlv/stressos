# stressos

### Environment setup

On MacOS:
```
$ brew install python3
$ pyvenv osenv
$ . osenv/bin/activate
(osenv) $ pip install -r requirements.txt


On Linux:
$ <install latest python3.6>
$ python3.6 -m venv osenv
$ . osenv/bin/activate
(osenv) $ pip install -r requirements.txt
```

### Credentials

When running interactively credentials may be stored in the following file:
```
$ cat ~/.aws/credentials
[default]
aws_access_key_id = ABCDEFGHIJKLM
aws_secret_access_key = ABCDEFGHIJKLMNOPQRSTUVWXYZ

[lancs]
aws_access_key_id = MNOPQRSTUVWXYZ
aws_secret_access_key = ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

Different profiles may be select using env var:
``` 
$ export AWS_PROFILE=lancs
```

### Basic tests

After activating your virtual environment and credentials try the following tests:

```
# this opens a connection and lists all buckets
$ python chkconn.py --secure -d s3.example.com -p 443

# this will list bucket contents or create the bucket if it doesn't exist
$ python chkbucket.py --secure -d s3.example.com -p 443 foobar-bucket

```


