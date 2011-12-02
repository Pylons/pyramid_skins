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

        try:
            name = system['view'].__name__
        except AttributeError:
            # handles the case of @view_config applied to instance methods
            name = system['request'].view_name

        request = system['request']

        instance = registry.queryAdapter(request, ISkinObject, name=name) or \
                   registry.getUtility(ISkinObject, name=name)

        return instance.render(**system)
    return renderer
