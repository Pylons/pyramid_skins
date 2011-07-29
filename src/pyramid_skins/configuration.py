import pkg_resources

from pyramid_skins.zcml import skins
from pyramid.asset import resolve_asset_spec
from pyramid.path import caller_path
from pyramid.config import PyramidConfigurationMachine
from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry


def register_path(config, spec, discovery=False, indexes=[], request_type=None):
    """ Add a skin path to the current configuration state.

    If ``discovery`` is enabled, the path will automatically be
    monitored for changes.

    The ``indexes`` argument is an optional list of view registrations
    with the provided names.

    The ``request_type`` option decides the request type for which to
    make the registration.
    """

    package, path = resolve_asset_spec(spec)
    if package is not None:
        path = pkg_resources.resource_filename(package, path)
    else:
        path = caller_path(path)

    context = PyramidConfigurationMachine()
    context.registry = config.registry

    directive = skins(context, path, discovery, request_type)
    for index in indexes:
        directive.view(config, index)

    for action in directive():
        config.action(*action)
