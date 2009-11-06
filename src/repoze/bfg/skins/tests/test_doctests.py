import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)

class DoctestCase(unittest.TestCase):
    def __new__(self, test):
        return getattr(self, test)()

    @classmethod
    def test_readme(cls):
        return doctest.DocFileSuite(
            'README.txt',
            optionflags=OPTIONFLAGS,
            setUp=cls.setUp,
            tearDown=cls.tearDown,
            package='repoze.bfg.skins')

    @staticmethod
    def setUp(test):
        import repoze.bfg.testing
        repoze.bfg.testing.setUp()
        repoze.bfg.testing.registerRoute('/willneverbeused', 'willneverbeused')

    @staticmethod
    def tearDown(test):
        import repoze.bfg.testing
        repoze.bfg.testing.tearDown()

