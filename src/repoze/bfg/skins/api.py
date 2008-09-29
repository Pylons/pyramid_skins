from zope import component
from interfaces import IApi

class Api(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __getattr__(self, name):
        return component.getMultiAdapter(
            (self.context, self.request), IApi, name=name)
            
    def __call__(self, context):
        return Api(context, self.request)
