#!/usr/bin/env python
# encoding: utf-8

"""
Copyright (c) 2010 The Echo Nest. All rights reserved.
Created by Tyler Williams on 2010-04-25.

Utility functions to support the Echo Nest web API interface.
"""
import urllib
import urllib2
import httplib
import config
import logging
import socket
import re
import time
from hashlib import md5
try:
    import cPickle as pickle
except:
    import pickle

try:
    import json
except ImportError:
    import simplejson as json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TYPENAMES = (
    ('AR', 'artist'),
    ('SO', 'song'),
    ('RE', 'release'),
    ('TR', 'track'),
    ('PE', 'person'),
    ('DE', 'device'),
    ('LI', 'listener'),
    ('ED', 'editor'),
    ('TW', 'tweditor'),
)
foreign_regex = re.compile(r'^.+?:(%s):([^^]+)\^?([0-9\.]+)?' % r'|'.join(n[1] for n in TYPENAMES))
short_regex = re.compile(r'^((%s)[0-9A-Z]{16})\^?([0-9\.]+)?' % r'|'.join(n[0] for n in TYPENAMES))
long_regex = re.compile(r'music://id.echonest.com/.+?/(%s)/(%s)[0-9A-Z]{16}\^?([0-9\.]+)?' % (r'|'.join(n[0] for n in TYPENAMES), r'|'.join(n[0] for n in TYPENAMES)))

class EchoNestAPIError(Exception):
    """
    Generic API errors. 
    """
    def __init__(self, code, message):
        self.code = code
        self._message = message
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return 'Echo Nest API Error %d: %s' % (self.code, self._message)

def verify_successful(response_dict):
    status_dict = response_dict['response']['status']
    code = int(status_dict['code'])
    message = status_dict['message']
    if (code != 0):
        # do some cute exception handling
        raise EchoNestAPIError(code, message)
    del response_dict['response']['status']


def callm(method, param_dict, POST = False, socket_timeout=config.CALL_TIMEOUT, data = None):
    """
    Call the api! 
    Param_dict is a *regular* *python* *dictionary* so if you want to have multi-valued params
    put them in a list.
    
    ** note, if we require 2.6, we can get rid of this timeout munging.
    """
    param_dict['api_key'] = config.ECHO_NEST_API_KEY
    param_list = []
    
    for key,val in param_dict.iteritems():
        if isinstance(val, list):
            param_list.extend( [(key,subval) for subval in val] )
        else:
            if isinstance(val, unicode):
                val = val.encode('utf-8')
            param_list.append( (key,val) )
    params = urllib.urlencode(param_list)
    socket.setdefaulttimeout(socket_timeout)
    tic=time.time()

    if(POST):
        if (not method == 'track/upload') or (param_dict.has_key('url')):
            """
            this is a normal POST call
            """
            url = 'http://%s/%s/%s/%s' % (config.API_HOST, config.API_SELECTOR, config.API_VERSION, method)
            f = urllib.urlopen(url, params)

        else:
            """
            upload with a local file is special, as the body of the request is the content of the file,
            and the other parameters stay on the URL
            """
            url = '/%s/%s/%s?%s' % (config.API_SELECTOR, config.API_VERSION, 
                                        method, params)
            conn = httplib.HTTPConnection(config.API_HOST, port = 80)
            conn.request('POST', url, body = data, headers = {'Content-Type': 'application/octet-stream'})
            f = conn.getresponse()

    else:
        """
        just a normal GET call
        """
        url = 'http://%s/%s/%s/%s?%s' % (config.API_HOST, config.API_SELECTOR, config.API_VERSION, 
                                        method, params)
        f = urllib.urlopen(url)


    toc=time.time()
    socket.setdefaulttimeout(None)
    if config.TRACE_API_CALLS:
        logging.info("%2.2fs : %s" % (toc-tic, url))
    response_dict = json.loads(f.read())
    verify_successful(response_dict)
    return response_dict


def postChunked(host, selector, fields, files):
    """
    Attempt to replace postMultipart() with nearly-identical interface.
    (The files tuple no longer requires the filename, and we only return
    the response body.) 
    Uses the urllib2_file.py originally from 
    http://fabien.seisen.org which was also drawn heavily from 
    http://code.activestate.com/recipes/146306/ .

    This urllib2_file.py is more desirable because of the chunked 
    uploading from a file pointer (no need to read entire file into 
    memory) and the ability to work from behind a proxy (due to its 
    basis on urllib2).
    """
    params = urllib.urlencode(fields)
    url = 'http://%s%s?%s' % (host, selector, params)
    u = urllib2.urlopen(url, files)
    result = u.read()
    [fp.close() for (key, fp) in files]
    return result

class attrdict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

class memoize(object):
    """
        Caches the result of a class method inside the instance.
        big ups to: http://eoyilmaz.blogspot.com/2009/09/python-function-decorators-caching.html
    """
    def __init__(self, method):        
        if not isinstance( method, property ):
            self._method = method
            self._name = method.__name__
            self._isProperty = False
        else:
            self._method = method.fget
            self._name = method.fget.__name__
            self._isProperty = True
        self._obj = None

    def __get__(self, inst, cls):
        self._obj = inst
        if self._isProperty:
            return self.__call__()
        else:
            return self

    def __call__(self, *args, **kwargs):
        print 'args: %s, kwargs %s' % (args, kwargs)
        key = self._name+md5(pickle.dumps(args, 2)).hexdigest()+md5(pickle.dumps(kwargs, 2)).hexdigest()
        print 'key is: %s' % (key,)
        # call the function and store the result as a cache
        if not hasattr(self._obj, key) or getattr(self._obj, key ) == None:
            data = self._method(self._obj, *args, **kwargs )
            setattr( self._obj, key, data )

        return getattr( self._obj, key )

    def __repr__(self):
        """Return the function's representation
        """
        return self._obj.__repr__()

