# stressos

### Environment setup

On MacOS:
```
$ brew install python3
$ pyvenv osenv
$ . osenv/bin/activate
(osenv) $ pip install -r requirements.txt


On Linux:
$ <install python3>
$ python3 -m venv osenv
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

[foobar]
aws_access_key_id = MNOPQRSTUVWXYZ
aws_secret_access_key = ABCDEFGHIJKLMNOPQRSTUVWXYZ
is_secure = True
```

Different profiles may be select using env var or cmdline option:
``` 
$ export AWS_PROFILE=foobar
```

### Basic tests

After activating your virtual environment and credentials try the following tests:

```
# this opens a connection and lists all buckets
$ python chkconn.py -d foobar.example.com -p 443 --profile foobar

# this will list bucket contents or create the bucket if it doesn't exist
$ python chkbucket.py -d foobar.example.com -p 443 --profile foobar foobar-bucket

```


