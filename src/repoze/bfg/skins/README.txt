Documentation
=============

This section is tested using the :mod:`manuel` library. You can run
the tests from the command-line::

$ python setup.py test

This allows you to make sure the package is compatible with your
platform.

In the course of the narrative we will demonstrate different usage
scenarios. The test setup contains the following files::

  ./skins
  ./skins/index.pt
  ./skins/main_template.pt
  ./skins/images/logo.png
  ./skins/about/index.pt
  ./skins/about/images/logo.png

.. -> output

  >>> import os
  >>> from repoze.bfg.skins import tests
  >>> for filename in output.split('\n'):
  ...     assert os.lstat(
  ...         os.path.join(os.path.dirname(tests.__file__), filename.strip())) \
  ...         is not None

The meaning of this set of skin components is that ``index.pt``
represents some document that we want to publish; it uses
``main_template.pt`` is the o-wrap template. The ``./about`` directory
is some subsection of the site which has its own logo.

Getting started
---------------

We begin by registering the ``skins`` directory. This makes the
files listed above available as skin components. The ZCML-directive
``skins`` makes registration easy::

  <include package="repoze.bfg.skins" />

  <skins path="skins" />

.. -> configuration

.. invisible-code-block: python

  from zope.configuration.xmlconfig import string
  _ = string("""
     <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
     <include package="repoze.bfg.includes" file="meta.zcml" />
       %(configuration)s
     </configure>""".strip() % locals())

  from zope.component import getUtility
  from repoze.bfg.skins.interfaces import ISkinObject
  getUtility(ISkinObject, name="index")

The ``path`` parameter indicates a relative path which defines the
mount point for the skin registration.

Skin components
###############

At this point the skin objects are available as utility
components. This is the low-level interface::

  from zope.component import getUtility
  from repoze.bfg.skins.interfaces import ISkinObject
  index = getUtility(ISkinObject, name="index")

.. -> code

  >>> exec(code)
  >>> assert index is not None

The component name is available in the ``name`` attribute::

  index.name

.. -> expr

  >>> eval(expr)
  u'index'

Skin objects
############

The ``SkinObject`` class itself wraps this utility lookup::

  from repoze.bfg.skins import SkinObject
  FrontPage = SkinObject("index")

.. -> code

  >>> exec(code)
  >>> FrontPage.__get__() is not None
  True

This is now a callable which will render the template to a
response. The first two positional arguments (if given) are mapped to
``context`` and ``request``::

  response = FrontPage(u"Hello world!")

.. -> code

Keyword arguments are passed into the template scope::

  <html>
    <body>
      Hello world!
    </body>
  </html>

.. -> output

  >>> exec(code)
  >>> response.body.replace('\n\n', '\n') == output.strip('\n')
  True

Framework integration
---------------------

The package comes with integration for views and routes.

Views
#####

In the previous section, we have seen how skin objects are callable
and match the view callable signature.

In BFG we can also define a view using a class which provides
``__init__`` and ``__call__``. The call method must return a
response. Using ``SkinObject`` we can define the class as follows::

  class FrontPageView(object):
      __call__ = SkinObject("index")

      def __init__(self, context, request):
          self.context = context
          self.request = request

.. -> code

  >>> exec(code)

When the ``__call__`` attribute is accessed, the view instance
dictionary (which in this case has the symbols ``context`` and
``request``) is bound to the template. The dictionary is then passed
as keyword arguments when the template is called.

While the two patterns are equivalent, using a view allows you to
prepare data for the template.

The views are registered using the standard ``view`` directive::

  <view name="frontpage1" view=".FrontPage" />
  <view name="frontpage2" view=".FrontPageView" />

.. -> configuration

  >>> from repoze.bfg.skins import tests
  >>> tests.FrontPage = FrontPage
  >>> tests.FrontPageView = FrontPageView
  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   %(configuration)s
  ... </configure>""".strip() % locals())

Both yield the exact same output when passed ``'Hello world!'`` as the
view context::

  <html>
    <body>
      Hello world!
    </body>
  </html>

.. -> output

  >>> from repoze.bfg.view import render_view
  >>> from repoze.bfg.testing import DummyRequest
  >>> frontpage1 = render_view('Hello world!', DummyRequest(), name="frontpage1")
  >>> frontpage2 = render_view('Hello world!', DummyRequest(), name="frontpage2")
  >>> frontpage1.replace('\n\n', '\n') == frontpage2.replace('\n\n', '\n') == output.strip('\n')
  True

Automatic view registration
###########################

To expose the contents of a skin directory as *views*, we can insert a
``view`` registration directive into the ``skins`` directive::

  <skins path="skins">
     <view />
  </skins>

.. -> configuration

  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   <include package="repoze.bfg.skins" />
  ...   %(configuration)s
  ... </configure>""".strip() % locals())
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

.. note:: Views are registered using the component name. However, the directory separator character ("/") is replaced by an underscore (e.g. "images/logo.png" becomes "images_logo.png").

When wrapped inside ``skins``, an option ``index`` is available to
allow registering default index views (e.g. index.pt)::

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

Routes integration
##################

We can configure a route to serve up skins registered as views under
some path (``subpath``)::

  <route
     name="skins"
     path="/static/*subpath"
     factory="repoze.bfg.skins.RoutesTraverserFactory"
     />

.. -> configuration

  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   %(configuration)s
  ... </configure>""".strip() % locals())
  >>> from zope.component import getSiteManager
  >>> registry = getSiteManager()
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
  >>> router.root_factory = getUtility(IRoutesMapper)
  >>> app_iter = router(environ, start_response)
  ('200 OK', [('content-type', 'image/png; charset=UTF-8')])

This traverser will convert ``subpath`` into a view name.

Templates
---------

Included with the package is a factory for Zope Page Templates (with
the file extension ".pt"). The :mod:`Chameleon` rendering engine is
used.

Page templates registered as skin objects will be called *skin
templates*. Support is provided to locate other skin templates and
include them as macros.

Skin expression
###############

This package provides a new expression ``skin:`` which will retrieve a
skin object by name. Lookups are either absolute or relative.

Absolute

  If the name begins with a slash ("/") character, it's considered an
  absolute lookup, e.g.::

    /images/logo.png => "images/logo.png"

  This is a placeless lookup.

Relative

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

  >>> print render_view('Hello world!', DummyRequest(), name="about")
  <html>
   ... <img src="/about/images/logo.png" /> ...
  </html>

Route expression
################

The ``route:`` expression maps to the ``repoze.bfg.url.route_url``
framework function:

  <img tal:attributes="src string:${route: skins}/images/logo.png" />

.. -> source

  >>> from chameleon.zpt.template import PageTemplate
  >>> template = PageTemplate(source)
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

Factories
---------

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

Reload support
--------------

When the global setting ``debug`` is set (to any non-trivial value),
skin objects are discovered at run-time and files are automatically
reloaded when changed.

