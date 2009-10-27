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

        import zope.component
        registry = zope.component.getSiteManager()

        from repoze.bfg.threadlocal import manager
        info = manager.get().copy()
        manager.push(info)
        info['registry'] = registry

        import repoze.bfg.configuration
        import repoze.bfg.skins

        repoze.bfg.configuration.make_registry(
            None, package=repoze.bfg.skins, registry=registry)

        assert zope.component.getSiteManager() is registry

    @staticmethod
    def tearDown(test):
        from repoze.bfg.threadlocal import manager
        manager.pop()

        import repoze.bfg.testing
        repoze.bfg.testing.tearDown()
