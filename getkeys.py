#!/usr/bin/env python3
import os
import requests
import urllib
import urllib3

"""
Retrieve object store keys from panda server
"""

def getSSLCertificate():
    """ Return the path to the SSL certificate """ 

    if 'X509_USER_PROXY' in os.environ:
        sslCertificate = os.environ['X509_USER_PROXY']
    else:
        sslCertificate  = '/tmp/x509up_u%s' % str(os.getuid())

    return sslCertificate

def getKeys(node):
    urllib3.disable_warnings()
    r = requests.post('https://%s%s' % (host, path),
                                  verify=False,
                                  cert=(sslCert, sslKey),
                                  data=urllib.parse.urlencode(node),
                                  timeout=60)
    if r and r.status_code == 200:
        print(r.text)


sslCert = getSSLCertificate()
sslKey = sslCert
host = 'pandaserver.cern.ch:25443'
path = '/server/panda/getKeyPair'

node={}
node['privateKeyName'] = 'LANCS_ObjectStoreKey'
node['publicKeyName'] = 'LANCS_ObjectStoreKey.pub'
#node['privateKeyName'] = 'BNL_ObjectStoreKey'
#node['publicKeyName'] = 'BNL_ObjectStoreKey.pub'
#node['privateKeyName'] = 'RAL_ObjectStoreKey'
#node['publicKeyName'] = 'RAL_ObjectStoreKey.pub'
#node['privateKeyName'] = 'CERN_ObjectStoreKey'
#node['publicKeyName'] = 'CERN_ObjectStoreKey.pub'
#node['privateKeyName'] = 'MWT2_ObjectStoreKey'
#node['publicKeyName'] = 'MWT2_ObjectStoreKey.pub'
node['privateKeyName'] = 'AGLT2_ObjectStoreKey'
node['publicKeyName'] = 'AGLT2_ObjectStoreKey.pub'

getKeys(node)
