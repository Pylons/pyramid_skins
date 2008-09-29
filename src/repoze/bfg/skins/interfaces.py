from zope import interface

from repoze.bfg.interfaces import IView

class IMacro(interface.Interface):
    """Macros API available to templates. Access skin template macros
    by name using attribute access, e.g. ``macros.my_template_name``."""

class IApi(interface.Interface):
    """An application programming interface available to
    templates. Register as a named component that adapts on (context,
    request)."""
    
class ISkinTemplate(IView):
    """Skin template view."""
    
    path = interface.Attribute(
        """Full path to the template. This attribute is available to
    allow applications to get a reference to files that relate to the
    template file, e.g. metadata or additional resources. An example
    could be a title and a description, or a icon that gives a visual
    representation for the template.""")
