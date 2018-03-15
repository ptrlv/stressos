from boto.s3.key import Key
import argparse
from . import realistic
import traceback
import random
from . import common
import sys


"""
This is stub, not at all in a working state.

Populate a bucket with objects following a specified size distribution

Using this code as a starting point: https://github.com/ceph/s3-tests
Authors:
  p.love@lancaster.ac.uk
"""


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bucket', help='name of target bucket')
    parser.add_argument('-m', '--mean', help='mean size of file in bytes')
    parser.add_argument('-s', '--stddev', help='stddev of file in bytes')
    parser.add_argument('-n', '--num', help='number of files')
    parser.add_argument('--seed', dest='seed', help='optional seed for the random number generator')
   
    return parser.parse_args()


def get_strings(mean, stddev, seed=None):
    
    rand = random.Random(seed)

    while True:
        while True:
            size = int(rand.normalvariate(mean, stddev))
            if size >= 0:
                break
        yield ''.join(random.choice(string.ascii_lowercase) for i in range(size))


def gen_objects(n, mean, stddev, seed=None):
    """Make objects with random content and return list of files """


    string_generator = get_strings(mean, stddev, seed)
    return [get_strings.next() for _ in range(n)]


def put_objects(bucket, files, seed):
    """Upload a bunch of files to an S3 bucket
       IN:
         boto S3 bucket object
         list of file handles to upload
         seed for PRNG
       OUT:
         list of boto S3 key objects
    """
    keys = []
    name_generator = realistic.names(15, 4, seed=seed)

    for fp in files:
        print >> sys.stderr, 'sending file with size %dB' % fp.size
        key = Key(bucket)
        key.key = name_generator.next()
        key.set_contents_from_file(fp, rewind=True)
        key.set_acl('public-read')
        keys.append(key)

    return keys


def main():
    args = getargs()
    #SETUP
    random.seed(options.seed if options.seed else None)
    conn = common.s3.main

    if options.outfile:
        OUTFILE = open(options.outfile, 'w')
    elif common.config.file_generation.url_file:
        OUTFILE = open(common.config.file_generation.url_file, 'w')
    else:
        OUTFILE = sys.stdout

    if options.bucket:
        bucket = conn.create_bucket(options.bucket)
    else:
        bucket = common.get_new_bucket()

#    bucket.set_acl('public-read')
    keys = []
    print >> OUTFILE, 'bucket: %s' % bucket.name
    print >> sys.stderr, 'setup complete, generating files'
    seed = random.random()
    files = get_random_files(args.num, args.mean, args.stddev, seed)
    keys += upload_objects(bucket, files, seed)

    print >> sys.stderr, 'finished sending files. generating urls'
    for key in keys:
        print >> OUTFILE, key.generate_url(0, query_auth=False)

    print >> sys.stderr, 'done'



if __name__ == '__main__':
    main()
