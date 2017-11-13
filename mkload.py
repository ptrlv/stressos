from __future__ import print_function
import argparse
#import random
import socket
import time
import datetime
import multiprocessing
import logging
import logging.handlers
import sys
import hashlib

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
parser.add_argument("-d", "--hostname", dest="hostname", help="hostname of endpoint")
parser.add_argument("-t", "--duration", type=int, dest="duration", help="duration of test")
parser.add_argument("-b", "--bucket", help="name of target bucket")
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

#function to connect and write to Ceph OS
def write_thread(conn, bucket, dest_host, src_file, keyname):
    global time_end    
    global logger

    ret_code = True

    try:
        try:
            key = Key(bucket)
            key.key = '%s_%s' %(hashlib.md5(keyname.encode('utf-8')).hexdigest()[0:15],keyname)
#rucio?            key.md5 = "ea7a25c839be547c6bd964e015671453"
#rucio?            key.set_metadata("md5", "ea7a25c839be547c6bd964e015671453")

            start = datetime.datetime.now()
            key.set_contents_from_filename(src_file)
            stop = datetime.datetime.now()

            elapsed_time_string=stop-start
            elapsed_time=float(elapsed_time_string.seconds)+float(elapsed_time_string.microseconds)/1000000.
            timestamp=start.strftime('[%Y-%m-%d %H:%M:%S.%f] ')
            logger.info("Host - %s write to bucket %s elapsed time - %.3f sec at %s" %(dest_host,bucket,elapsed_time,timestamp))
            stamp = datetime.datetime.timestamp(start)
            msg = '{},{},{},{}'.format(stamp, dest_host, key.size, elapsed_time)
            print(msg)
        except Exception as e:
            logger.info("Thread Exception (write object) %s" %(str(e)))
            ret_code = False
    except Exception as e:
        logger.info("Thread Exception (get_bucket) %s" %(str(e)))
        ret_code = False
    return ret_code


def get_connection(access_key, secret_key, host, port, is_secure):
    
    #create the connection to the S3 server
    conn = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        host = host,
        port = port,
        is_secure = is_secure,
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )
    logger.info("Make connection to remote host %s" %(host))
    
    return conn

def stress_loop_func(conn, bucket, dest_host, src_file, keyname):
    global logger
    global time_end
    global site

    # removed balanced_host stuff
    new_host = dest_host
    # writing loop
    iloop=0
    while (time.time() < time_end):
        try:
            newkeyname="%s_%s" %(keyname,str(iloop))
            logger.debug("Writing file: %s to Object %s" %(src_file,newkeyname))
            # write to Object store
            ret_code = write_thread(conn, bucket, new_host, src_file, newkeyname)
            if ret_code :
                iloop += 1
            else :
                logger.debug("Writing to OS failed end thread")
                #break
            time.sleep(5)
            # close the connection
            conn.close()
        except Exception as e:
            logger.info("Thread Exception (boto.connect_s3) %s %s" %(new_host,str(e)))
    logger.info("Host - %s number of writes to OS %d" %(new_host,(iloop+1)))


def worker(i, hostname, submit_host, src_file, nthreads):
    global logger
    name = multiprocessing.current_process().name
    logger.info('Starting: %s', multiprocessing.current_process().name)
    thread_id = 0
    threadpools = []
    total_threads=0

    # Init Thread pool with desired number of threads
    logger.info('Initialize ThreadPool - num threads : %d' %(nthreads))
    threadpool = ThreadPool(nthreads)

    conn = get_connection(args.access_key,
                          args.secret_key,
                          args.hostname,
                          args.port,
                          args.is_secure)

    bucket = conn.get_bucket(args.bucket)

    for i in range(nthreads):
        logger.debug("Add thread to ThreadPool thread # %d" %(thread_id))
        threadpool.add_task(stress_loop_func, conn, bucket, hostname, src_file, "write_test_%s_%d_%d" % (submit_host,i,thread_id))
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
    
    submit_host = socket.gethostname()
    submit_host = submit_host.split(".")[0]

    time_start = time.time()
    time_end = time.time() + args.duration

    LOG_FILENAME = '/tmp/multiprocessing_cephs3_test_%s_%s.log' %(submit_host,args.hostname)

    logger.info('submit host - %s' %(submit_host))
    logger.info('number of subprocesses - %d' %(num_processes))

    jobs = []
    try:
        for i in range(num_processes):
            p = multiprocessing.Process(target=worker, args=(i,args.hostname,submit_host,args.source_file,args.nthreads))
            jobs.append(p)
            p.start()

        for p in jobs:
            p.join()

    except Exception as e:
        logger.info("multiprocessing Exception %s" %str(e))

"""
siege.log
      Date & Time,  Trans,  Elap Time,  Data Trans,  Resp Time,  Trans Rate,  Throughput,  Concurrent,    OKAY,   Failed
2017-10-17 12:48:45,    615,       5.00,          10,       0.20,      123.00,        2.00,       24.18,     615,       0
2017-10-17 13:43:33,   3508,       4.18,         194,       0.03,      839.23,       46.41,       24.57,    3508,       0
2017-10-17 13:57:56,  40359,     676.03,        2247,       0.01,       59.70,        3.32,        0.67,   40359,       0
"""
