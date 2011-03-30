import copy
import os
import mimetypes
import webob

from zope.interface import implements
from zope.interface import classProvides
from zope.component import getUtility
from zope.component import queryAdapter
from chameleon.zpt.template import PageTemplateFile

from repoze.bfg.skins.interfaces import ISkinObject
from repoze.bfg.skins.interfaces import ISkinObjectFactory
from repoze.bfg.threadlocal import get_current_request

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
            if encoding is not None:
                self.encoding = encoding

    def __call__(self, context=None, request=None, **kw):
        if self.path is None:
            inst = self.__get__()
            return inst(context=context, request=request, **kw)

        result = self.render(context=context, request=request, **kw)
        if isinstance(result, basestring):
            response = webob.Response(body=result)
        else:
            response = webob.Response(app_iter=result)
            response.content_length = os.path.getsize(self.path)

        content_type = self.content_type
        if content_type is None:
            content_type = type(self).content_type
        response.content_type = content_type
        response.charset = self.encoding
        return response

    def __get__(self, view=None, cls=None):
        inst = queryAdapter(get_current_request(), ISkinObject, name=self.name) or \
               getUtility(ISkinObject, name=self.name)
        inst = copy.copy(inst)
        if view is not None:
            inst._bound_kwargs = view.__dict__
        return inst

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

    def __init__(self, relative_path, path):
        SkinObject.__init__(self, relative_path, path)
        PageTemplateFile.__init__(self, path)

    def refresh(self):
        self.read()

    def render(self, *args, **kw):
        if args:
            slots, = args
            return self.render_macro("", slots=slots, parameters=kw)
        kw.update(self._bound_kwargs)
        return PageTemplateFile.render(self, **kw)

    @classmethod
    def component_name(cls, relative_path):
        return os.path.splitext(relative_path)[0]

    def _set_path(self, path):
        self.filename = path

    def _get_path(self):
        return self.filename

    path = property(_get_path, _set_path)



