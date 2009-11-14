Developer's Guide
=================

This interactive narrative is written as a doctest.

You can run the tests by issuing the following command at the
command-line prompt::

$ python setup.py test

In the course of the narrative we will demonstrate different
setups. We have prepared a directory with skin files::

  ./tests/skins
  ./tests/skins/index.pt
  ./tests/skins/images/logo.png
  ./tests/skins/about/index.pt
  ./tests/skins/about/images/logo.png

We will use the ZCML configuration language to register this structure
for use as skins. The following ``configure`` function loads in a ZCML
configuration string.

  >>> from repoze.bfg.skins import tests as testing

The ZCML-directive ``skins`` takes a ``path`` argument; we'll provide a
path which points to a directory within the testing harness.

  >>> import os
  >>> path = os.path.join(testing.__path__[0], 'skins')

  >>> testing.configure("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg">
  ...    <include package="repoze.bfg.skins" />
  ...    <skins path="%s" />
  ... </configure>""" % path)

Skin objects as components
--------------------------

After this bit of configuration, our skin objects are available as
components.

  >>> from zope.component import getUtility
  >>> from repoze.bfg.skins.interfaces import ISkinObject

The name of the component is the relative path.

  >>> getUtility(ISkinObject, name="images/logo.png")
  <repoze.bfg.skins.models.SkinObject name="images/logo.png" at ...>

The page template factory strips off the file extension. The file
"index.pt" becomes a skin template with the name "index".

  >>> getUtility(ISkinObject, name="index")
  <repoze.bfg.skins.models.SkinTemplate name="index" at ...>

The component name is available in the ``name`` attribute:

  >>> getUtility(ISkinObject, name="index").name
  u'index'

Descriptor usage
----------------

The ``SkinObject`` class works as a descriptor. This is useful to tie
user interface classes with skin files with a weak binding.

  >>> from repoze.bfg.skins import SkinObject

Use it as a class attribute.

  >>> class MyClass(object):
  ...     index = SkinObject("index")
  ...     logo = SkinObject("images/logo.png")

The property works on the class itself, and on instances.

  >>> MyClass.index
  <repoze.bfg.skins.models.SkinTemplate name="index" at ...>
  >>> MyClass.logo
  <repoze.bfg.skins.models.SkinObject name="images/logo.png" at ...>

Or directly as a view function::

  >>> index_view = SkinObject("index")

The view function takes context and request arguments, but we can get
away with trivial arguments for now.

  >>> print index_view(None, None).body
  <html>
    <body>
      Hello, world!
    </body>
  </html>

View registration
-----------------

We can register views for skin objects by wrapping a ``view``
directive in the ``skins`` directive.

There are no required arguments to the ``view`` directive:

  >>> testing.configure("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg">
  ...    <include package="repoze.bfg.skins" />
  ...    <skins path="%s">
  ...      <view />
  ...    </skins>
  ... </configure>""" % path)

The BFG framework function ``render_view_to_response`` lets us look up
views by name and retrieve a response object for a given ``context``
and ``request``.

  >>> context = testing.DummyContext()
  >>> request = testing.DummyRequest("")
  >>> from repoze.bfg.view import render_view_to_response

Note in the example how the directory separator character has been
replaced by an underscore.

  >>> response = render_view_to_response(
  ...    context, request, name="images_logo.png")
  >>> response.status
  '200 OK'
  >>> response.content_type
  'image/png'

The page template view first renders the template before returning the
response.

  >>> response = render_view_to_response(
  ...    context, request, name="index")
  >>> response.status
  '200 OK'
  >>> response.content_type
  'text/html'

The response body contains the rendered page template:

  >>> print response.body
  <html>
    <body>
      Hello, world!
    </body>
  </html>

The view directive accepts a ``index`` option; optionally use it to
specify an index filename for directories, e.g.

  >>> testing.configure("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg">
  ...    <include package="repoze.bfg.skins" />
  ...    <skins path="%s">
  ...      <view index="index.pt" />
  ...    </skins>
  ... </configure>""" % path)

This registers index views for each directory:

  >>> response = render_view_to_response(
  ...    context, request, name="")
  >>> response.status
  '200 OK'
  >>> response.content_type
  'text/html'

  >>> response = render_view_to_response(
  ...    context, request, name="about")
  >>> response.status
  '200 OK'
  >>> response.content_type
  'text/html'

Routes
------

Now that we have views registered, let's configure a route.

  >>> testing.configure("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg">
  ...    <include package="repoze.bfg.skins" />
  ...    <route
  ...       name="test"
  ...       path="/*subpath"
  ...       factory="repoze.bfg.skins.RoutesTraverserFactory"
  ...       />
  ... </configure>""")

To try it out, we'll configure a router to use the components we've
set up.

  >>> from repoze.bfg.router import Router
  >>> from zope.component import getSiteManager
  >>> router = Router(getSiteManager())

We need to set the root factory to the routes mapper.

  >>> from zope.component import getUtility
  >>> from repoze.bfg.interfaces import IRoutesMapper
  >>> router.root_factory = getUtility(IRoutesMapper)

Our "test" route lets us pass in any valid skin path:

  >>> testing.DummyRequest("/images/logo.png").get_response(router)
  <Response at ... 200 OK>
  >>> testing.DummyRequest("/index").get_response(router)
  <Response at ... 200 OK>

Templates
---------

Included with the package is functionality to support interaction
between templates registered as skin components.

An expression type ``skin`` is available for page templates to look up
other skin components by name.

  >>> from chameleon.zpt.template import PageTemplate
  >>> template = PageTemplate("""
  ... <html tal:define="master skin: /index" metal:use-macro="master.macros['main']">
  ...    <body metal:fill-slot="body">
  ...       <h1>Welcome</h1>
  ...       <img src="${route: test}/images/logo.png" />
  ...    </body>
  ... </html>""")

  >>> print template.render(context=context, request=request)
  <html>
    <body>
      <h1>Welcome</h1>
      <img src="http://localhost/images/logo.png" />
    </body>
  </html>

  >>> print MyClass.index.render()
  <html>
    <body>
      Hello, world!
    </body>
  </html>

The ``about/index`` template illustrates relative skin object lookup::

  >>> from repoze.bfg.view import render_view
  >>> print render_view(context, request, name="about")
  <html>
   ... <img src="/about/images/logo.png" /> ...
  </html>
