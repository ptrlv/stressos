from __future__ import print_function
import glob
import os
import random
import commands
import socket
import time
import datetime
import multiprocessing
import logging
import logging.handlers
import sys
import hashlib
import shutil

from multiprocessing_cephs3_stress_test_tokens import getOS_info

import boto
import boto.s3.connection
from boto.s3.key import Key

from Queue import Queue
from threading import Thread

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


site=sys.argv[1]
#hostname = 'ceph003.usatlas.bnl.gov' 
hostname = sys.argv[2]
time_length = int(sys.argv[3])
num_threads = int(sys.argv[4])
source_file = sys.argv[5]

access_key,secret_key,port,bucket_name,is_secure = getOS_info(site)


eprint('site = %s hostname=%s'%(site,hostname))
eprint('access_key = %s'%(access_key))
eprint('secret_key = %s'%(secret_key))
eprint('port = %d'%(port))
eprint('bucket_name = %s'%(bucket_name))
eprint('is_secure = %r'%(is_secure))

remote_host = hostname.split(".")[0]

balance_hosts = {}
hosts = []
socket_hosts = socket.getaddrinfo(hostname, port)
#print socket_hosts 
for socket_host in socket_hosts:
    if socket_host[4][0] not in hosts and not ':' in socket_host[4][0]:
        hosts.append(socket_host[4][0])
if hosts:
    balance_hosts[hostname] = hosts

eprint(balance_hosts)

#submit_host = socket.getfqdn()
submit_host = socket.gethostname()
submit_host = submit_host.split(".")[0]
eprint("Submit host - ",submit_host)
eprint("Remote host - ",remote_host)

time_start = time.time()
time_end = time.time() + time_length


LOG_FILENAME = '/dev/shm/multiprocessing_cephs3_test_%s_%s.log' %(submit_host,remote_host)


#function to connect and write to Ceph OS

def write_thread(conn,dest_host, src_file, keyname):
    global submit_host
    global time_end    
    global logger
    global bucket_name
    #print 'submit host - %s , ending time - %d' %(submit_host,time_end)

    ret_code=True

    # get bucket
    try:
        bucket = conn.get_bucket(bucket_name)
        #upload
        try:
            key = Key(bucket)
            key.key = '%s_%s' %(hashlib.md5(keyname).hexdigest()[0:15],keyname)
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
            logger.info("Host - %s write to bucket %s elapsed time - %.3f sec at %s" %(dest_host,bucket_name,elapsed_time,timestamp))
        except Exception as e:
            timestamp=start.strftime('[%Y-%m-%d %H:%M:%S.%f] ')
            logger.info("Host - %s start write to bucket %s at %s" %(dest_host,bucket_name,timestamp))
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

    new_host = None
    if not site == "OSiRIS" :
        if balance_hosts and dest_host in balance_hosts and balance_hosts[dest_host]:
            new_host = random.choice(balance_hosts[dest_host])

    if not new_host:
        new_host = dest_host
    # writing loop
    iloop=0
    while (time.time() < time_end):
        try:
            #create the connection to the S3 server
            conn = boto.connect_s3(
                aws_access_key_id = access_key,
                aws_secret_access_key = secret_key,
                host = new_host,
                port = port,
                is_secure=is_secure,           # uncommmnt if you are not using ssl
                calling_format = boto.s3.connection.OrdinaryCallingFormat(),
                )
            logger.info("Make connection to remote host %s" %(new_host))
            
            newkeyname="%s_%s" %(keyname,str(iloop))
            logger.debug("Writing file: %s to Object %s" %(src_file,newkeyname))
            # write to Object store
            ret_code = write_thread(conn,new_host, src_file, newkeyname)
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






def worker(num,hostname,submit_host,src_file,num_threads):
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
    # test the number of arguements passed to the program if less than 5 quit
    if len(sys.argv) < 5 :
        message = "Error too few arguements passed - %s <OS site name> <Remote OS hostname> <length of time for test to run in sec> <number of threads to use> <name of input file>" %(sys.argv[0])
        logger.info(message)
        try:
            raise Exception()
        except:
            eprint(message)
            sys.exit(3)
       
        
    #multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                   maxBytes=0,
                                                   backupCount=10,
                                                   )
    handler.doRollover()
    formatter = logging.Formatter("%(asctime)s - ProdID: %(process)d - ThreadID: %(thread)d  %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    num_processes = multiprocessing.cpu_count() * 4
    
    logger.info('python %s %s %s %s %s %s' %(sys.argv[0],sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]))
    logger.info('submit host - %s' %(submit_host))
    logger.info('remote hosts - %s' %(str(balance_hosts)))
    logger.info('Number of subprocesses - %d' %(num_processes))

    source_file_in_mem='/dev/shm/%s.object_file'%(submit_host)
    try:
        # first copy to source file to shared memory device /dev/shm
        shutil.copy2(source_file,source_file_in_mem)
        logger.info("Host - %s copy file %s to %s " %(submit_host,source_file,source_file_in_mem))
        jobs = []
        try:
            for i in range(num_processes):
                p = multiprocessing.Process(target=worker, args=(i,hostname,submit_host,source_file_in_mem,num_threads))
                jobs.append(p)
                p.start()

            # perhaps wait for the processes to finish
            for p in jobs:
                p.join()
        except Exception as e:
            logger.info("multiprocessing Exception %s" %str(e))
        # remove object file from memory
        try:
            os.remove(source_file_in_mem)
            logger.info("Host - %s removed %s from memory" %(submit_host,source_file_in_mem))
        except Exception as e:
            logger.info("Exception Host - %s cannot remove %s " %(submit_host,source_file_in_mem))
            
    except Exception as e:
        logger.info("Exception Host - %s copy file %s to %s Failed" %(submit_host,source_file,source_file_in_mem))

