Registration
============

In the course of this narrative we will demonstrate different usage
scenarios. The example test setup contains the following files::

  ./skins/index.pt
  ./skins/main_template.pt
  ./skins/images/logo.png
  ./skins/about/index.pt
  ./skins/about/images/logo.png

         ↳ mount point

.. -> output

  >>> import os
  >>> from pyramid_skins import tests
  >>> for filename in output.split('\n'):
  ...     if filename.lstrip().startswith('.'):
  ...         assert os.lstat(
  ...             os.path.join(os.path.dirname(tests.__file__), filename.strip())) \
  ...             is not None

To explain this setup, imagine that the ``index.pt`` template
represents some page in the site (e.g. the *front page*); it uses
``main_template.pt`` as the :term:`o-wrap` template. The ``about``
directory represents some editorial about-section where
``about/index.pt`` is the index page. This section provides its own
logo.

We begin by registering the directory. This makes the files listed
above available as skin components. The ZCML-directive ``skins`` makes
registration easy:

.. code-block:: xml

  <configure xmlns="http://pylonshq.com/pyramid">
    <include package="pyramid_skins" />
    <skins path="skins" />
  </configure>

.. -> configuration

.. invisible-code-block: python

  xmlconfig("""
     <configure xmlns="http://pylonshq.com/pyramid" package="pyramid_skins.tests">
     <include package="pyramid_zcml" file="meta.zcml" />
       %(configuration)s
     </configure>""".strip() % locals())

  from zope.component import getUtility
  from pyramid_skins.interfaces import ISkinObject
  getUtility(ISkinObject, name="index")

The ``path`` parameter indicates a relative path which defines the
mount point for the skin registration.


Components
##########

At this point the skin objects are available as utility
components. This is the low-level interface::

  from zope.component import getUtility
  from pyramid.compat import text_
  from pyramid_skins.interfaces import ISkinObject
  index = getUtility(ISkinObject, name="index")

.. -> code

  >>> exec(code)
  >>> assert index is not None

The component name is available in the ``name`` attribute::

  index.name

.. -> expr

  >>> print(text_(eval(expr)))
  index

We now move up one layer and consider the skin components as objects.

Objects
#######

The ``SkinObject`` class itself wraps the low-level utility lookup::

  from pyramid_skins import SkinObject
  FrontPage = SkinObject("index")

.. -> code

  >>> exec(code)

This object is a callable which will render the template to a response
(it could be an image, stylesheet or some other resource type). In the
case of templates, the first two positional arguments (if given) are
mapped to ``context`` and ``request``. These symbols are available for
use in the template.

::

  response = FrontPage(u"Hello world!")

.. -> code

The index template simply inserts the ``context`` value into the body
tag of the HTML document::

  <html>
    <body>
      Hello world!
    </body>
  </html>

.. -> output

  >>> exec(code)
  >>> response.body.replace(b'\n\n', b'\n') == output.encode('utf-8')
  True
  >>> response.content_type == 'text/html'
  True
  >>> response.charset == 'UTF-8'
  True

The exact same approach works for the logo object::

  from pyramid_skins import SkinObject
  logo = SkinObject("images/logo.png")

.. -> code

Calling the ``logo`` object returns an HTTP response::

  200 OK

.. -> output

  >>> exec(code)
  >>> response = logo()
  >>> response.status == output.strip('\n')
  True
  >>> response.content_type == 'image/png'
  True
  >>> response.content_length == 2833
  True
  >>> response.charset == None
  True

  >>> exec(code)
  >>> response.headers['content-type']
  'image/png'


Request-specific skins
######################

Instead of global utility skin components, we can provide a request
type:

.. code-block:: xml

  <configure xmlns="http://pylonshq.com/pyramid">
    <include package="pyramid_skins" />
    <skins path="skins" request_type="pyramid.interfaces.IRequest" />
  </configure>

.. -> configuration

.. invisible-code-block: python

  _ = xmlconfig("""
     <configure xmlns="http://pylonshq.com/pyramid" package="pyramid_skins.tests">
     <include package="pyramid_zcml" file="meta.zcml" />
       %(configuration)s
     </configure>""".strip() % locals())

The skin component is now registered as a named adapter on the
request:

  >>> from pyramid.testing import DummyRequest
  >>> request = DummyRequest()

We use the ``getAdapter`` call:

  >>> from zope.component import getAdapter
  >>> getAdapter(request, ISkinObject, name="index")
  <pyramid_skins.models.SkinTemplate name="index" path=".../skins/index.pt" at ...>

Views
#####

The call method signature for skin templates is ``(context,
request)``. This is the same as views. That is, we can use skin
template objects directly as view callables::

  <view name="frontpage1" view=".FrontPage" />

.. -> config1

In Pyramid we can also define a view using a class which provides
``__init__`` and ``__call__``. The call method must return a
response. With skin objects, we can express it this way::

  from pyramid_skins import BindableSkinObject

  class FrontPageView(object):
      __call__ = BindableSkinObject("index")

      def __init__(self, context, request):
          self.context = context
          self.request = request

.. -> code

  >>> exec(code)

When the ``__call__`` attribute is accessed (as a descriptor), a view
callable is returned, bound to the view's instance dictionary (which
in this case has the symbols ``context`` and ``request``)::

  <div id="view-${type(view).__name__.lower()}">
    <a href="${request.route_url('search')">Search</a>

    <p class="content">
      ${context}
    </p>
  </div>

Note that methods are not bound.

  <view name="frontpage2" view=".FrontPageView" />

.. -> config2

.. we run these two view configurations.

  >>> from pyramid_skins import tests
  >>> tests.FrontPage = FrontPage
  >>> tests.FrontPageView = FrontPageView
  >>> _ = xmlconfig("""
  ... <configure xmlns="http://pylonshq.com/pyramid"
  ...            package="pyramid_skins.tests">
  ...   <include package="pyramid_zcml" file="meta.zcml" />
  ...   <include package="pyramid_skins" />
  ...   %(config1)s
  ...   %(config2)s
  ... </configure>""".strip() % locals())

While the two patterns are equivalent, using a view allows you to
prepare data for the template. Both yield the exact same output when
passed ``'Hello world!'`` as the view context::

  <html>
    <body>
      Hello world!
    </body>
  </html>

.. -> output

  >>> from pyramid.view import render_view
  >>> from pyramid.testing import DummyRequest
  >>> frontpage1 = render_view('Hello world!', DummyRequest(), name="frontpage1")
  >>> frontpage2 = render_view('Hello world!', DummyRequest(), name="frontpage2")
  >>> frontpage1.replace(b'\n\n', b'\n') == frontpage2.replace(b'\n\n', b'\n') == output.encode('utf-8')
  True

Renderer
########

The package comes with a renderer factory for skin objects. It looks
up a skin object based on view name.

.. automodule:: pyramid_skins.renderer

   .. autofunction:: renderer_factory

In your application setup, use the ``add_renderer`` method::

  config.add_renderer('skin', renderer_factory)

Example view::

  @view_config(name='index', renderer='skin')
  def index(request):
      return {'title': 'My application'}


Discovery
#########

In some scenarios, it's useful to be able to discover skin objects at
run-time. An example is when you use skins to publish editorial
content which is added to the file system.

The ``discovery`` parameter takes a boolean argument, e.g. ``True``:

.. code-block:: xml

  <configure xmlns="http://pylonshq.com/pyramid">
    <skins path="skins" discovery="True" />
  </configure>

.. -> configuration

Let's add a new skin template with the source:

.. code-block:: xml

  <div>Hello world!</div>

.. -> source

.. invisible-code-block: python

  from zope.component import queryUtility
  from pyramid_skins.interfaces import ISkinObject
  import os
  import imp
  import shutil
  import sys
  import tempfile
  import time

  tmppath = tempfile.mkdtemp()
  try:
      try:
          f = open(os.path.join(tmppath, 'foo.py'), 'w')
          path, suffix = os.path.splitext(f.name)
          module = os.path.basename(path)
          imp.load_module(module, open(f.name), path, (suffix, "r", imp.PY_SOURCE))
      finally:
          f.close()

      # make skins directory
      dir = os.path.join(os.path.dirname(path), "skins")
      if not os.path.exists(dir):
          os.mkdir(dir)
      g = None

      # register skin directory
      _ = xmlconfig("""
         <configure xmlns="http://pylonshq.com/pyramid"
                    package="%(module)s">
         <include package="pyramid_zcml" file="meta.zcml" />
         <include package="pyramid_skins" file="meta.zcml" />
           %(configuration)s
         </configure>""".strip() % locals())

      # Wait a while for the discoverer to start up
      time.sleep(0.5)

      # add new file for discovery
      g = tempfile.NamedTemporaryFile(dir=dir, suffix=".pt")
      try:
          g.write(source.encode('utf-8'))
          g.flush()

          name = os.path.splitext(os.path.basename(g.name))[0]
          count = 10
          # retry a few times for discovery
          while count:
              # sleep for a short while to discover the new file
              time.sleep(0.5)

              # verify existence
              template = queryUtility(ISkinObject, name=name)
              if template:
                  break
              count = count - 1
          assert template is not None, "Template does not exist: " + name
          if template:
              output = template()
      finally:
          g.close()

  finally:
      shutil.rmtree(tmppath)

  >>> print(output)
  200 OK
  Content-Length: 24
  Content-Type: text/html; charset=UTF-8
  <BLANKLINE>
  <div>Hello world!</div>

Compatibility
-------------
- Mac OS X 10.5+ (requires the ``MacFSEvents`` library)
- Linux 2.6.13+ with Libc >= 2.4 (requires ``pyinotify`` library)


Imperative configuration
========================

If you prefer imperative configuration over declarative you can use
the ``pyramid_skins.configuration.register_path`` method for
configuration:

.. automodule:: pyramid_skins.configuration

   .. autofunction:: register_path

Example::

  from pyramid.config import Configurator
  config = Configurator()

  from pyramid_skins.configuration import register_path
  register_path(config, path)

