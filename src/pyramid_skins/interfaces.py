from zope import interface
from pyramid.interfaces import IView


class ISkinObject(interface.Interface):
    name = interface.Attribute(
        """Component name.""")

    def refresh():
        """Refresh object from file on disk (reload)."""


class ISkinObjectFactory(interface.Interface):
    def component_name(relative_path):
        """Returns a component name. This method must be a
        class- or static method."""


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

    def __call__(context, request):
        """Returns a bound skin template instance."""

    def get_api(name):
        """Look up skin api by name."""

    def get_macro(name):
        """Look up skin macro by name."""


class IBoundSkinTemplate(ISkinTemplate):
    """Bound to a context and request."""

    def __call__(**kwargs):
        """Renders template to a response object."""

    def render(**kwargs):
        """Renders template to a unicode string, passing optional
        keyword-arguments."""


class ISkinTemplateView(IView):
    """When skin templates are set to provide one or more interfaces,
    a component providing this interface will be registered."""

    template = interface.Attribute(
        """The skin template object.""")

    def __call__():
        """Renders template to a response object."""

    def render(**kwargs):
        """Renders template to a unicode string, passing optional
        keyword-arguments."""


class ISkinApi(interface.Interface):
    """A helper component available to skin templates. Skin APIs
    should be registered as named components adapting on (context,
    request, template)."""


class ISkinApiMethod(interface.Interface):
    """Skin API methods are an alternative to a generic API and get
    the chance of having arguments passed."""
