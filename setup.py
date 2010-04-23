#!/usr/bin/env python

__version__ = "$Revision: 0 $"
# $Source$

from distutils.core import setup

setup(name='beta_pyechonest',
      version='4.0',
      description='Python interface to The Echo Nest APIs.',
      author='Tyler Williams',
      author_email='tyler@echonest.com',
      maintainer='Tyler Williams',
      maintainer_email='tyler@echonest.com',
      url='http://code.google.com/p/pyechonest/',
      download_url='http://code.google.com/p/pyechonest/',
      package_dir={'beta_pyechonest':'src'},
      packages=['beta_pyechonest'],
      requires=['urllib',
                'urllib2',
                'simplejson',
                ]
     )
