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
                "pyramid_skins", os.path.join(
                    "docs", "registration.rst")),
            pkg_resources.resource_filename(
                "pyramid_skins", os.path.join(
                    "docs", "templates.rst")),
            pkg_resources.resource_filename(
                "pyramid_skins", os.path.join(
                    "docs", "routing.rst")),
            setUp=cls.setUp,
            tearDown=cls.tearDown,
            )

    @staticmethod
    def setUp(test):
        import pyramid.testing
        pyramid.testing.registerRoute('/willneverbeused', 'willneverbeused')

        request = pyramid.testing.DummyRequest()
        config = pyramid.testing.setUp(request=request, hook_zca=True)

        import pyramid.config
        context = pyramid.config.PyramidConfigurationMachine()
        context.registry = config.registry

        from zope.configuration.xmlconfig import string
        from zope.configuration.xmlconfig import registerCommonDirectives
        registerCommonDirectives(context)
        config = pyramid.config.Configurator.with_context(context)
        config.commit()

        import pyramid_zcml
        pyramid_zcml.load_zcml(config, 'pyramid_zcml:meta.zcml')

        def xmlconfig(s, context=context):
            context = string(s, context=context, execute=False)
            config = pyramid.config.Configurator.with_context(context)
            config.commit()

        test.globs['xmlconfig'] = xmlconfig
        test.globs['registry'] = config.registry
        test.globs['request'] = request

    @staticmethod
    def tearDown(test):
        test.globs.clear()
        import pyramid.testing
        pyramid.testing.tearDown()
