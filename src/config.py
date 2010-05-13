#!/usr/bin/env python
# encoding: utf-8

"""
Copyright (c) 2010 The Echo Nest. All rights reserved.
Created by Tyler Williams on 2010-04-25.

Global configuration variables for accessing the Echo Nest web API.
"""

__version__ = "$Revision: 4.1 $"
# $Source$

import os

if('ECHO_NEST_API_KEY' in os.environ):
    ECHO_NEST_API_KEY = os.environ['ECHO_NEST_API_KEY']
else:
    ECHO_NEST_API_KEY = None


API_HOST = 'beta.developer.echonest.com'

API_SELECTOR = 'api'

API_VERSION = 'v4'

HTTP_USER_AGENT = 'BETA_PyENAPI'

MP3_BITRATE = 128

CACHE = True
"""
You may change this to False to prevent local caching
of API results.
"""

TRACE_API_CALLS = False
"""
If true, API calls will be traced to the console
"""

ANALYSIS_VERSION = 3
"""
Analysis version
"""
