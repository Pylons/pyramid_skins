import os
import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)

class DoctestCase(unittest.TestCase):
    def __new__(self, test):
        return getattr(self, test)()

    @classmethod
    def test_docs(cls):
        import manuel.testing
        import manuel.codeblock
        import manuel.doctest
        import manuel.capture
        m = manuel.doctest.Manuel(optionflags=OPTIONFLAGS)
        m += manuel.codeblock.Manuel()
        m += manuel.capture.Manuel()

        import pkg_resources
        return manuel.testing.TestSuite(
            m,
            pkg_resources.resource_filename(
                "repoze.bfg.skins", os.path.join(
                    "docs", "registration.rst")),
            pkg_resources.resource_filename(
                "repoze.bfg.skins", os.path.join(
                    "docs", "templates.rst")),
            pkg_resources.resource_filename(
                "repoze.bfg.skins", os.path.join(
                    "docs", "routing.rst")),
            setUp=cls.setUp,
            tearDown=cls.tearDown)

    @staticmethod
    def setUp(test):
        import repoze.bfg.testing
        repoze.bfg.testing.setUp()
        repoze.bfg.testing.registerRoute('/willneverbeused', 'willneverbeused')

    @staticmethod
    def tearDown(test):
        import repoze.bfg.testing
        repoze.bfg.testing.tearDown()

