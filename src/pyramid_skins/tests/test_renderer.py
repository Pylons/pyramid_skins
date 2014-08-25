import os
import unittest
from zope.interface import alsoProvides

path = os.path.dirname(__file__)


class RendererTest(unittest.TestCase):
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

    def register_skins(self):
        from pyramid.interfaces import IRequest
        from pyramid_skins.configuration import register_path
        import new

        skins = {}
        for name in ('alt_skins', 'other_skins'):
            interface = new.classobj(
                'IThemeRequest-%s' % name,
                (IRequest, ),
                dict(__doc__=""" marker interface for custom theme """))
            skins[name] = interface
            register_path(self.config, os.path.join(path, name), request_type=interface)
        return skins

    def test_multiple_skins_alt(self):
        from pyramid.threadlocal import get_current_request
        from pyramid.view import render_view
        from pyramid_skins.configuration import register_path
        from pyramid_skins.renderer import renderer_factory

        register_path(self.config, os.path.join(path, 'skins'))
        skins = self.register_skins()
        self.config.add_renderer('skin', renderer_factory)

        def index(context, request):
            return {'context': context}

        self.config.add_view(index, name='index', renderer='skin')

        alsoProvides(get_current_request(), skins['alt_skins'])
        result = render_view('Hello world!', get_current_request(), 'index')
        self.assertTrue('Alternative' in result)

    def test_multiple_skins_other(self):
        from pyramid.threadlocal import get_current_request
        from pyramid.view import render_view
        from pyramid_skins.configuration import register_path
        from pyramid_skins.renderer import renderer_factory

        register_path(self.config, os.path.join(path, 'skins'))
        skins = self.register_skins()
        self.config.add_renderer('skin', renderer_factory)

        def index(context, request):
            return {'context': context}

        self.config.add_view(index, name='index', renderer='skin')

        alsoProvides(get_current_request(), skins['other_skins'])
        result = render_view('Hello world!', get_current_request(), 'index')
        self.assertTrue('Other' in result)
