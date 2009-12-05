.. We set up the skin components from the getting started section
.. behind the scenes.

  >>> from zope.configuration.xmlconfig import string
  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg"
  ...            package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   <include package="repoze.bfg.skins" />
  ...   <skins path="skins" />
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
  >>> template = "<div %s tal:replace='inst.name' />"
  >>> print PageTemplate(template % define_main_template)()
  main_template
  >>> print PageTemplate(template % define_logo)()
  images/logo.png

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

  This is akin to *acquisition* (the object is attempted acquired from
  the current context and below). It can be used to redefine skin
  objects for a particular location and below.

  >>> from zope.component import getUtility
  >>> from repoze.bfg.skins.interfaces import ISkinObject
  >>> about = getUtility(ISkinObject, name="about/index")
  >>> print about(context=u"Hello world!").body
  <html>
   ... <img src="/about/images/logo.png" /> ...
  </html>

Route expression
################

The ``route:`` expression maps to the ``repoze.bfg.url.route_url``
framework function::

  <img tal:attributes="src string:${route: static}/images/logo.png" />

.. -> source

In the :ref:`framework integration <framework-integration>` section we learn how you can set
up a route to serve up skin objects as static resources or even views.

  >>> from repoze.bfg.testing import registerRoute
  >>> registerRoute("/static", "static")
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
