from models import SkinObject
from routes import RoutesTraverserFactory
from configuration import register_path

import pyramid_zcml

def includeme(config):
    """ Function meant to be included via
    :meth:`pyramid.config.Configurator.include`, which sets up the
    Configurator with a ``register_path`` method."""

    config.include(pyramid_zcml)
    config.load_zcml("pyramid_skins:configure.zcml")
    config.add_directive('register_path', register_path, action_wrap=False)
