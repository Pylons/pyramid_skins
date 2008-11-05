import os

from zope import interface
from zope import component
from zope.component import getGlobalSiteManager
from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.fields import GlobalObject, Path

from zope.schema import TextLine

from webob import Response

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import INewRequest
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import ISettings
from repoze.bfg.security import ViewPermissionFactory

from chameleon.zpt.template import PageTemplateFile

from macros import Macros
from api import Api
from interfaces import IMacro
from interfaces import ISkinTemplate

def find_templates(path):
    os.lstat(path)
    for dirpath, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".pt"):
                fullpath = os.path.join(dirpath, filename)
                rel_path = fullpath[len(path)+1:]
                name = os.path.splitext(rel_path.replace(os.path.sep, '/'))[0]
                yield name, fullpath

class TemplateViewFactory(object):
    interface.implements(ISkinTemplate)
    
    def __init__(self, path):
        self.template = PageTemplateFile(path)
        self.name, ext = os.path.splitext(os.path.basename(path))
        self.path = path

    def __call__(self, context, request, **kwargs):
        result = self.render(context, request, **kwargs)
        return Response(result)

    def render(self, context, request, **kwargs):
        macros = Macros(context, request)
        api = Api(context, request, self)
        return self.template(
            context=context, request=request, macros=macros, api=api, **kwargs)

class TemplateMacroFactory(object):
    def __init__(self, template_name):
        self.skin_template = TemplateViewFactory(template_name)
        
    def __call__(self, context, request):
        def macro(context, request):
            template = self.skin_template.template
            api = Api(context, request, self.skin_template)
            return template.macros.bind(
                context=context, request=request, api=api)[""]
        return macro(context, request)

class EventHandlerFactory(object):
    def __init__(self, directory, for_, provides, request_type, permission):
        self.directory = directory
        self.for_ = for_
        self.permission = permission
        self.provides = provides
        self.request_type = request_type

    def __call__(self, event):
        settings = component.queryUtility(ISettings)
        auto_reload = settings and settings.reload_templates
        if not auto_reload:
            return

        gsm = getGlobalSiteManager()
        for name, fullpath in find_templates(self.directory):
            iface = self.for_ or interface.Interface
            if type(iface) is not interface.interface.InterfaceClass:
                iface = interface.implementedBy(iface)
                
            view = gsm.adapters.lookup(
                    (iface, self.request_type), self.provides, name)
            if view is None:
                # permission
                if self.permission:
                    pfactory = ViewPermissionFactory(self.permission)
                    component.registerAdapter(
                            pfactory,
                            (self.for_, self.request_type),
                            IViewPermission,
                            name)

                # template as view
                view = TemplateViewFactory(fullpath)
                component.provideAdapter(
                    view, (self.for_, self.request_type), self.provides, name)

                # template as macro
                macro = TemplateMacroFactory(fullpath)
                component.provideAdapter(
                    macro, (self.for_, self.request_type), IMacro, name)

def templates(_context, directory, for_=None, provides=interface.Interface,
              request_type=IRequest, permission=None):
    # provide interface
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )

    class _ISkinTemplate(provides, ISkinTemplate):
        """Dynamically created interface which provides ``%s`` in
        addition to ``ISkinTemplate``.""" % provides.__name__
        
    event_handler = EventHandlerFactory(
        directory, for_, _ISkinTemplate, request_type, permission)
    
    _context.action(
        discriminator = ('registerHandler', id(event_handler), INewRequest),
        callable = handler,
        args = ('registerHandler', event_handler, (INewRequest,), '', '',
                False),
        )

    for name, fullpath in find_templates(directory):
        # the view name is given by the relative path where the path
        # separator is replaced by a dot '.' and the file extension
        # removed
        
        # register permissions adapter if required
        if permission:
            pfactory = ViewPermissionFactory(permission)
            _context.action(
                discriminator = ('permission', for_,name, request_type,
                                 IViewPermission),
                callable = handler,
                args = ('registerAdapter',
                        pfactory, (for_, request_type), IViewPermission, name,
                        _context.info),
                )

        # register template as view component
        view = TemplateViewFactory(fullpath)
        _context.action(
            discriminator = ('view', for_, name, request_type, _ISkinTemplate),
            callable = handler,
            args = ('registerAdapter',
                    view, (for_, request_type), _ISkinTemplate, name,
                    _context.info),
            )

        # register template as macro component
        macro = TemplateMacroFactory(fullpath)
        _context.action(
            discriminator = ('view', for_, name, request_type, IMacro),
            callable = handler,
            args = ('registerAdapter',
                    macro, (for_, request_type), IMacro, name,
                    _context.info),
            )
        
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

    provides = GlobalObject(
        title=(u"The interface which the template components should "
               u"additionally provide."),
        required=False,
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

