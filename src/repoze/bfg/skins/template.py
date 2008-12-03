import os
import webob

from zope import interface
from zope import component

from repoze.bfg.interfaces import IRequest
from chameleon.zpt.template import PageTemplateFile

from interfaces import ISkinApi
from interfaces import ISkinMacro
from interfaces import ISkinTemplate

from copy import copy

def get_skin_template(context, request, name):
    """Look up skin template by name."""
    
    gsm = component.getSiteManager()
    return gsm.adapters.lookup(
        map(interface.providedBy, (context, request)), ISkinTemplate, name=name)

def render_skin_template_to_response(context, request, name):
    return component.queryMultiAdapter(
        (context, request), ISkinTemplate, name)

def render_skin_template(context, request, name):
    response = render_skin_template_to_response(context, request, name)
    if response is not None:
        return response.body

class SkinTemplate(object):
    interface.implements(ISkinTemplate)

    context = None
    request = None
    
    def __init__(self, path):
        self.template = PageTemplateFile(path)
        self.name, ext = os.path.splitext(os.path.basename(path))
        self.path = path

    def __call__(self, context, request, **kwargs):
        """Render and return a WebOb response."""
        
        return webob.Response(
            self.render(context, request, **kwargs))

    def __getattr__(self, name):
        if name.startswith('get_'):
            method = component.queryMultiAdapter(
                (self.context, self.request, self), ISkinApi, name=name[4:])
            if method is None:
                raise AttributeError(name)
            return method
        raise AttributeError(name)
        
    def bind(self, context, request):
        """Bind template to context and request (returns a copy of the
        template instance)."""
        
        template = copy(self)
        template.context = context
        template.request = request
        return template
    
    def render(self, context, request, **kwargs):
        """Bind and render template."""

        return self.template(
            context=context, request=request,
            template=self.bind(context, request), **kwargs)

    def get_api(self, name):
        """Look up skin api by name."""
        
        assert self.context is not None
        return component.getMultiAdapter(
            (self.context, self.request, self), ISkinApi, name=name)

    def get_macro(self, name):
        """Look up skin macro by name."""
        
        assert self.context is not None
        return component.getMultiAdapter(
            (self.context, self.request), ISkinMacro, name=name)
    
class SkinMacro(SkinTemplate):
    interface.implements(ISkinMacro)
    
    def __call__(self, context, request):
        def macro(context, request):
            return self.template.macros.bind(
                context=context, request=request,
                template=self.bind(context, request))[""]
        return macro(context, request)

class SkinApi(object):
    """Base class for skin template helper APIs."""
    
    interface.implements(ISkinApi)
    component.adapts(interface.Interface, IRequest, ISkinTemplate)
    
    def __init__(self, context, request, template):
        self.context = context
        self.request = request
        self.template = template
