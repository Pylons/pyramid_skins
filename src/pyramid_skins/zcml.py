import os
import threading
import weakref
import logging

from zope import interface
from zope.schema import TextLine
from zope.schema import Bool

from zope.configuration.fields import Path

from pyramid_zcml import IViewDirective
from pyramid_zcml import with_context
from pyramid_skins.models import SkinObject
from pyramid_skins.interfaces import ISkinObject
from pyramid_skins.interfaces import ISkinObjectFactory
from pyramid.config import Configurator

logger = logging.getLogger("pyramid_skins")

import pyramid_skins as package


def walk(path):
    os.lstat(path)
    for dir_path, dirs, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dir_path, filename)
            rel_path = full_path[len(path) + 1:]
            yield rel_path.replace(os.path.sep, '/'), str(full_path)


def dirs(path):
    os.lstat(path)
    for dir_path, dirs, filenames in os.walk(path):
        yield dir_path[len(path) + 1:]


def register_skin_object(registry, relative_path, path, request_type):
    ext = os.path.splitext(path)[1]
    factory = registry.queryUtility(ISkinObjectFactory, name=ext) or \
              SkinObject

    name = factory.component_name(relative_path)

    if request_type is not None:
        inst = registry.adapters.lookup(
            (request_type, ), ISkinObject, name=name, default=None
            )
    else:
        inst = registry.queryUtility(ISkinObject, name=name)

    if inst is not None:
        inst.path = path
        inst.refresh()
    else:
        inst = factory(relative_path, path)

        def adapter(request):
            return inst

        if request_type is not None:
            registry.registerAdapter(
                adapter, (request_type, ), ISkinObject, name=name
                )
        else:
            registry.registerUtility(inst, ISkinObject, name)


def register_skin_view(registry, relative_path, path, kwargs):
    for inst in registry.getAllUtilitiesRegisteredFor(ISkinObject):
        if inst.path == path:
            break
    else:  # pragma: nocover
        raise RuntimeError("Skin object not found: %s." % relative_path)

    name = type(inst).component_name(relative_path).replace('/', '_')

    config = Configurator(registry=registry, autocommit=True)
    config.add_view(view=inst, name=name, **kwargs)


class Discoverer(threading.Thread):
    run = None

    def __init__(self):
        super(Discoverer, self).__init__()
        self.paths = {}

    def watch(self, path, handler):
        if self.run is None:  # pragma: nocover
            raise ImportError(
                "Must have either ``MacFSEvents`` (on Mac OS X) or "
                "``pyinotify`` (Linux) to enable runtime discovery.")

        self.paths[path] = handler

        # thread starts itself
        if not self.isAlive():
            self.daemon = True
            self.start()

    try:
        import fsevents
    except ImportError:  # pragma: nocover
        pass
    else:
        def run(self):  # pragma: nocover
            logger.info("Starting FS event listener.")

            def callback(subpath, subdir):
                for path, handler in self.paths.items():
                    if subpath.startswith(path):
                        config = handler.configure()
                        config.commit()

            stream = self.fsevents.Stream(callback, *self.paths)
            observer = self.fsevents.Observer()
            observer.schedule(stream)
            observer.run()
            observer.unschedule(stream)
            observer.stop()
            observer.join()

    try:
        import pyinotify
    except ImportError:  # pragma: nocover
        pass
    else:
        wm = pyinotify.WatchManager()

        def run(self):  # pragma: nocover
            self.watches = []
            mask = self.pyinotify.IN_CREATE

            for path in self.paths:
                wdd = self.wm.add_watch(path, mask, rec=True)
                self.watches.append(wdd)

            class Event(self.pyinotify.ProcessEvent):
                def process_IN_CREATE(inst, event):
                    subpath = event.path
                    for path, handler in self.paths.items():
                        if subpath.startswith(path):
                            config = handler.configure()
                            config.commit()

            handler = Event()
            notifier = self.pyinotify.Notifier(self.wm, handler)
            notifier.loop()
            for wdd in self.watches:
                self.wm.rm_watch(wdd.values())
            notifier.stop()
            notifier.join()


class skins(object):
    threads = weakref.WeakValueDictionary()

    def __init__(self, context, path=None, discovery=False, request_type=None):
        self.context = context
        self.path = os.path.realpath(path).encode('utf-8')
        self.views = []
        self.request_type = Configurator(context.registry, package=package, autocommit=False).\
                            maybe_dotted(request_type)

        if discovery:
            thread = self.threads.get(id(context.registry))
            if thread is None:
                thread = self.threads[id(context.registry)] = Discoverer()
            thread.watch(self.path, self)

    def __call__(self):
        registry = self.context.registry

        for relative_path, path in walk(self.path):
            yield (relative_path, path, ISkinObject), \
                  register_skin_object, \
                  (registry, relative_path, path, self.request_type)

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
                view = (relative_path, path, ISkinObject,) + \
                       (kwargs.get('name'), kwargs.get('request_type'),
                        kwargs.get('route_name'), kwargs.get('request_method'),
                        kwargs.get('request_param'), kwargs.get('containment'),
                        kwargs.get('attr'), kwargs.get('renderer'),
                        kwargs.get('wrapper'), kwargs.get('xhr'),
                        kwargs.get('accept'), kwargs.get('header'),
                        kwargs.get('path_info')), \
                        register_skin_view, \
                        (registry, relative_path, path, kwargs)

                yield view

    def configure(self):
        config = with_context(self.context)

        for action in self():
            config.action(*action)

        return config

    def view(self, context, index=None, **kwargs):
        assert 'name' not in kwargs
        kwargs.setdefault('request_type', self.request_type)
        self.views.append((index, kwargs))


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
        required=False,
        )


class ISkinViewDirective(IViewDirective):
    index = TextLine(
        title=u"Index filename",
        description=u"""
        Filename for which index views are created.""",
        required=False)
