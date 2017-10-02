#!/usr/bin/python

'''
   Original Author: Ricardo Pascal
   http://voorloopnul.com/blog/a-python-netstat-in-less-than-100-lines-of-code/

   Modified for use in counting cephs3 stress testing
'''


import pwd
import os
import re
import glob
import sys
import logging
import logging.handlers
import socket
import time

PROC_TCP = "/proc/net/tcp"
STATE = {
        '01':'ESTABLISHED',
        '02':'SYN_SENT',
        '03':'SYN_RECV',
        '04':'FIN_WAIT1',
        '05':'FIN_WAIT2',
        '06':'TIME_WAIT',
        '07':'CLOSE',
        '08':'CLOSE_WAIT',
        '09':'LAST_ACK',
        '0A':'LISTEN',
        '0B':'CLOSING'
        }

def _load():
    ''' Read the table of tcp connections & remove header  '''
    with open(PROC_TCP,'r') as f:
        content = f.readlines()
        content.pop(0)
    return content

def _hex2dec(s):
    return str(int(s,16))

def _ip(s):
    ip = [(_hex2dec(s[6:8])),(_hex2dec(s[4:6])),(_hex2dec(s[2:4])),(_hex2dec(s[0:2]))]
    return '.'.join(ip)

def _remove_empty(array):
    return [x for x in array if x !='']

def _convert_ip_port(array):
    host,port = array.split(':')
    return _ip(host),_hex2dec(port)

def netstat(hostslist):
    '''
    Function to return a list with status of tcp connections at linux systems
    To get pid of all network process running on system, you must run this script
    as superuser
    '''
    global logger

    logger.debug("hostslist %s " %(hostslist))
    content=_load()
    result = {}
    # initialize totals 
    for state in STATE.values():
        logger.debug("state %s " %(state))
        result[state] = 0

    for line in content:
        line_array = _remove_empty(line.split(' '))     # Split lines and remove empty spaces.
        l_host,l_port = _convert_ip_port(line_array[1]) # Convert ipaddress and port from hex to decimal.
        r_host,r_port = _convert_ip_port(line_array[2]) 
        r_host_port = r_host + ":" + r_port
        # test if this connection is to remote host and port
        logger.debug("remote host:remote port %s " %(r_host_port))
        if r_host_port in hostslist :
            tcp_id = line_array[0]
            state = STATE[line_array[3]]
            
            #uid = pwd.getpwuid(int(line_array[7]))[0]       # Get user from UID.
            #inode = line_array[9]                           # Need the inode to get process pid.
            #pid = _get_pid_of_inode(inode)                  # Get pid prom inode.
            #try:                                            # try read the process name.
            #    exe = os.readlink('/proc/'+pid+'/exe')
            #except:
            #    exe = None

            #nline = [tcp_id, uid, l_host+':'+l_port, r_host+':'+r_port, state, pid, exe]
            result[state] += 1
    return result

def _get_pid_of_inode(inode):
    '''
    To retrieve the process pid, check every running process and look for one using
    the given inode.
    '''
    for item in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if re.search(inode,os.readlink(item)):
                return item.split('/')[2]
        except:
            pass
    return None

if __name__ == '__main__':
    # input parameters  1) length of time for test  2) remote host to check
    # test the number of arguements passed to the program if less than 3 quit                                                                                                            
    if len(sys.argv) < 3 :
        message = "Error too few arguements passed - %s < length of time for test> <remote host> <port>" %(sys.argv[0])
        logger.info(message)
        try:
            raise Exception()
        except:
            eprint(message)
            sys.exit(3)

    lengthoftest = int(sys.argv[1])
    remotehost = sys.argv[2]
    remoteport = sys.argv[3]

    # sort out host names
    remote_host_shortname = remotehost.split(".")[0]

    balance_hosts = {}
    hosts = []
    hostslist = []
    socket_hosts = socket.getaddrinfo(remotehost, remoteport)

    for socket_host in socket_hosts:
        if socket_host[4][0] not in hosts and not ':' in socket_host[4][0]:
            hosts.append(socket_host[4][0])
    if hosts:
        balance_hosts[remotehost] = hosts

    for host in balance_hosts[remotehost]:
        hostslist.append("%s:%s" %(host,remoteport))

    submit_host = socket.gethostname()
    submit_host = submit_host.split(".")[0]


    # setup for logging
    LOG_FILENAME='multiprocessing_cephs3_tcp_connections_%s_%s.log' %(submit_host,remote_host_shortname)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # Add the log message handler to the logger                                                                                                                                          
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                   maxBytes=0,
                                                   backupCount=10,
                                                   )
    handler.doRollover()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    logger.info("./netstat.py %d %s" %( lengthoftest, remotehost))
    logger.debug("hostslist - %s" %(hostslist))

    time_start = time.time()
    time_end = time.time() + lengthoftest

    # start timer loop checking every second (sleep 1 seconds between checks)
    while (time.time() < time_end):
        # loop over the possible states
        result = netstat(hostslist)
        message = "Ncon to %s " %(remote_host_shortname)
        for state in STATE.values():
            message = message + "(%s)= %d " %(state,result[state])
        logger.info(" %s " %(message))
        time.sleep(1)

    message = "Ncon to %s " %(remote_host_shortname)
    for state in STATE.values():
        message = message + "(%s)= %d " %(state,result[state])
    logger.info(" %s " %(message))


