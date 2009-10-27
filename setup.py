##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
USAGE = open(os.path.join(here, 'src', 'repoze', 'bfg', 'skins', 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='repoze.bfg.skins',
      version = '0.13',
      description='Skin support for BFG.',
      long_description="\n\n".join((README, USAGE, CHANGES)),
      keywords = "zope3 repoze bfg",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['repoze', 'repoze.bfg'],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.component',
                        'zope.configuration',
                        'zope.testing',
                        'repoze.bfg',
                        'chameleon.zpt>=1.1',
                        ],
      include_package_data = True,
      zip_safe = False,
      test_suite="repoze.bfg.skins.tests",
      )
