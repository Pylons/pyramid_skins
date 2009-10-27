import os

from zope import interface
from zope.component import getSiteManager
from zope.component import queryUtility
from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.config import expand_action

from zope.schema import TextLine

from zope.configuration.fields import GlobalObject, Path
from zope.configuration.config import ConfigurationMachine

from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import INewRequest

from repoze.bfg.settings import get_settings
from repoze.bfg.zcml import view as register_bfg_view

from repoze.bfg.skins.models import SkinObject
from repoze.bfg.skins.interfaces import ISkinObject
from repoze.bfg.skins.interfaces import ISkinObjectFactory

def walk(path):
    os.lstat(path)
    for dir_path, dirs, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dir_path, filename)
            rel_path = full_path[len(path)+1:]
            yield rel_path.replace(os.path.sep, '/'), str(full_path)

def register_skin_object(relative_path, path):
    gsm = getSiteManager()
    ext = os.path.splitext(path)[1]
    factory = gsm.queryUtility(ISkinObjectFactory, name=ext) or \
              SkinObject

    name = factory.component_name(relative_path)
    inst = gsm.queryUtility(ISkinObject, name=name)

    if inst is not None:
        inst.path = path
        inst.refresh()
    else:
        inst = factory(relative_path, path)
        gsm.registerUtility(inst, ISkinObject, name)

def register_skin_view(relative_path, path, kwargs):
    gsm = getSiteManager()

    inst = None
    for inst in gsm.getAllUtilitiesRegisteredFor(ISkinObject):
        if inst.path == path:
            break

    assert inst is not None
    name = type(inst).component_name(relative_path).replace('/', '_')

    context = ConfigurationMachine()
    register_bfg_view(
        context, name=name, view=inst, **kwargs)
    context.execute_actions()

class skins(object):
    def __init__(self, context, path):
        self.context = context
        self.path = path
        self.views = []

    def __call__(self):
        for skin in iter(self):
            yield skin
        for view in self.views:
            yield view

    def __iter__(self):
        for relative_path, path in walk(self.path):
            yield (relative_path, path, ISkinObject), \
                  register_skin_object, \
                  (relative_path, path)

    def view(self, context, **kwargs):
        assert 'name' not in kwargs
        for relative_path, path in walk(self.path):
            view = (relative_path, path, ISkinObject,) + \
                   (kwargs.get('name'), kwargs.get('request_type'),
                    kwargs.get('route_name'), kwargs.get('request_method'),
                    kwargs.get('request_param'), kwargs.get('containment'),
                    kwargs.get('attr'), kwargs.get('renderer'),
                    kwargs.get('wrapper'), kwargs.get('xhr'),
                    kwargs.get('accept'), kwargs.get('header'),
                    kwargs.get('path_info')), \
                    register_skin_view, \
                    (relative_path, path, kwargs)
            self.views.append(view)

class ISkinDirective(interface.Interface):
    path = Path(
        title=u"Path",
        description=u"Path to the directory containing the skin.",
        required=True)

class ITemplatesDirective(interface.Interface):
    directory = Path(
        title=u"Directory",
        description=u"""
        Path to the directory containing the template files.""",
        required=True
        )

    for_ = GlobalObject(
        title=u"The interface or class the view templates are for.",
        required=False
        )

    request_type = GlobalObject(
        title=u"""The request type interface for the view""",
        description=(u"The view will be called if the interface represented by "
                     u"'request_type' is implemented by the request.  The "
                     u"default request type is repoze.bfg.interfaces.IRequest"),
        required=False
        )
    
    class_ = GlobalObject(
        title=(u"Skin template class."),
        required=False,
        )

    permission = TextLine(
        title=u"Permission",
        description=u"The permission needed to use the view templates.",
        required=False
        )

    content_type = TextLine(
        title=u"Content-type",
        description=u"The content-type of the response.",
        required=False
        )

