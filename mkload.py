from __future__ import print_function
import argparse
import glob
import os
import random
import socket
import time
import datetime
import multiprocessing
import logging
import logging.handlers
import sys
import hashlib
import shutil

import boto
import boto.s3.connection
from boto.s3.key import Key

from queue import Queue
from threading import Thread

"""
Multithreaded script to provide PUT load onto objectstores.

Authors:
benjamin@phy.duke.edu
p.love@lancaster.ac.uk
"""

parser = argparse.ArgumentParser()
parser.add_argument("source_file")
parser.add_argument("-k", "--key", dest="access_key", help="access key")
parser.add_argument("-s", "--secret", dest="secret_key", help="access secret")
parser.add_argument("-n", "--nthreads", dest="nthreads", type=int, help="number of threads")
parser.add_argument("-d", "--hostbase", dest="hostbase", help="hostname of endpoint")
parser.add_argument("-t", "--duration", type=int, dest="duration", help="duration of test")
parser.add_argument("-b", "--bucket", dest="bucket_name", help="name of target bucket")
parser.add_argument("-c", "--secure", dest="is_secure", action="store_true", help="use https")
parser.add_argument("-p", "--port", dest="port", type=int, default=443, help="port number")
parser.add_argument("--debug", action="store_true", help="debug messages")

args = parser.parse_args()

class Worker(Thread):
    global logger
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = False
        self.start()
    
    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try: 
                func(*args, **kargs)
            except Exception as e:
                logger.info("%s" %(str(e)))
            self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

def eprint(*args, **kwargs):
    timestamp=datetime.datetime.today().strftime('[%Y-%m-%d %H:%M:%S] ')
    print(timestamp,*args, file=sys.stderr, **kwargs)

print('port: %d' % (args.port))
print('bucket_name: %s' % (args.bucket_name))
print('is_secure: %r' % (args.is_secure))

submit_host = socket.gethostname()
submit_host = submit_host.split(".")[0]
print("Submit host: ", submit_host)
print("Remote host: ", args.hostbase)

time_start = time.time()
time_end = time.time() + args.duration

LOG_FILENAME = '/tmp/multiprocessing_cephs3_test_%s_%s.log' %(submit_host,args.hostbase)


#function to connect and write to Ceph OS
def write_thread(conn, dest_host, src_file, keyname):
    global submit_host
    global time_end    
    global logger

    ret_code=True

    try:
        bucket = conn.get_bucket(args.bucket_name)
        try:
            key = Key(bucket)
            key.key = '%s_%s' %(hashlib.md5(keyname.encode('utf-8')).hexdigest()[0:15],keyname)
            key.md5 = "ea7a25c839be547c6bd964e015671453"
            key.set_metadata("md5", "ea7a25c839be547c6bd964e015671453")
            # time the write
            start=datetime.datetime.now()
            key.set_contents_from_filename(src_file)
            stop=datetime.datetime.now()
            #
            elapsed_time_string=stop-start
            elapsed_time=float(elapsed_time_string.seconds)+float(elapsed_time_string.microseconds)/1000000.
            timestamp=start.strftime('[%Y-%m-%d %H:%M:%S.%f] ')
            logger.info("Host - %s write to bucket %s elapsed time - %.3f sec at %s" %(dest_host,args.bucket_name,elapsed_time,timestamp))
        except Exception as e:
#            timestamp=start.strftime('[%Y-%m-%d %H:%M:%S.%f] ')
#            logger.info("Host - %s start write to bucket %s at %s" %(dest_host,args.bucket_name,timestamp))
            logger.info("Thread Exception (write object) %s" %(str(e)))
            ret_code = False
    except Exception as e:
        logger.info("Thread Exception (get_bucket) %s" %(str(e)))
        ret_code = False
    return ret_code


def test_loop_func(dest_host, src_file, keyname):
    global logger
    global time_end
    global site

    # removed balanced_host stuff
    new_host = dest_host
    # writing loop
    iloop=0
    while (time.time() < time_end):
        try:
            #create the connection to the S3 server
            conn = boto.connect_s3(
                aws_access_key_id = args.access_key,
                aws_secret_access_key = args.secret_key,
                host = new_host,
                port = args.port,
                is_secure = args.is_secure,           # uncommmnt if you are not using ssl
                calling_format = boto.s3.connection.OrdinaryCallingFormat(),
                )
            logger.info("Make connection to remote host %s" %(new_host))
            
            newkeyname="%s_%s" %(keyname,str(iloop))
            logger.debug("Writing file: %s to Object %s" %(src_file,newkeyname))
            # write to Object store
            ret_code = write_thread(conn, new_host, src_file, newkeyname)
            if ret_code :
                iloop += 1
            else :
                logger.debug("Writing to OS failed end thread")
                #break
            time.sleep(15)
            # close the connection
            conn.close()
        except Exception as e:
            logger.info("Thread Exception (boto.connect_s3) %s %s" %(new_host,str(e)))
    logger.info("Host - %s number of writes to OS %d" %(new_host,(iloop+1)))


def worker(num, hostname, submit_host, src_file, num_threads):
    global logger
    name = multiprocessing.current_process().name
    logger.info('Starting: %s', multiprocessing.current_process().name)
    thread_id = 0
    threadpools = []
    total_threads=0

    # Init Thread pool with desired number of threads
    logger.info('Initialize ThreadPool - num threads : %d' %(num_threads))
    threadpool = ThreadPool(num_threads)

    for i in range(num_threads):
        logger.debug("Add thread to ThreadPool thread # %d" %(thread_id))
        threadpool.add_task(test_loop_func, hostname, src_file, "write_test_%s_%d_%d" % (submit_host,num,thread_id))
        thread_id += 1
    threadpool.wait_completion()
    sys.stdout.flush()
    sys.stderr.flush()

if __name__ == '__main__':
        
    logger = multiprocessing.get_logger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
    else:
        logger.setLevel(logging.INFO)
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                       maxBytes=0,
                                                       backupCount=10,
                                                       )
        handler.doRollover()

    formatter = logging.Formatter("%(asctime)s - ProdID: %(process)d - ThreadID: %(thread)d  %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    num_processes = multiprocessing.cpu_count() * 4
    num_processes = 1
    
    logger.info('submit host - %s' %(submit_host))
    logger.info('number of subprocesses - %d' %(num_processes))

    jobs = []
    try:
        for i in range(num_processes):
            p = multiprocessing.Process(target=worker, args=(i,args.hostbase,submit_host,args.source_file,args.nthreads))
            jobs.append(p)
            p.start()

        # perhaps wait for the processes to finish
        for p in jobs:
            p.join()
    except Exception as e:
        logger.info("multiprocessing Exception %s" %str(e))
