#!/usr/bin/env python
# encoding: utf-8

"""
Copyright (c) 2010 The Echo Nest. All rights reserved.
Created by Tyler Williams on 2010-04-25.

The Song module loosely covers http://beta.developer.echonest.com/song.html
Refer to the official api documentation if you are unsure about something.
"""

import util
from proxies import SongProxy
from results import Result

class Song(SongProxy):
    """
    A Song object
    
    Create a song object like so:
        s = song.Song('SOXZYYG127F3E1B7A2')
    
    Attributes: (**attributes** are guaranteed to exist as soon as an artist object exists)
        **id**: Echo Nest Song ID
        **title**: Song Title
        **artist_name**: Artist Name
        **artist_id**: Artist ID
        audio_summary: An Audio Summary Result object
        song_hotttnesss: A float representing a song's hotttnesss
        artist_hotttnesss: A float representing a song's parent artist's hotttnesss
        artist_familiarity: A float representing a song's parent artist's familiarity
        artist_location: A string specifying a song's parent artist's location
        tracks: A list of track result objects
    
    """
    def __init__(self, id, buckets = None, **kwargs):
        buckets = buckets or []
        super(Song, self).__init__(id, buckets, **kwargs)
    
    def __repr__(self):
        return "<%s - %s>" % (self.type.encode('utf-8'), self.title.encode('utf-8'))
    
    def __str__(self):
        return self.title.encode('utf-8')
    
        
    def get_audio_summary(self, cache=True):
        if not (cache and ('audio_summary' in self.cache)):
            response = self.get_attribute('profile', bucket='audio_summary')
            self.cache['audio_summary'] = response['songs'][0]['audio_summary']
        return Result('audio_summary', self.cache['audio_summary'])
    
    audio_summary = property(get_audio_summary)
    
    def get_song_hotttnesss(self, cache=True):
        if not (cache and ('song_hotttnesss' in self.cache)):
            response = self.get_attribute('profile', bucket='song_hotttnesss')
            self.cache['song_hotttnesss'] = response['songs'][0]['song_hotttnesss']
        return self.cache['song_hotttnesss']
    
    song_hotttnesss = property(get_song_hotttnesss)
    
    def get_artist_hotttnesss(self, cache=True):
        if not (cache and ('artist_hotttnesss' in self.cache)):
            response = self.get_attribute('profile', bucket='artist_hotttnesss')
            self.cache['artist_hotttnesss'] = response['songs'][0]['artist_hotttnesss']
        return self.cache['artist_hotttnesss']
    
    artist_hotttnesss = property(get_artist_hotttnesss)
    
    def get_artist_familiarity(self, cache=True):
        if not (cache and ('artist_familiarity' in self.cache)):
            response = self.get_attribute('profile', bucket='artist_familiarity')
            self.cache['artist_familiarity'] = response['songs'][0]['artist_familiarity']
        return self.cache['artist_familiarity']
    
    artist_familiarity = property(get_artist_familiarity)
    
    def get_artist_location(self, cache=True):
        if not (cache and ('artist_location' in self.cache)):
            response = self.get_attribute('profile', bucket='artist_location')
            self.cache['artist_location'] = response['songs'][0]['artist_location']
        return self.cache['artist_location']
    
    artist_location = property(get_artist_location)
    
    def get_tracks(self, catalog=None, limit=False, cache=True):
        if not (cache and ('tracks' in self.cache)):
            kwargs = {
                'method_name':'profile',
                'bucket':['tracks'],
            }
            if catalog:
                kwargs['bucket'].append('id:%s' % catalog)
            if limit:
                kwargs['limit'] = 'true'
            response = self.get_attribute(**kwargs)
            self.cache['tracks'] = response['songs'][0].get('tracks', [])
        return [Result('track', t) for t in self.cache['tracks']]
    
    tracks = property(get_tracks) 


def search(title=None, artist=None, artist_id=None, combined=None, description=None, results=None, max_tempo=None, \
                min_tempo=None, max_duration=None, min_duration=None, max_loudness=None, min_loudness=None, \
                artist_max_familiarity=None, artist_min_familiarity=None, artist_max_hotttnesss=None, \
                artist_min_hotttnesss=None, song_max_hotttnesss=None, song_min_hotttnesss=None, mode=None, \
                key=None, max_latitude=None, min_latitude=None, max_longitude=None, min_longitude=None, \
                sort=None, buckets=[], limit=False):
    """search for songs"""
    kwargs = {}
    if title:
        kwargs['title'] = title
    if artist:
        kwargs['artist'] = artist
    if artist_id:
        kwargs['artist_id'] = artist_id
    if combined:
        kwargs['combined'] = combined
    if description:
        kwargs['description'] = description
    if results:
        kwargs['results'] = results
    if max_tempo:
        kwargs['max_tempo'] = max_tempo
    if min_tempo:
        kwargs['min_tempo'] = min_tempo
    if max_duration:
        kwargs['max_duration'] = max_duration
    if min_duration:
        kwargs['min_duration'] = min_duration
    if max_loudness:
        kwargs['max_loudness'] = max_loudness
    if min_loudness:
        kwargs['min_loudness'] = min_loudness
    if artist_max_familiarity:
        kwargs['artist_max_familiarity'] = artist_max_familiarity
    if artist_min_familiarity:
        kwargs['artist_min_familiarity'] = artist_min_familiarity
    if artist_max_hotttnesss:
        kwargs['artist_max_hotttnesss'] = artist_max_hotttnesss
    if artist_min_hotttnesss:
        kwargs['artist_min_hotttnesss'] = artist_min_hotttnesss
    if song_max_hotttnesss:
        kwargs['song_max_hotttnesss'] = song_max_hotttnesss
    if song_min_hotttnesss:
        kwargs['song_min_hotttnesss'] = song_min_hotttnesss
    if mode:
        kwargs['mode'] = mode
    if key:
        kwargs['key'] = key
    if max_latitude:
        kwargs['max_latitude'] = max_latitude
    if min_latitude:
        kwargs['min_latitude'] = min_latitude
    if max_longitude:
        kwargs['max_longitude'] = max_longitude
    if min_longitude:
        kwargs['min_longitude'] = min_longitude
    if sort:
        kwargs['sort'] = sort
    if buckets:
        kwargs['bucket'] = buckets
    if limit:
        kwargs['limit'] = 'true'
    
    result = util.callm("%s/%s" % ('song', 'search'), kwargs)
    fix = lambda x : dict((str(k), v) for (k,v) in x.iteritems())
    return [Song(**fix(s_dict)) for s_dict in result['response']['songs']]

def profile(ids, buckets = None, limit=False):
    """get the profiles for multiple songs at once"""

    buckets = buckets or []
    if not isinstance(ids, list):
        ids = [ids]
    kwargs = {}
    kwargs['id'] = ids
    if buckets:
        kwargs['bucket'] = buckets
    if limit:
        kwargs['limit'] = 'true'
    
    result = util.callm("%s/%s" % ('song', 'profile'), kwargs)
    fix = lambda x : dict((str(k), v) for (k,v) in x.iteritems())
    return [Song(**fix(s_dict)) for s_dict in result['response']['songs']]

