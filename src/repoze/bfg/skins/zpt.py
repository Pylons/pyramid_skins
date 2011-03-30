import re

from zope import interface
from zope import component

from chameleon.core import types
from chameleon.zpt.expressions import ExpressionTranslator
from chameleon.zpt.interfaces import IExpressionTranslator

from repoze.bfg.skins.interfaces import ISkinObject
from repoze.bfg.url import route_url
from repoze.bfg.threadlocal import get_current_request


class SkinTranslator(ExpressionTranslator):
    interface.implements(IExpressionTranslator)

    symbol = '_lookup_skin'
    re_path = re.compile(r'^[A-Za-z./_\-]+$')

    def translate(self, string, escape=None):
        if not string:
            return None
        string = string.strip()

        if self.re_path.match(string) is None:
            raise SyntaxError(string)

        value = types.value("%s('%s', template)" % (self.symbol, string))
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


def _lookup_component(request, name):
    return component.queryAdapter(request, ISkinObject, name=name) or \
           component.getUtility(ISkinObject, name=name)


def _lookup_skin(name, template):
    request = get_current_request()

    if name.startswith('/'):
        return _lookup_component(request, name[1:])

    if not ISkinObject.providedBy(template):
        raise TypeError(
            "Relative lookup for '%s' invalid for template class: %s." % (
                name, type(template)))
    path = '/' + template.name
    while path:
        try:
            return _lookup_component(request, "%s/%s" % (path[1:], name))
        except component.ComponentLookupError:
            pass

        path = path[:path.rindex('/')]

    return _lookup_component(request, name)
