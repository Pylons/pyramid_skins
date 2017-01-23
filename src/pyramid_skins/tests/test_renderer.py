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
        self.assertTrue(b'Hello world' in result)

    def register_skins(self, paths):
        from pyramid.interfaces import IRequest
        from pyramid_skins.configuration import register_path

        skins = {}
        for path in paths:
            name = os.path.basename(path)
            class interface(IRequest):
                __doc__ = """ marker interface for custom theme """
            interface.__name__ = 'IThemeRequest-%s' % name
            skin = register_path(self.config, path, request_type=interface)
            skins[name] = dict(
                skin=skin,
                interface=interface)
        return skins

    def test_multiple_skins_alt(self):
        from pyramid.threadlocal import get_current_request
        from pyramid.view import render_view
        from pyramid_skins.configuration import register_path
        from pyramid_skins.renderer import renderer_factory

        register_path(self.config, os.path.join(path, 'skins'))
        skins = self.register_skins([
            os.path.join(path, 'alt_skins'),
            os.path.join(path, 'other_skins')])
        self.config.add_renderer('skin', renderer_factory)

        def index(context, request):
            return {'context': context}

        self.config.add_view(index, name='index', renderer='skin')

        alsoProvides(get_current_request(), skins['alt_skins']['interface'])
        result = render_view('Hello world!', get_current_request(), 'index')
        self.assertTrue(b'Alternative' in result)

    def test_multiple_skins_other(self):
        from pyramid.threadlocal import get_current_request
        from pyramid.view import render_view
        from pyramid_skins.configuration import register_path
        from pyramid_skins.renderer import renderer_factory

        register_path(self.config, os.path.join(path, 'skins'))
        skins = self.register_skins([
            os.path.join(path, 'alt_skins'),
            os.path.join(path, 'other_skins')])
        self.config.add_renderer('skin', renderer_factory)

        def index(context, request):
            return {'context': context}

        self.config.add_view(index, name='index', renderer='skin')

        alsoProvides(get_current_request(), skins['other_skins']['interface'])
        result = render_view('Hello world!', get_current_request(), 'index')
        self.assertTrue(b'Other' in result)

    def test_skin_reload(self):
        from pyramid_skins.configuration import register_path
        import shutil
        import tempfile

        register_path(self.config, os.path.join(path, 'skins'))
        tmp = tempfile.mkdtemp()

        try:
            skins_dir = os.path.join(tmp, 'skins')
            os.mkdir(skins_dir)
            with open(os.path.join(skins_dir, 'index.pt'), 'wb') as f:
                f.write(b'<html><title>Alternative</title></html>')

            skins = self.register_skins([skins_dir])

            from pyramid_skins.renderer import renderer_factory
            self.config.add_renderer('skin', renderer_factory)

            def index(context, request):
                return {'context': context}

            self.config.add_view(index, name='index', renderer='skin')

            from pyramid.view import render_view
            from pyramid.threadlocal import get_current_request
            alsoProvides(get_current_request(), skins['skins']['interface'])
            result = render_view('Hello world!', get_current_request(), 'index')
            self.assertTrue(b'Alternative' in result)
            with open(os.path.join(skins_dir, 'index.pt'), 'wb') as f:
                f.write(b'<html><title>Other</title></html>')
            skins['skins']['skin'].configure()
            result = render_view('Hello world!', get_current_request(), 'index')
            self.assertTrue(b'Other' in result)
        finally:
            shutil.rmtree(tmp)
