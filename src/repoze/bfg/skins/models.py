import os
import mimetypes
import webob

from zope.interface import implements
from zope.interface import classProvides
from zope.component import getUtility
from chameleon.zpt.template import PageTemplateFile

from repoze.bfg.skins.interfaces import ISkinObject
from repoze.bfg.skins.interfaces import ISkinObjectFactory

class SkinObject(object):
    implements(ISkinObject)
    classProvides(ISkinObjectFactory)

    def __init__(self, relative_path, path=None):
        self.path = path
        self._name = self.component_name(relative_path)

    def __call__(self, context, request):
        content_type, encoding = mimetypes.guess_type(self.path)
        if not content_type:
            content_type = 'application/octet-stream'

        response = webob.Response(app_iter=file(self.path))
        response.content_type = content_type
        return response

    def __get__(self, *args):
        return getUtility(ISkinObject, name=self._name)

    def __repr__(self):
        return '<%s.%s name="%s" at 0x%x>' % (
            type(self).__module__, type(self).__name__, self._name, id(self))

    @classmethod
    def component_name(cls, relative_path):
        return relative_path

    def refresh(self):
        pass

class SkinTemplate(SkinObject, PageTemplateFile):
    def __init__(self, relative_path, path):
        SkinObject.__init__(self, relative_path, path)
        PageTemplateFile.__init__(self, path)

    def __call__(self, context, request, **kw):
        result = self.render(context=context, request=request, **kw)
        response = webob.Response(result)
        response.content_type = self.content_type or 'text/html'
        return response

    def refresh(self):
        self.read()

    @classmethod
    def component_name(cls, relative_path):
        return os.path.splitext(relative_path)[0]

    def _set_path(self, path):
        self.filename = path

    def _get_path(self):
        return self.filename

    path = property(_get_path, _set_path)



