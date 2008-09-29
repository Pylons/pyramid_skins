import os

import zope.interface
import zope.component
import zope.testing

import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component
import zope.component.testing
import zope.configuration.xmlconfig

import repoze.bfg.skins

import chameleon.zpt

def setUp(suite):
    zope.component.testing.setUp(suite)
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', chameleon.zpt)()

skins_path = repoze.bfg.skins.__path__[0]
new_template_path = os.path.join(skins_path, "tests", "templates", "new.pt")

def tearDown(suite):
    try:
        os.unlink(new_template_path)
    except OSError:
        pass
    zope.component.testing.tearDown(suite)

def test_suite():
    doctests = ("zcml.txt",)
    globs = dict(interface=zope.interface,
                 component=zope.component,
                 path=skins_path,
                 new_template_path=new_template_path,
                 os=os)


    return unittest.TestSuite(
        [zope.testing.doctest.DocFileSuite(
                doctest,
                optionflags=OPTIONFLAGS,
                setUp=setUp,
                globs=globs,
                tearDown=tearDown,
                package="repoze.bfg.skins") for doctest in doctests]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
