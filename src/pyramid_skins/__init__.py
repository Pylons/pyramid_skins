from pyramid_skins.models import BindableSkinObject, SkinObject  # noqa
from pyramid_skins.routes import RoutesTraverserFactory
from pyramid_skins.configuration import register_path


def includeme(config):
    """ Function meant to be included via
    :meth:`pyramid.config.Configurator.include`, which sets up the
    Configurator with a ``register_path`` method."""
    from pyramid_skins.interfaces import ISkinObjectFactory
    from pyramid_skins.models import SkinTemplate

    config.add_directive('register_path', register_path, action_wrap=False)
    config.add_traverser(RoutesTraverserFactory)
    config.registry.registerUtility(SkinTemplate, ISkinObjectFactory, name='.pt')
