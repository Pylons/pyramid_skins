from zope import interface
from zope import component

from chameleon.core import types
from chameleon.zpt.expressions import ExpressionTranslator
from chameleon.zpt.interfaces import IExpressionTranslator

from repoze.bfg.skins.interfaces import ISkinObject
from repoze.bfg.url import route_url

class SkinTranslator(ExpressionTranslator):
    interface.implements(IExpressionTranslator)

    symbol = '_lookup_skin'

    def translate(self, string, escape=None):
        if not string:
            return None
        string = string.strip()
        value = types.value("%s('%s')" % (self.symbol, string))
        value.symbol_mapping[self.symbol] = _lookup_skin
        return value

class RouteTranslator(ExpressionTranslator):
    interface.implements(IExpressionTranslator)

    symbol = '_route_url'

    def translate(self, string, escape=None):
        if not string:
            return None
        string = string.strip()
        value = types.value("%s('%s', request, subpath='').rstrip('/')" % (
            self.symbol, string))
        value.symbol_mapping[self.symbol] = route_url
        return value

def _lookup_skin(name):
    return component.getUtility(ISkinObject, name=name)
