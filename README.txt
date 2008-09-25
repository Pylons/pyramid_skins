Overview
========

``repoze.skins`` provides component-based templates that may be used
both as views and template macros. It's compatible with the
``repoze.bfg`` framework.

We'll refer to these templates as "skin templates".

Templates as views
------------------

Using the ZCML-directive ``<bfg:templates>`` we can register a
directory with templates and make them available as view components,
complete with security and adaptation::

  <bfg:templates
     for="some_specification"
     layer="some_request_layer"
     directory="templates"
     permission="view" />

Each template located inside the directory becomes a view component
and given a name based on the relative path to the template file
(minus the extension, directory separators are replaced with a dot).

The skin template components are callables and return a WSGI response
object.

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

Credits
-------

This package was put together by Malte Borch <mborch@gmail.com>. To
contribute to development or for support, please visit either #repoze
on freenode irc.

