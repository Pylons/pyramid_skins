import os
import webob

from zope import interface
from zope import component

from repoze.bfg.interfaces import IRequest
from chameleon.zpt.template import PageTemplateFile

from interfaces import ISkinApi
from interfaces import ISkinTemplate

from copy import copy

def get_skin_template(context, request, name):
    """Look up skin template by name."""
    
    gsm = component.getSiteManager()
    return gsm.adapters.lookup(
        map(interface.providedBy, (context, request)), ISkinTemplate, name=name)

def render_skin_template_to_response(context, request, name, **kwargs):
    template = get_skin_template(context, request, name)
    if template is not None:
        return template(context, request, **kwargs)

def render_skin_template(context, request, name, **kwargs):
    response = render_skin_template_to_response(
        context, request, name, **kwargs)
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

    def __eq__(self, other):
        return self.template is other.template

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

    def get_api(self, name, context=None):
        """Look up skin api by name."""

        if context is None:
            context = self.context
            
        assert self.request is not None
        return component.getMultiAdapter(
            (context, self.request, self), ISkinApi, name=name)

    def get_macro(self, name=None, context=None):
        """Look up skin macro by name."""
        
        if context is None:
            context = self.context

        assert self.request is not None

        if name is None:
            return self.template.macros.bind(
                context=context, request=self.request,
                template=self.bind(context, self.request))[""]

        template = get_skin_template(context, self.request, name)
        if template is None:
            raise component.ComponentLookupError(
                "Unable to look up skin template: %s." % repr(name))
            
        if template == self:
            raise RuntimeError(
                "Macro is equal to calling template.")
                
        return template.bind(context, self.request).get_macro()

class SkinApi(object):
    """Base class for skin template helper APIs."""
    
    interface.implements(ISkinApi)
    component.adapts(interface.Interface, IRequest, ISkinTemplate)
    
    def __init__(self, context, request, template):
        self.context = context
        self.request = request
        self.template = template
