import os

from zope import interface
from zope import component
from zope.component import getGlobalSiteManager
from zope.component.zcml import handler
from zope.component.interface import provideInterface

from zope.schema import TextLine

from zope.configuration.fields import \
     GlobalObject, GlobalInterface, Tokens, Path
from zope.configuration.config import ConfigurationMachine

from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import INewRequest
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import ISettings

from repoze.bfg.security import ViewPermissionFactory

from chameleon.zpt.template import PageTemplateFile

from interfaces import ISkinMacro
from interfaces import ISkinTemplate

from template import SkinTemplate

def find_templates(path):
    os.lstat(path)
    for dirpath, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".pt"):
                fullpath = os.path.join(dirpath, filename)
                rel_path = fullpath[len(path)+1:]
                # the template name is given by the relative path
                # where the path separator is replaced by a dot '.'
                # and the file extension removed
                name = os.path.splitext(rel_path.replace(os.path.sep, '/'))[0]
                yield name, fullpath

class DirectoryRegistrationFactory(object):
    def __init__(self, directory, for_, provides, request_type, permission):
        self.directory = directory
        self.for_ = for_
        self.permission = permission
        self.provides = provides
        self.request_type = request_type

    def __call__(self, event=None, context=None, force_reload=False):
        if force_reload is False:
            settings = component.queryUtility(ISettings)
            auto_reload = settings and settings.reload_templates
            if not auto_reload:
                return

        if context is None:
            _context = ConfigurationMachine()
        else:
            _context = context
            
        gsm = getGlobalSiteManager()
        
        iface = self.for_ or interface.Interface
        if type(iface) is not interface.interface.InterfaceClass:
            iface = interface.implementedBy(iface)
                
        for name, fullpath in find_templates(self.directory):
            view = SkinTemplate(fullpath)

            for provides in self.provides:
                template = gsm.adapters.lookup(
                    (iface, self.request_type), provides, name=name)
                if template is not None:
                    continue

                # if the skin template is to provide a view, we may need
                # to register a permission adapter for it
                if provides.isOrExtends(IView) and self.permission:
                    pfactory = ViewPermissionFactory(self.permission)
                    _context.action(
                        discriminator = ('permission', self.for_, name,
                                         self.request_type, IViewPermission),
                        callable = handler,
                        args = ('registerAdapter',
                                pfactory, (self.for_, self.request_type),
                                IViewPermission, name, _context.info),
                        )

                # register the skin template component for this
                # specification
                _context.action(
                    discriminator = ('view', self.for_, name,
                                     self.request_type, provides),
                    callable = handler,
                    args = ('registerAdapter',
                            view, (self.for_, self.request_type), provides, name,
                            _context.info),
                    )

        # if no configuration context was supplied, execute the actions
        if context is None:
            _context.execute_actions()

def templates(_context, directory, for_=None, provides=(ISkinMacro,),
              request_type=IRequest, permission=None, content_type=None):
    # if a permission is required, make sure we're registering a view;
    # otherwise, it makes no sense and we should raise an error
    if permission is not None:
        if True not in [iface.isOrExtends(IView) for iface in provides]:
            raise ValueError(
                "Can only require permission when a view is provided.")

    # if none of the interface provide the ``ISkinTemplate``
    # interface, we provide it by default
    provides = list(provides)
    if True not in [iface.isOrExtends(ISkinTemplate) for iface in provides]:
        provides.append(ISkinTemplate)

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )

    # we register a separate handler to register the templates; we
    # will call it immediately and with every new request (in order to
    # pick up new templates on the fly, if the ``reload_templates``
    # setting is set).
    factory = DirectoryRegistrationFactory(
        directory, for_, provides, request_type, permission)
    
    _context.action(
        discriminator = ('registerHandler', id(factory), INewRequest),
        callable = handler,
        args = ('registerHandler', factory, (INewRequest,), '', '',
                False),
        )

    factory(context=_context, force_reload=True)

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

    provides = Tokens(
        title=(u"The interface which the template components should "
               u"additionally provide."),
        required=False,
        value_type=GlobalInterface(),
        )

    request_type = GlobalObject(
        title=u"""The request type interface for the view""",
        description=(u"The view will be called if the interface represented by "
                     u"'request_type' is implemented by the request.  The "
                     u"default request type is repoze.bfg.interfaces.IRequest"),
        required=False
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

