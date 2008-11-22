from zope import interface
from zope import component

from api import TemplateAPI

import interfaces

def get_skin_template(context, request, name):
    gsm = component.getSiteManager()
    return gsm.adapters.lookup(
        map(interface.providedBy, (context, request)),
        interfaces.ISkinTemplate, name=name)

def render_skin_template_to_response(context, request, name):
    return component.queryMultiAdapter(
        (context, request), ISkinTemplate, name)

def render_skin_template(context, request, name):
    response = render_skin_template_to_response(context, request, name)
    if response is not None:
        return response.body