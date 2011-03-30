.. We set up the skin components from the getting started section
.. behind the scenes.

  >>> from zope.configuration.xmlconfig import string
  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg"
  ...            package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   <include package="repoze.bfg.skins" />
  ...
  ...     <!-- global skin -->
  ...     <skins path="skins" />
  ...
  ...     <!-- request-specific -->
  ...     <skins path="alt_skins" request_type="repoze.bfg.interfaces.IRequest" />
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

  tal:define="inst skin: /images/logo.gif | skin: /images/logo.png"

.. -> define_logo

  >>> from chameleon.zpt.template import PageTemplate
  >>> template = "<div %s tal:replace='inst.path' />"
  >>> print PageTemplate(template % define_main_template)()
  /.../skins/main_template.pt
  >>> print PageTemplate(template % define_logo)()
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
  >>> from repoze.bfg.skins.interfaces import ISkinObject
  >>> about = getUtility(ISkinObject, name="about/index")
  >>> print about(context=u"Hello world!").body
  <html>
   ... <img src="/about/images/logo.png" /> ...
  </html>

Finally, skins may also be request-specific. In the setup for this
test, we have registered an alternative skins directory for the
standard ``IRequest`` layer. The standard dummy request provides this
layer:

  >>> from repoze.bfg.threadlocal import manager
  >>> from repoze.bfg.testing import DummyRequest
  >>> manager.get()['request'] = DummyRequest()

We can now see that the 'main_template' skin object is resolved from
the skins path registered for the ``IRequest`` layer
(``"alt_skins"``):

  >>> print PageTemplate(template % define_main_template)()
  /.../alt_skins/main_template.pt

This applies also to the ``SkinObject`` constructor:

  >>> from repoze.bfg.skins import SkinObject
  >>> SkinObject("main_template").__get__().path
  '/.../alt_skins/main_template.pt'

Remove request again.

  >>> manager.get()['request'] = None

Route expression
################

The ``route:`` expression maps to the ``repoze.bfg.url.route_url``
framework function::

  <img tal:attributes="src string:${route: static}/images/logo.png" />

.. -> source

In the :ref:`framework integration <framework-integration>` section we learn how you can set
up a route to serve up skin objects as static resources or even views.

  >>> from repoze.bfg.testing import registerRoute
  >>> route = registerRoute("/static", "static")
  >>> from chameleon.zpt.template import PageTemplate
  >>> template = PageTemplate(source)
  >>> from repoze.bfg.testing import DummyRequest
  >>> print template(request=DummyRequest())
  <img src="http://example.com/static/images/logo.png" />

This is a convenient way to compute the URL for static resources. See
the `repoze.bfg url documentation
<http://docs.repoze.org/bfg/1.1/api/url.html#repoze.bfg.url.static_url>`_
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

  >>> template = PageTemplate(source)
  >>> print template()
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

  >>> template = PageTemplate(source)
  >>> print template()
  <html>
    <body>
      Inserted.
    </body>
  </html>
