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
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

long_description = "\n\n".join((README, CHANGES))
long_description = long_description.decode('utf-8')

install_requires =[
    'setuptools',
    'Chameleon >= 2.7',
    'zope.interface',
    'zope.component',
    'zope.configuration',
    'zope.testing',
    'pyramid >= 1.4',
    'pyramid_zcml >= 0.9.2',
    ]

tests_require = []

if sys.platform == "darwin":
    tests_require.append("MacFSEvents")

if sys.platform.startswith("linux"):
    tests_require.append("pyinotify")

tests_require = install_requires + [
    'manuel',
    'zope.testing>3.8.7',
    'zope.component>3.9.2',
    ] + tests_require

setup(name='pyramid_skins',
      version = '1.1',
      description='Templating framework for Pyramid.',
      long_description=long_description,
      keywords = "pyramid templates",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: BFG'],
      license='BSD',
      author='Malthe Borch and the Pylons Community',
      author_email='pylons-discuss@googlegroups.org',
      maintainer='Malthe Borch',
      maintainer_email='mborch@gmail.com',
      url='http://packages.python.org/pyramid_skins/',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=[],
      include_package_data = True,
      zip_safe = False,
      install_requires=install_requires,
      tests_require = tests_require,
      extras_require = {
        'tests': [dep.split('==')[0] for dep in tests_require],
          },
      test_suite="pyramid_skins.tests",
      )
