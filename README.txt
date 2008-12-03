Overview
========

``repoze.bfg.skins`` provides a framework to register file-system page
templates (ZPT) as components; we'll refer to these templates as "skin
templates".

Templates registered using this framework double as template macros in
the sense that a mechanism is exposed to easily look up and render a
skin template as a macro from inside a template.

Package configuration
---------------------

Within your repoze.bfg application package, include the ZCML
configuration by adding the following statement to your
project's ``configure.zcml`` file::

  <include package="repoze.bfg.skins" file="meta.zcml"/>

Registering templates
---------------------

Once you've included the ``repoze.bfg.skins`` ZCML, you may use the
ZCML directive ``<bfg:templates>`` to register a directory with
templates and make them available as view components, complete with
security and adaptation::

  <bfg:templates
     directory="templates"/>

The ``directory`` parameter indicates a package-relative path that
should point at a filesystem directory containing ``chameleon.zpt``
templates with the extension ``.pt``.  Each template located inside
the directory (recursively) becomes a component with a name based on
the relative path to the template file (minus the extension, directory
separators are replaced with a dot).

Note that templates will only be available as traversable views if you
explicitly name the ``IView`` interface::

  <bfg:templates
     provides="repoze.bfg.interfaces.IView"
     directory="templates"/>
     
Skin template components are callables and return a WSGI response
object (like all ``repoze.bfg`` views).

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

The ``provides``, ``request_type``, ``permission`, and ``for``
parameters are all optional.

Macro support
-------------

Templates are also available as METAL macros using the function
``get_macro`` which is available from the ``template`` symbol to all
skin templates.

The ``template`` symbol is tied to the current context and
request. The usage of the ``macros`` object is demonstrated below::

   <div metal:use-macro="template.get_macro('thumbnail')" />
   <div metal:use-macro="template.get_macro('thumbnail', context)" />

A more elaborate example demonstrating macro slot support::

   <div metal:use-macro="template.get_macro('thumbnail')">
      <span metal:fill-slot="label">
         This is a thumbnail
      <span>
   </div>

Providing custom skin APIs 
--------------------------

Helper utilities can be registered as skin apis and pulled in using
the utility function ``get_api``, which is available from the
``template`` symbol.

They must be registered as named component providing the ``ISkinApi``
interface, adapting on (context, request, template). A base class is
provide for convenience:

  >>> from repoze.bfg.skins.template import SkinApi

To look up a template API, simply use attribute-access on the ``api``
symbol.

  <div tal:define="api template.get_api('custom')" />

Automatic detection of new template files
-----------------------------------------

When the global configuration option ``auto_reload`` is set to "true",
skin templates are found at run-time.

Contributors
------------

Malthe Borch <mborch@gmail.com>
Stefan Eletzhofer <stefan.eletzhofer@inquant.de>

To contribute to development or get support, please visit the #repoze
channel on freenode irc or write the mailinglist.


