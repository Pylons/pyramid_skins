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
README = open(os.path.join(here, 'README.rst'), 'rb').read()
CHANGES = open(os.path.join(here, 'CHANGES.txt'), 'rb').read()

long_description = b"\n\n".join((README, CHANGES))
long_description = long_description.decode('utf-8')

requires = [
    'setuptools',
    'Chameleon >= 2.7',
    'zope.interface',
    'pyramid >= 1.5',
    ]

docs_extras = [
    'Sphinx',
    'docutils',
    'repoze.sphinx.autointerface']

testing_extras = [
    'MacFSEvents;sys_platform=="darwin"',
    'manuel',
    'coverage',
    'nose2',
    'pyinotify;sys_platform=="linux"',
    'pyramid_zcml >= 0.9.2',
    'zope.testing>3.8.7',
    'zope.component>3.9.2']

setup(name='pyramid_skins',
      version = '3.0',
      description='Templating framework for Pyramid.',
      long_description=long_description,
      keywords = "pyramid templates",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3 :: Only',
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
      python_requires=">=3.7",
      namespace_packages=[],
      include_package_data = True,
      zip_safe = False,
      install_requires=requires,
      tests_require=testing_extras,
      extras_require={
          'testing': testing_extras,
          'docs': docs_extras,
          'development': testing_extras + docs_extras},
      test_suite="pyramid_skins.tests",
      )
