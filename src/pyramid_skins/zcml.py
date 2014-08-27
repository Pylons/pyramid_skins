from zope import interface
from zope.schema import TextLine
from zope.schema import Bool

from zope.configuration.fields import Path

from pyramid_zcml import IViewDirective
from pyramid_skins.configuration import Skins
from pyramid_skins.configuration import register_skin_object
from pyramid.config import Configurator


def skins(context, **kw):
    config = Configurator(registry=context.registry, autocommit=True)
    return Skins(config, **kw)


class ISkinDirective(interface.Interface):
    path = Path(
        title=u"Path",
        description=u"Path to the directory containing the skin.",
        required=True)

    discovery = Bool(
        title=u"Discovery",
        description=(u"Enables run-time discovery."),
        required=False)

    request_type = TextLine(
        title=u"The request type string or dotted name interface.",
        description=(u"If provided, skin objects will be registered "
                     u"as named adapters for the request type interface."),
        required=False)


class ISkinViewDirective(IViewDirective):
    index = TextLine(
        title=u"Index filename",
        description=u"""
        Filename for which index views are created.""",
        required=False)
