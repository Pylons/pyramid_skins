import os

from zope import component

from zope.configuration import xmlconfig
import zope.configuration.config

from zope.component.zcml import handler
from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalObject, Path
from zope.interface import Interface
from zope.schema import TextLine

from webob import Response

from repoze.bfg.interfaces import IRequest
from repoze.bfg.interfaces import INewRequest
from repoze.bfg.interfaces import IViewPermission
from repoze.bfg.interfaces import IView
from repoze.bfg.path import package_path
from repoze.bfg.security import ViewPermissionFactory

from chameleon.zpt.template import PageTemplateFile

from macros import Macros
from interfaces import IMacro

def find_templates(path):
    os.lstat(path)
    for dirpath, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(".pt"):
                fullpath = os.path.join(dirpath, filename)
                rel_path = fullpath[len(path)+1:]
                name = os.path.splitext(rel_path.replace(os.path.sep, '.'))[0]
                fullname = os.path.join(path, rel_path)
                yield name, fullname, rel_path

def create_view_from_template(template):
    def view(context, request):
        macros = Macros(context, request)
        result = template(
            context=context, request=request, macros=macros)
        return Response(result)
    return view

def create_macro_from_template(template):
    def macro(context, request):
        return template.macros[""]
    return macro

def templates(_context, directory, for_=None, request_type=IRequest,
        permission=None):
    # provide interface
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )


    # register an event-handler that searches directories for new
    # templates
    registry = {}

    def make_template(path):
        template = PageTemplateFile(path)
        registry[path] = template
        return template

    def event_handler(new_request_event):
        for name, fullpath, rel_path in find_templates(directory):
            template = registry.get(fullpath)
            if template is None:
                template = make_template(fullpath)

                # permission
                if permission:
                    pfactory = ViewPermissionFactory(permission)
                    component.registerAdapter(
                            pfactory,
                            (for_, request_type),
                            IViewPermission,
                            name)

                # template as view
                view = create_view_from_template(template)
                component.provideAdapter(view, (for_, request_type), IView, name)

                # template as macro
                macro = create_macro_from_template(template)
                component.provideAdapter(macro, (for_, request_type), IMacro, name)

    _context.action(
        discriminator = ('registerHandler', id(event_handler), INewRequest),
        callable = handler,
        args = ('registerHandler', event_handler, (INewRequest,), '', '',
                False),
        )

    for name, fullpath, rel_path in find_templates(directory):
        # the view name is given by the relative path where the path
        # separator is replaced by a dot '.' and the file extension
        # removed
        template = make_template(fullpath)

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
        view = create_view_from_template(template)
        _context.action(
            discriminator = ('view', for_, name, request_type, IView),
            callable = handler,
            args = ('registerAdapter',
                    view, (for_, request_type), IView, name,
                    _context.info),
            )

        # register template as macro component
        macro = create_macro_from_template(template)
        _context.action(
            discriminator = ('view', for_, name, request_type, IMacro),
            callable = handler,
            args = ('registerAdapter',
                    macro, (for_, request_type), IMacro, name,
                    _context.info),
            )
        
class ITemplatesDirective(Interface):
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
    
    permission = TextLine(
        title=u"Permission",
        description=u"The permission needed to use the view templates.",
        required=False
        )

