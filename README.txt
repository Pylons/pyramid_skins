Overview
========

``repoze.bfg.skins`` provides a framework to register file-system page
templates (ZPT) as components; we'll refer to these templates as "skin
templates".

Templates registered using this framework are available as individual
components within the component architecture and optionally as views,
which are readily available for rendering through the router.

Any skin template may also be invoked as a macro using the METAL
template language.

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
templates and make them available as template components, e.g.::

  <bfg:templates
     directory="templates"
     />

The ``directory`` parameter indicates a package-relative path that
should point at a filesystem directory containing ``chameleon.zpt``
templates with the extension ``.pt``.  Each template located inside
the directory (recursively) becomes a component with a name based on
the relative path to the template file (minus the extension, directory
separators are replaced with a dot).

Optional parameters are ``content_type``, ``request_type``,
``permission`, ``class`` and ``for``.

See the `repoze.bfg view request type documentation
<http://static.repoze.org/bfgdocs/narr/views.html#view-request-types>`_
for more information on request types.

Using the ``class`` parameter, the components registered may be
traversable views::

  <bfg:templates
     directory="templates"
     class="repoze.bfg.skins.SkinTemplateView"
     permission="some_permission"
     />

Each template will be registered as a traversable view component,
optionally protected by a permission.

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


