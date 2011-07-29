import os
import unittest

path = os.path.dirname(__file__)


class ImperativeConfigurationTest(unittest.TestCase):
    def setUp(self):
        import pyramid.testing
        self.config = pyramid.testing.setUp(
            hook_zca=True,
            request=pyramid.testing.DummyRequest(),
            autocommit=True
            )

        import pyramid_skins
        self.config.include(pyramid_skins)

    def tearDown(self):
        import pyramid.testing
        pyramid.testing.tearDown()

    def test_renderer(self):
        from pyramid_skins.configuration import register_path
        register_path(self.config, os.path.join(path, 'skins'))

        from pyramid_skins.renderer import renderer_factory
        self.config.add_renderer('skin', renderer_factory)

        def index(context, request):
            return {'context': context}

        self.config.add_view(index, name='index', renderer='skin')

        from pyramid.view import render_view
        from pyramid.threadlocal import get_current_request
        result = render_view('Hello world!', get_current_request(), 'index')
        self.assertTrue('Hello world' in result)
