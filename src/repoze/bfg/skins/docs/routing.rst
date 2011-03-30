.. _framework-integration:

Routing
=======

The package comes with support for routing URLs to skin objects. This
works with resources -- images, stylesheets and other static files --
and templates (these are rendered into a response).

For BFG to render the skin objects, we must register views such that
the router can publish them. The benefit is that we can reuse the
``view`` directive and even protect the views with permissions.

Adding views
############

To expose the contents of a skin directory as *views*, we can insert a
``view`` registration directive into the ``skins`` directive::

  <skins path="skins">
     <view />
  </skins>

.. -> configuration

  >>> from zope.configuration.xmlconfig import string
  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   <include package="repoze.bfg.skins" />
  ...   %(configuration)s
  ... </configure>""".strip() % locals())
  >>> from repoze.bfg.view import render_view
  >>> from repoze.bfg.testing import DummyRequest
  >>> render_view('Hello world!', DummyRequest(), name="") is None
  True
  >>> print render_view('Hello world!', DummyRequest(), name="index")
  <html>
    <body>
      Hello world!
    </body>
  </html>

The ``view`` directive has no required attributes, but all the
attributes which are applicable for the standalone directive [#]_ are
available, except ``name`` which is defined by the component and
``view`` which is given by the skin object.

.. note:: Views are registered using the component name. However, the directory separator character ("/") is replaced by an underscore (e.g. "images/logo.png" becomes "images_logo.png"). This is a technical detail if you use the built-in routing functionality.

When wrapped inside ``skins``, an option ``index`` is available to
allow registering default index views (e.g. ``index.pt``)::

  <skins path="skins">
     <view index="index.pt" />
  </skins>

.. -> configuration

  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   <include package="repoze.bfg.skins" />
  ...   %(configuration)s
  ... </configure>""".strip() % locals())
  >>> print render_view('Hello world!', DummyRequest(), name="")
  <html>
    <body>
      Hello world!
    </body>
  </html>

When an index name is set, a view is registered for the directory
path, mapped to the index object in the directory.

.. [#] See the `repoze.bfg view request type documentation <http://static.repoze.org/bfgdocs/narr/views.html#view-request-types>`_ for more information on request types.

Route factory
#############

We can configure a route to serve up skins registered as views under
some path -- ``subpath`` -- using the provided routes traverser
factory::

  <route
     name="skins"
     path="/static/*subpath"
     factory="repoze.bfg.skins.RoutesTraverserFactory"
     use_global_views="True"
     />

.. -> configuration

  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   %(configuration)s
  ... </configure>""".strip() % locals())
  >>> from repoze.bfg.threadlocal import get_current_registry
  >>> registry = get_current_registry()
  >>> from repoze.bfg.router import Router
  >>> router = Router(registry)
  >>> environ = {
  ...     'wsgi.url_scheme':'http',
  ...     'SERVER_NAME':'localhost',
  ...     'SERVER_PORT':'8080',
  ...     'REQUEST_METHOD':'GET',
  ...     'PATH_INFO':'/static/images/logo.png',
  ...     }
  >>> def start_response(*args): print args
  >>> from repoze.bfg.interfaces import IRoutesMapper
  >>> from zope.component import getUtility
  >>> router.root_factory = getUtility(IRoutesMapper)
  >>> app_iter = router(environ, start_response)
  ('200 OK', [('Content-Length', '2833'), ('Content-Type', 'image/png')])

This traverser will convert ``subpath`` into a view name which then
prompts the BFG router to publish the skin object (by calling it).
