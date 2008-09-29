Overview
========

``repoze.skins`` provides component-based templates that may be used
both as views and template macros. It's compatible with the
``repoze.bfg`` framework.

We'll refer to these templates as "skin templates".


Including the ``repoze.skins`` ZCML
----------------------------------

Within your repoze.bfg application package, include the
``repoze.skins`` ZCML registrations by modifying your application's
``configure.zcml``.  Add the following ZCML to that file::

  <include package="repoze.skins" file="meta.zcml"/>

  
Templates as views
------------------

Once you've included the ``repoze.skins`` ZCML, you may use the
ZCML directive ``<bfg:templates>`` to register a directory with
templates and make them available as view components, complete with
security and adaptation::

  <bfg:templates
     directory="templates"/>

The ``directory`` parameter indicates a package-relative path that
should point at a filesystem directory containing ``chameleon.zpt``
templates with the extension ``.pt``.  Each template located inside
the directory (recursively) becomes a view component and given a name
based on the relative path to the template file (minus the extension,
directory separators are replaced with a dot).

The skin template components are callables and return a WSGI response
object.

You can override which "request type" the skin is for by using the
``request_type`` attribute::

  <bfg:templates
     request_type="mypackage.interfaces.MyRequestType"
     directory="templates"/>

See the `repoze.bfg view request type documentation
<http://static.repoze.org/bfgdocs/narr/views.html#view-request-types>`_
for more information on request types.

If you want to protect your templates with a specific permission, you
may as well by using the ``permission`` directive::

  <bfg:templates
     permission="view"
     directory="templates"/>

If you want the templates to only be displayed for specific context
(model) types, use the for parameter::

  <bfg:templates
     for="myproject.models.MyModel"
     directory="templates"/>

The ``request_type``, ``permission`, and ``for`` parameters can be
combined freely.


Templates as macros
-------------------

Templates are also available as METAL macros using the symbol
``macros`` which is available to all skin templates (it may be
instantiated manually, too).

The ``macros`` object is tied to the current request; the context is
the template context, if one does not explicitly provide one. The
usage of the ``macros`` object is demonstrated below::

   <div metal:use-macro="macros.thumbnail" />
   <div metal:use-macro="macros(some_context).thumbnail" />

As with all METAL macros, the macro slot functionality is available.


Template API support
--------------------

To aid template designers, applications and libraries can make APIs
available to templates. Simply register a named component for the
``repoze.skins.interfaces.IApi`` interface that adapts on (context,
request).

In the template, get the api by using the ``api`` symbol:

  <div tal:define="my_api api.my_api" />

The ``api`` symbol is available to all skin templates.


Automatic detection of new templates
------------------------------------

In debug-mode, skin templates are automatically picked up and
registered. The way this works is that there's an event listener
registered for the ``repoze.bfg.interfaces.INewRequest`` event such
that directories are searched for new files before any application
logic is run, prior to each request.


Credits
-------

This package was put together by Malte Borch <mborch@gmail.com>. To
contribute to development or for support, please visit either #repoze
on freenode irc.

