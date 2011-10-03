import pkg_resources
import sys

from pyramid_skins.zcml import skins
from pyramid.asset import resolve_asset_spec
from pyramid.path import caller_path
from zope.configuration.config import ConfigurationMachine


def register_path(config, spec, discovery=False, indexes=[], request_type=None):
    """ Add a skin path to the current configuration state.

    If ``discovery`` is enabled, the path will automatically be
    monitored for changes.

    The ``indexes`` argument is an optional list of view registrations
    with the provided names.

    The ``request_type`` option decides the request type for which to
    make the registration.
    """

    package_name, path = resolve_asset_spec(spec)
    if package_name is not None:
        path = pkg_resources.resource_filename(package_name, path)
    else:
        path = caller_path(path)

    if package_name is None: # absolute filename
        package = config.package
    else:
        __import__(package_name)
        package = sys.modules[package_name]
    context = ConfigurationMachine()
    context.registry = config.registry
    context.autocommit = False
    context.package = package
    context.route_prefix = getattr(config, 'route_prefix', None)

    directive = skins(context, path, discovery, request_type)
    for index in indexes:
        directive.view(config, index)

    for action in directive():
        config.action(*action)
