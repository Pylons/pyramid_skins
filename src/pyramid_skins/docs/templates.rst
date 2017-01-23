.. We set up the skin components from the getting started section
.. behind the scenes.

  >>> _ = xmlconfig("""
  ... <configure xmlns="http://pylonshq.com/pyramid"
  ...            package="pyramid_skins.tests">
  ...   <include package="pyramid_zcml" file="meta.zcml" />
  ...   <include package="pyramid_skins" />
  ...
  ...     <!-- global skin -->
  ...     <skins path="skins" />
  ...
  ...     <!-- request-specific -->
  ...     <skins path="alt_skins"
  ...            request_type=".tests.IAlternativeRequest"
  ...        />
  ...
  ...   </configure>""".strip() % locals())

Templates
=========

Included with the package is a factory for Zope Page Templates (with
the file extension ".pt"). The :mod:`Chameleon` engine is used to
render templates.

Page templates registered as skin objects will be called *skin
templates*. Support is provided to locate other skin templates and
include them as macros.

Skin expression
###############

This package provides a new expression ``skin:`` which will retrieve a
skin object by name::

  tal:define="inst skin: /main_template"

.. -> define_main_template

The pipe operator lets us provide one or more fallback options::

  tal:define="inst skin: /images/logo.gif | /images/logo.png"

.. -> define_logo

  >>> def render_template(string, **context):
  ...     from tempfile import NamedTemporaryFile
  ...     f = NamedTemporaryFile(suffix=".pt")
  ...     f.write(string.encode('utf-8'))
  ...     f.flush()
  ...     from pyramid_skins.zcml import register_skin_object
  ...     register_skin_object(registry, string, f.name, None)
  ...     from pyramid_skins import BindableSkinObject
  ...     inst = BindableSkinObject(string)
  ...     try:
  ...         return inst(**context).body.decode('utf-8')
  ...     finally:
  ...         f.close()

  >>> template = "<div %s tal:replace='inst.path' />"

  >>> print(render_template(template % define_main_template))
  /.../skins/main_template.pt
  >>> print(render_template(template % define_logo))
  /.../skins/images/logo.png

Whitespace is ignored in any case. Skin lookups are either absolute or
relative.

*Absolute*

  If the name begins with a slash ("/") character, it's considered an
  absolute lookup, e.g.::

    /images/logo.png => "images/logo.png"

  This is a placeless lookup.

*Relative*

  If the name does not begin with a slash, it is a placeful lookup.

  Descending from the current path (given a skin template context), we
  attempt to locate the skin object at every parent level.

  For example, the name ``"images/logo.png"`` is relative. If we are
  rendering the about page, then it will map to::

    /about/images/logo.png

  instead of::

    /images/logo.png

  This is similar to *acquisition* (the object is attempted acquired
  from the current context and below). It can be used to redefine skin
  objects for a particular location and below.

  >>> from zope.component import getUtility
  >>> from pyramid_skins.interfaces import ISkinObject
  >>> about = getUtility(ISkinObject, name="about/index")
  >>> print(about(context=u"Hello world!").body.decode('utf-8'))
  <html>
   ... <img src="/about/images/logo.png" /> ...
  </html>

Finally, skins may also be request-specific. In the setup for this
test, we have registered an alternative skins directory for the
standard ``IRequest`` layer. The standard dummy request provides this
layer:

  >>> from pyramid_skins.tests import IAlternativeRequest
  >>> from zope.interface import alsoProvides
  >>> alsoProvides(request, IAlternativeRequest)

We can now see that the 'main_template' skin object is resolved from
the skins path registered for the ``IRequest`` layer
(``"alt_skins"``):

  >>> print(render_template(template % define_main_template))
  /.../alt_skins/main_template.pt

This applies also to the ``SkinObject`` constructor:

  >>> from pyramid_skins import BindableSkinObject
  >>> bound = BindableSkinObject("main_template")
  >>> response = bound()
  >>> print(response.body.decode('utf-8'))
  <html>
    <title>Alternative</title>
    <body>
      Hello template!
    </body>
  </html>

Remove request again.

  >>> from zope.interface import noLongerProvides
  >>> noLongerProvides(request, IAlternativeRequest)

Route expression
################

The ``route:`` expression maps to the ``pyramid.url.route_url``
framework function::

  <img tal:attributes="src string:${route: static}/images/logo.png" />

.. -> source

In the :ref:`framework integration <framework-integration>` section we
learn how you can set up a route to serve up skin objects as static
resources or even views.

  >>> route = add_route("/static", "static")
  >>> print(render_template(source))
  <img src="http://example.com/static/images/logo.png" />

This is a convenient way to compute the URL for static resources. See
the `Pyramid url documentation
<http://docs.pylonsproject.org/projects/pyramid/1.1/api/url.html#pyramid.url.static_url>`_
for more information on URL generation.

Macro support
#############

Skin templates may define macros. Use the standard ``macros``
attribute to reach them::

  <html tal:define="master skin: /main_template"
        metal:use-macro="master.macros['body']">
    <body metal:fill-slot="body">
      Inserted.
    </body>
  </html>

.. -> source

  >>> print(render_template(source))
  <body>
    Inserted.
  </body>

Skin objects can also be used directly as METAL macros. In this case
the entire template is rendered::

  <html metal:use-macro="skin: /main_template">
    <body metal:fill-slot="body">
      Inserted.
    </body>
  </html>

.. -> source

  >>> print(render_template(source))
  <html>
    <body>
      Inserted.
    </body>
  </html>
