import os
import unittest

path = os.path.dirname(__file__)


class ImperativeConfigurationTest(unittest.TestCase):
    def setUp(self):
        import pyramid.testing
        self.config = pyramid.testing.setUp(hook_zca=True, autocommit=True)

    def tearDown(self):
        import pyramid.testing
        pyramid.testing.tearDown()

    def test_register_absolute_path(self):
        from pyramid_skins.configuration import register_path
        register_path(self.config, os.path.join(path, 'skins'))

        from pyramid_skins.interfaces import ISkinObject
        inst = self.config.registry.queryUtility(ISkinObject, name="index.pt")
        self.assertTrue(inst is not None)

    def test_register_asset_spec(self):
        from pyramid_skins.configuration import register_path
        register_path(self.config, "pyramid_skins:tests/skins")

        from pyramid_skins.interfaces import ISkinObject
        inst = self.config.registry.queryUtility(ISkinObject, name="index.pt")
        self.assertTrue(inst is not None)

    def test_register_view(self):
        name = 'index.pt'
        from pyramid_skins.configuration import register_path
        register_path(self.config, os.path.join(path, 'skins'), indexes=[name])

        from pyramid.testing import DummyRequest
        from pyramid.view import render_view

        response = render_view('Hello world!', DummyRequest(), "")
        self.assertTrue(response is not None)
