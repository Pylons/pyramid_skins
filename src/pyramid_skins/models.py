import os
import mimetypes
import functools

from zope.interface import implements
from zope.interface import classProvides
from zope.component import ComponentLookupError

from chameleon.zpt.template import PageTemplateFile
from chameleon.tales import ProxyExpr
from chameleon.tales import TalesExpr

from pyramid.response import Response
from pyramid.threadlocal import get_current_request
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_url

from pyramid_skins.interfaces import ISkinObject
from pyramid_skins.interfaces import ISkinObjectFactory


def _lookup_component(request, name):
    registry = get_current_registry()
    return registry.queryAdapter(request, ISkinObject, name=name) or \
           registry.getUtility(ISkinObject, name=name)


def get_route_url_from_threadlocal_request(route_name):
    name = "/" + route_name.strip()
    request = get_current_request()
    return route_url(name, request)


def lookup_skin(template, name):
    request = get_current_request()
    name = name.strip()

    if name.startswith('/'):
        return _lookup_component(request, name[1:])

    assert ISkinObject.providedBy(template)

    path = '/' + template.name
    while path:
        try:
            return _lookup_component(request, "%s/%s" % (path[1:], name))
        except ComponentLookupError:
            pass

        path = path[:path.rindex('/')]

    return _lookup_component(request, name)


# BBB: Chameleon < 2.10.
if TalesExpr not in ProxyExpr.__bases__:
    _proxy_expr = ProxyExpr

    class ProxyExpr(TalesExpr):
        def __init__(self, name, *args):
            super(ProxyExpr, self).__init__(*args)
            self.name = name

        def translate(self, expression, target):
            """Return statements that assign a value to ``target``."""

            compiler = _proxy_expr(self.name, expression)
            return compiler(target, None)


class SkinObject(object):
    implements(ISkinObject)
    classProvides(ISkinObjectFactory)

    _bound_kwargs = {}
    content_type = 'application/octet-stream'
    encoding = None

    def __init__(self, relative_path, path=None):
        self.path = path
        self.name = self.component_name(relative_path)

        if path is not None:
            content_type, encoding = mimetypes.guess_type(path)
            if content_type is not None:
                self.content_type = content_type
            if encoding is not None:  # pragma: nocover
                self.encoding = encoding

    def __call__(self, context=None, request=None, **kw):
        if self.path is None:
            inst = self.__get__()
            return inst(context=context, request=request, **kw)

        result = self.render(context=context, request=request, **kw)
        if isinstance(result, basestring):
            response = Response(body=result)
        else:
            response = Response(app_iter=result)
            response.content_length = os.path.getsize(self.path)

        content_type = self.content_type
        if content_type is None:
            content_type = type(self).content_type
        response.content_type = content_type
        response.charset = self.encoding
        return response

    def __get__(self, view=None, cls=None):
        request = get_current_request()
        registry = get_current_registry()
        inst = registry.queryAdapter(request, ISkinObject, name=self.name) or \
               registry.getUtility(ISkinObject, name=self.name)

        if view is None:
            return inst

        return functools.partial(inst.__call__, view=view, **view.__dict__)

    def __repr__(self):
        return '<%s.%s name="%s" path="%s" at 0x%x>' % (
            type(self).__module__, type(self).__name__,
            self.name, self.path, id(self))

    @classmethod
    def component_name(cls, relative_path):
        return relative_path

    def refresh(self):
        pass

    def render(self, **kw):
        return file(self.path)


class SkinTemplate(SkinObject, PageTemplateFile):
    content_type = 'text/html'
    encoding = 'UTF-8'

    expression_types = PageTemplateFile.expression_types.copy()
    expression_types['skin'] = functools.partial(ProxyExpr, '__skin')
    expression_types['route'] = functools.partial(ProxyExpr, '__route')

    @property
    def builtins(self):
        return {
            'macros': self.macros,
            'nothing': None,
            '__skin': functools.partial(lookup_skin, self),
            '__route': get_route_url_from_threadlocal_request,
            }

    def __init__(self, relative_path, path):
        SkinObject.__init__(self, relative_path, path)
        PageTemplateFile.__init__(self, path)

    def refresh(self):
        body = self.read()
        self.cook(body)

    def render(self, **context):
        return PageTemplateFile.render(self, **context)

    @classmethod
    def component_name(cls, relative_path):
        return os.path.splitext(relative_path)[0]

    def _set_path(self, path):
        self.filename = path

    def _get_path(self):
        return self.filename

    path = property(_get_path, _set_path)
