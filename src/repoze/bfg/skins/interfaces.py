from zope import interface

from repoze.bfg.interfaces import IView

class ISkinTemplate(interface.Interface):
    """Skin templates are page templates which reside in a skin
    directory. These are registered as named components adapting on
    (context, request)."""

    name = interface.Attribute(
        """This is the basename of the template filename relative to
        the skin directory. Note that the OS-level path separator
        character is replaced with a forward slash ('/').""")

    path = interface.Attribute(
        """Full path to the template. This attribute is available to
    allow applications to get a reference to files that relate to the
    template file, e.g. metadata or additional resources. An example
    could be a title and a description, or a icon that gives a visual
    representation for the template.""")

    def render(context, request):
        """Render the template and return a unicode string."""

    def get_api(name):
        """Look up skin api by name."""

    def get_macro(name):
        """Look up skin macro by name."""

class ISkinMacro(ISkinTemplate):
    """Skin template components provide this interface by default,
    which enables them for use as macros."""
        
class ISkinApi(interface.Interface):
    """A helper component available to skin templates. Skin APIs
    should be registered as named components adapting on (context,
    request, template)."""

class ISkinApiMethod(interface.Interface):
    """Skin API methods are an alternative to a generic API and get
    the chance of having arguments passed."""
