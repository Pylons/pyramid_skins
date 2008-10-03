from zope import interface
from zope import component

from repoze.bfg.interfaces import IRequest

from interfaces import ITemplateAPI
from interfaces import ISkinTemplate

class Api(object):
    def __init__(self, context, request, template):
        self.context = context
        self.request = request
        self.template = template
        
    def __getattr__(self, name):
        return component.getMultiAdapter(
            (self.context, self.request, self.template), ITemplateAPI, name=name)
            
    def __call__(self, context):
        return Api(context, self.request, self.template)

class TemplateAPI(object):
    """Base class."""
    
    interface.implements(ITemplateAPI)
    component.adapts(interface.Interface, IRequest, ISkinTemplate)
    
    def __init__(self, context, request, template):
        self.context = context
        self.request = request
        self.template = template
