from pyramid.interfaces import IRenderer
from zope.interface import implementer

from .interfaces import ISkinObject


@implementer(IRenderer)
def renderer_factory(info):
    """ Renders a skin object based on view name. """

    registry = info.registry

    def renderer(value, system):
        try:
            system.update(value)
        except (TypeError, ValueError):  # pragma: nocover
            raise ValueError('Renderer was passed non-dictionary as value.')

        name = system['view'].__name__
        request = system['request']

        instance = registry.queryAdapter(request, ISkinObject, name=name) or \
                   registry.getUtility(ISkinObject, name=name)

        return instance.render(**system)
    return renderer
