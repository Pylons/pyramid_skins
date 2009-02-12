import os
import webob

from zope import interface
from zope import component
from zope.component.interfaces import ComponentLookupError

from repoze.bfg.interfaces import IRequest

from chameleon.zpt.template import PageTemplateFile

from interfaces import ISkinApi
from interfaces import ISkinApiMethod
from interfaces import ISkinTemplate
from interfaces import ISkinTemplateView
from interfaces import IBoundSkinTemplate

from copy import copy

def get_skin_template(context, request, name, request_type=None):
    if request_type is None:
        return component.queryMultiAdapter(
            (context, request), ISkinTemplate, name=name)

    factory = component.getSiteManager().adapters.lookup(
        (interface.providedBy(context), request_type), 
        ISkinTemplate, name=name)

    if factory is not None:
        return factory(context, request)

    msg = "Unable to look up skin template '%s' for provided = %s." % (
        name, repr((context, request)))
    
    raise ComponentLookupError(msg)

def get_skin_template_view(context, request, name, request_type=None):
    if request_type is None:
        request_type = interface.providedBy(request)
        
    view = component.getSiteManager().adapters.lookup(
        (interface.providedBy(context), request_type), 
        ISkinTemplateView, name=name)

    if view is None:
        msg = "Unable to look up skin template view '%s' for provided = %s." % (
            name, repr((context, request)))
        raise ComponentLookupError(msg)

    return view

def render_skin_template_to_response(context, request, name, **kwargs):
    template = get_skin_template(context, request, name)
    if template is not None:
        return template(**kwargs)

def render_skin_template(context, request, name, **kwargs):
    template = get_skin_template(context, request, name)
    if template is not None:
        return template.render(**kwargs)

class SkinTemplate(object):
    interface.implements(ISkinTemplate)

    context = None
    request = None
    
    def __init__(self, path, content_type=None):
        self.template = PageTemplateFile(path)
        self.name, ext = os.path.splitext(os.path.basename(path))
        self.path = path
        self.content_type = content_type
        
    def __eq__(self, other):
        return self.template is other.template

    def __getattr__(self, name):
        assert IBoundSkinTemplate.providedBy(self)
        
        if name.startswith('get_'):
            method = component.queryMultiAdapter(
                (self.context, self.request, self),
                ISkinApiMethod, name=name[4:])
        
            if method is not None:
                return method
        
            method = component.queryMultiAdapter(
                (self.context, self.request, self),
                ISkinApi, name=name[4:])
            
            if method is None:
                raise AttributeError(name)
            
            return method
        
        raise AttributeError(name)

    def __call__(self, context=None, request=None, **kwargs):
        if IBoundSkinTemplate.providedBy(self):
            return webob.Response(
                self.render(**kwargs), content_type=self.content_type)
        return self.bind(context, request)
    
    @property
    def macros(self):
        return self.template.macros
    
    def bind(self, context, request):
        """Bind template to context and request (returns a copy of the
        template instance)."""
        
        template = copy(self)
        template.context = context
        template.request = request
        interface.alsoProvides(template, IBoundSkinTemplate)
        
        return template
    
    def render(self, **kwargs):
        """Bind and render template."""

        assert IBoundSkinTemplate.providedBy(self)

        return self.template(
            context=self.context, request=self.request, template=self, **kwargs)

    def get_api(self, name, context=None):
        """Look up skin api by name."""

        assert IBoundSkinTemplate.providedBy(self)
        
        if context is None:
            context = self.context

        return component.getMultiAdapter(
            (context, self.request, self), ISkinApi, name=name)
    
    def get_macro(self, name=None, context=None):
        """Look up skin macro by name."""

        assert IBoundSkinTemplate.providedBy(self)
        
        if context is None:
            context = self.context

        if name is None:
            return self.template.macros.bind(
                context=context, request=self.request, template=self)[""]

        template = get_skin_template(
            context, self.request, name)
        if template is None:
            raise component.ComponentLookupError(
                "Unable to look up skin macro: %s." % repr(name))
            
        if template == self:
            raise RuntimeError(
                "Macro is equal to calling template.")
                
        return template.get_macro()

class SkinTemplateView(object):
    interface.implementsOnly(ISkinTemplateView)

    def __init__(self, path, content_type=None):
        self.template = SkinTemplate(path, content_type=content_type)

    def __call__(self, context=None, request=None, **kwargs):
        template = self.template.bind(context, request)
        return template(**kwargs)
        
    def render(self, context, request, **kwargs):
        template = self.template.bind(context, request)
        return template.render(**kwargs)

class SkinApi(object):
    """Base class for skin template helper APIs."""
    
    interface.implements(ISkinApi)
    component.adapts(interface.Interface, IRequest, ISkinTemplate)
    
    def __init__(self, context, request, template):
        self.context = context
        self.request = request
        self.template = template
