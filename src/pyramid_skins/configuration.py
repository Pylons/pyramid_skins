import os
import pkg_resources
import weakref

from pyramid.asset import resolve_asset_spec
from pyramid.compat import bytes_, text_
from pyramid.path import caller_path
from pyramid_skins.interfaces import ISkinObject
from pyramid_skins.interfaces import ISkinObjectFactory
from pyramid_skins.models import SkinObject


def walk(path):
    os.lstat(path)
    for dir_path, dirs, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dir_path, filename)
            rel_path = full_path[len(path) + 1:]
            yield rel_path.replace(os.path.sep, '/'), full_path


def dirs(path):
    os.lstat(path)
    for dir_path, dirs, filenames in os.walk(path):
        yield dir_path[len(path) + 1:]


class Adapter:
    def __init__(self, inst):
        self.inst = inst

    def __call__(self, request):
        return self.inst

    def refresh(self):
        return self.inst.refresh()


def register_skin_object(registry, relative_path, path, request_type):
    ext = os.path.splitext(path)[1]
    factory = registry.queryUtility(ISkinObjectFactory, name=ext) or SkinObject

    name = factory.component_name(relative_path)

    if request_type is not None:
        inst = registry.adapters.lookup(
            (request_type, ), ISkinObject, name=name, default=None)
    else:
        inst = registry.queryUtility(ISkinObject, name=name)

    if inst is not None:
        inst.path = path
        inst.refresh()
    else:
        inst = factory(relative_path, path)

        if request_type is not None:
            registry.registerAdapter(
                Adapter(inst), (request_type, ), ISkinObject, name=name)
        else:
            registry.registerUtility(inst, ISkinObject, name)


def register_skin_view(config, relative_path, path, kwargs):
    for inst in config.registry.getAllUtilitiesRegisteredFor(ISkinObject):
        if inst.path == path:
            break
    else:  # pragma: nocover
        raise RuntimeError("Skin object not found: %s." % relative_path)

    name = type(inst).component_name(relative_path).replace('/', '_')

    config.add_view(view=inst, name=name, **kwargs)


class Skins(object):
    threads = weakref.WeakValueDictionary()

    def __init__(self, config, path=None, discovery=False, request_type=None):
        self.config = config
        self.registry = config.registry
        self.path = os.path.realpath(text_(path))
        self.views = []
        self.request_type = config.maybe_dotted(request_type)

        if discovery:
            thread = self.threads.get(id(self.registry))
            if thread is None:
                from pyramid_skins.discovery import Discoverer
                thread = self.threads[id(self.registry)] = Discoverer()
            thread.watch(self.path, self)

    def __call__(self):
        registry = self.registry

        for relative_path, path in walk(self.path):
            yield (
                (relative_path, path, ISkinObject),
                register_skin_object,
                (registry, relative_path, path, self.request_type))

        objects = {}
        for relative_path, path in walk(self.path):
            objects[relative_path] = path

        for index, kwargs in self.views:
            if index is not None:
                for path in dirs(self.path):
                    relative_path = os.path.join(path, index)
                    skin_path = objects.get(relative_path)
                    if skin_path is not None:
                        objects[path] = skin_path

            for relative_path, path in objects.items():
                yield (
                    (
                        relative_path, path, ISkinObject,
                        kwargs.get('name'), kwargs.get('request_type'),
                        kwargs.get('route_name'), kwargs.get('request_method'),
                        kwargs.get('request_param'), kwargs.get('containment'),
                        kwargs.get('attr'), kwargs.get('renderer'),
                        kwargs.get('wrapper'), kwargs.get('xhr'),
                        kwargs.get('accept'), kwargs.get('header'),
                        kwargs.get('path_info')),
                    register_skin_view,
                    (self.config, relative_path, path, kwargs))

    def configure(self):
        for action in self():
            self.config.action(*action)

        return self.config

    def view(self, context, index=None, **kwargs):
        assert 'name' not in kwargs
        kwargs.setdefault('request_type', self.request_type)
        self.views.append((index, kwargs))


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

    directive = Skins(config, path, discovery, request_type)
    for index in indexes:
        directive.view(config, index)

    for action in directive():
        config.action(*action)

    return directive
