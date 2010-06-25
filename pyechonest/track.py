#!/usr/bin/env python
# encoding: utf-8

"""
Copyright (c) 2010 The Echo Nest. All rights reserved.
Created by Reid Draper on 2010-06-15.

The Track module loosely covers http://beta.developer.echonest.com/track.html
Refer to the official api documentation if you are unsure about something.
"""

import urllib2
try:
    import json
except ImportError:
    import simplejson as json

from proxies import TrackProxy
import util

class Track(TrackProxy):
    def __repr__(self):
        return "<%s - %s>" % (self.type.encode('utf-8'), self.title.encode('utf-8'))
    
    def __str__(self):
        return self.title.encode('utf-8')

def _track_from_response(response):
    """
    This is the function that actually creates the track object
    """
    result = response['response']
    status = result['track']['status'].lower()
    if not status == 'complete':
        """
        pyechonest only supports wait = true for now, so this should not be pending
        """
        if status == 'error':
            raise Exception('there was an error analyzing the track')
        if status == 'pending':
            raise Exception('the track is still being analyzed')
    else:
        track = result['track']
        identifier      = track.pop('id') 
        md5             = track.pop('md5')
        audio_summary   = track.pop('audio_summary')
        json_url        = audio_summary['analysis_url']
        json_string     = urllib2.urlopen(json_url).read()
        analysis        = json.loads(json_string)
        track.update(analysis)
        return Track(identifier, md5, track)

def _upload(param_dict, data = None):
    """
    Calls upload either with a local audio file,
    or a url. Returns a track object.
    """
    param_dict['format'] = 'json'
    param_dict['wait'] = 'true'
    param_dict['bucket'] = 'audio_summary'
    result = util.callm('track/upload', param_dict, POST = True, socket_timeout = 300,  data = data) 
    return _track_from_response(result)

def _profile(param_dict):
    param_dict['format'] = 'json'
    param_dict['bucket'] = 'audio_summary'
    result = util.callm('track/profile', param_dict)
    return _track_from_response(result)

def _analyze(param_dict):
    param_dict['format'] = 'json'
    param_dict['bucket'] = 'audio_summary'
    param_dict['wait'] = 'true'
    result = util.callm('track/analyze', param_dict, POST = True, socket_timeout = 300)
    return _track_from_response(result)
    

""" Below are convenience functions for creating Track objects, you should use them """

def track_from_string(audio_data, filetype):
    param_dict = {}
    param_dict['filetype'] = filetype 
    return _upload(param_dict, data = audio_data)

def track_from_file(file_object, filetype):
    return track_from_string(file_object.read(), filetype)

def track_from_filename(filename, filetype = None):
    """
    if the filetype is none, we will get it from the extension
    """
    filetype = filetype or filename.split('.')[-1]
    return track_from_file(open(filename), filetype)

def track_from_url(url):
    param_dict = dict(url = url)
    return _upload(param_dict) 
     
def track_from_id(identifier):
    param_dict = dict(id = identifier)
    return _profile(param_dict)

def track_from_md5(md5):
    param_dict = dict(md5 = md5)
    return _profile(param_dict)

def track_from_reanalyzing_id(identifier):
    param_dict = dict(id = identifier)
    return _analyze(param_dict)

def track_from_reanalyzing_md5(md5):
    param_dict = dict(md5 = md5)
    return _analyze(param_dict)
