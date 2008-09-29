from zope import component
from interfaces import IMacro

class Macros(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __getattr__(self, name):
        return component.getMultiAdapter(
            (self.context, self.request), IMacro, name=name)

    def __call__(self, context):
        return Macros(context, self.request)
