Overview
========

.. role:: mod(emphasis)
.. role:: term(emphasis)

This package provides a framework to make files in a directory
structure available as *skin* components (the term originates from the
CMF package which provides comparable functionality on Zope
2). There's built-in integration with routes, views and components.

Skins make separation of library code and presentation easy, and come
with a customization story. An example of usage within library code is
a view class::

  class FrontPage(object):
      __call__ = SkinObject("site/frontpage")

When the ``template`` attribute is accessed on an instance of this
class, the skins framework looks up the object by the name
``site/frontpage``.

The ``site/frontpage`` object could appear in the file system as::

  /.../skins/site/frontpage.pt

Where the ``skins`` directory is the registration mount point. Note
that the file extension is excluded from the object name. This is a
behavior of the skin template factory which is associated with the
``.pt`` extension). Custom factories for other file extensions can be
registered (see `application setup`_).

If another skin directory contains an object by the same name, the
most recent registration takes priority, e.g.::

  /.../custom-skins/site/frontpage.pt

An alternative spelling which makes it easy to use skin objects as
views is::

  front_page = SkinObject("site/frontpage")

The ``front_page`` is now a callable which takes ``context`` and
``request``, similar to BFG views. Note that skin objects may be
exposed as views automatically (see views_ for instructions). This
makes it easy to publish some directory of files, be it static
(e.g. images, stylesheets) or dynamic (e.g. templates).

About
-----

The package is written and maintained by `Malthe Borch
<mailto:mborch@gmail.com>`_ and `Stefan Eletzhofer
<stefan.eletzhofer@inquant.de>`_. Available as-is under the BSD license.

To contribute or get support for this package, please visit the
#repoze channel on freenode irc or write to the `repoze-dev mailinglist <repoze-dev@lists.repoze.org>`_.

Usage
=====

The package allows configuration using the ZCML language. The ``skin``
directive is defined in the ``meta.zcml`` file::

  <include package="repoze.bfg.skins" file="meta.zcml" />

To configure all the included components (recommended), include the
package instead::

  <include package="repoze.bfg.skins" />

Application setup
-----------------

Once you've included the ``repoze.bfg.skins`` ZCML, you may use the
ZCML-directive ``<bfg:skins>`` to register a directory with templates
and make them available as template components, e.g.:::

  <bfg:skins path="skins" />

The ``path`` parameter indicates a relative path which contains the
skin object files.

The ``skins`` directive makes available skin components for use in
library code. The default factory (see Factories_) simply uses the
relative path as the component name; some factories may strip off the
file extension (this is the case for the page template factory).

.. _views:

To expose the contents of a skin directory as *views*,
we can insert a ``view`` registration directive into the ``skins``
directive::

  <bfg:skins path="skins">
     <bfg:view />
  </bfg:skins>

The ``view`` directive has no required attributes, but all the
attributes which are applicable for the standalone directive [#]_ are
available, except ``name`` which is defined by the component and
``view`` which is given by the skin object.

When wrapped inside ``skins``, an option ``index`` is available to
allow registering default index views (e.g. index.pt)::

  <bfg:skins path="skins">
     <bfg:view index="index.pt" />
  </bfg:skins>

.. note:: Views are registered using the component name. However, the directory separator character ("/") is replaced by an underscore (e.g. "document/view.pt" becomes "document_view").

.. [#] See the `repoze.bfg view request type documentation <http://static.repoze.org/bfgdocs/narr/views.html#view-request-types>`_ for more information on request types.

Routes integration
------------------

Every skin component corresponds to a relative path. We can configure a
route to map a subpath to skin components for which a view is
registered::

  <route
     name="skins"
     path="/content/*subpath"
     factory="repoze.bfg.skins.RoutesTraverserFactory"
     />

This traverser will convert the subpath into a view name and let BFG
render the view if possible.

View integration
----------------

Skin components are registered as named utilities. We can use the
``getUtility`` function to retrieve a skin component by name.

For convenience, the ``SkinObject`` class doubles as a descriptor
which can be used as a class attribute; it uses a ``getUtility`` call
when accessed::

  class MyView(object):
      __call__ = SkinObject("document_view")

The weak binding to the skin object makes it easy to depend on skin
components from library code without a hard dependency.

.. _Factories:

Factories
=========

The skin objects are instances of the ``SkinObject`` base class. We
may associate a custom factory for particular file extensions::

    class MySkinObject(SkinObject):
        pass

We register the class as a named utility component::

    <utility
       name=".my"
       component=".MySkinObject"
       provides="repoze.bfg.skins.interfaces.ISkinObjectFactory"
       />

Page template factory
---------------------

Included with the package is a factory for Zope Page Templates (with
the file extension ".pt"). The Chameleon rendering engine is used.

Page templates registered as skin objects will be called *skin
templates*. Support is provided to locate other skin templates and
include them as macros. This is made pluggable such that applications
can add additional functionality.

This package provides a new expression ``skin:`` which will retrieve a
skin object by name:

The skin object factory for page templates provide the ``macros``
attribute. The following snippet illustrates this::

  <div
    tal:define="master skin: main_template"
    metal:use-macro="master.macros['main']"
    />

The ``route:`` expression maps to the ``route_url`` framework function:

  <img tal:attributes="src ${route: skins}/images/logo.png" />

.. [#] See the `repoze.bfg url documentation <http://docs.repoze.org/bfg/1.1/api/url.html#repoze.bfg.url.static_url>`_ for more information on URL generation.

Automatic discovery and reload
------------------------------

When the global setting ``debug`` is set (to any non-trivial value),
skin objects are discovered at run-time and files are automatically
reloaded when changed.

