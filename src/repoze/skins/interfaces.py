from zope import interface

from repoze.bfg.interfaces import IView

class IMacro(interface.Interface):
    pass

class ISkinTemplate(IView):
    path = interface.Attribute("""The full path to the template""")
