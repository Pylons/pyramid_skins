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
  >>> from repoze.bfg.skins import tests
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
registration easy::

  <configure xmlns="http://namespaces.repoze.org/bfg">
    <include package="repoze.bfg.skins" />
    <skins path="skins" />
  </configure>

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


Components
##########

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
  'index'

We now move up one layer and consider the skin components as objects.

Objects
#######

The ``SkinObject`` class itself wraps the low-level utility lookup::

  from repoze.bfg.skins import SkinObject
  FrontPage = SkinObject("index")

.. -> code

  >>> exec(code)
  >>> FrontPage.__get__() is not None
  True

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
  >>> response.body.replace('\n\n', '\n') == output.strip('\n')
  True
  >>> response.content_type == 'text/html'
  True
  >>> response.charset == 'UTF-8'
  True

The exact same approach works for the logo object::

  from repoze.bfg.skins import SkinObject
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

  <configure xmlns="http://namespaces.repoze.org/bfg">
    <include package="repoze.bfg.skins" />
    <skins path="skins" request_type="repoze.bfg.interfaces.IRequest" />
  </configure>

.. -> configuration

.. invisible-code-block: python

  from zope.configuration.xmlconfig import string
  _ = string("""
     <configure xmlns="http://namespaces.repoze.org/bfg" package="repoze.bfg.skins.tests">
     <include package="repoze.bfg.includes" file="meta.zcml" />
       %(configuration)s
     </configure>""".strip() % locals())

The skin component is now registered as a named adapter on the
request:

  >>> from repoze.bfg.testing import DummyRequest
  >>> request = DummyRequest()

We use the ``getAdapter`` call:

  >>> from zope.component import getAdapter
  >>> getAdapter(request, ISkinObject, name="index")
  <repoze.bfg.skins.models.SkinTemplate name="index" path=".../skins/index.pt" at ...>

Views
#####

The call method signature for skin templates is ``(context,
request)``. This is the same as BFG views. That is, we can use skin
template objects directly as view callables::

  <view name="frontpage1" view=".FrontPage" />

.. -> config1

In BFG we can also define a view using a class which provides
``__init__`` and ``__call__``. The call method must return a
response. With skin objects, we can express it this way::

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
as keyword arguments when the template is called::

  <view name="frontpage2" view=".FrontPageView" />

.. -> config2

.. we run these two view configurations.

  >>> from repoze.bfg.skins import tests
  >>> tests.FrontPage = FrontPage
  >>> tests.FrontPageView = FrontPageView
  >>> from zope.configuration.xmlconfig import string
  >>> _ = string("""
  ... <configure xmlns="http://namespaces.repoze.org/bfg"
  ...            package="repoze.bfg.skins.tests">
  ...   <include package="repoze.bfg.includes" file="meta.zcml" />
  ...   <include package="repoze.bfg.skins" />
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

  >>> from repoze.bfg.view import render_view
  >>> from repoze.bfg.testing import DummyRequest
  >>> frontpage1 = render_view('Hello world!', DummyRequest(), name="frontpage1")
  >>> frontpage2 = render_view('Hello world!', DummyRequest(), name="frontpage2")
  >>> frontpage1.replace('\n\n', '\n') == frontpage2.replace('\n\n', '\n') == output.strip('\n')
  True

Discovery
#########

In some scenarios, it's useful to be able to discover skin objects at
run-time. An example is when you use skins to publish editorial
content which is added to the file system.

The ``discovery`` parameter takes a boolean argument, e.g. ``True``::

  <configure xmlns="http://namespaces.repoze.org/bfg">
    <skins path="skins" discovery="True" />
  </configure>

.. -> configuration

Let's add a new skin template with the source::

  <div>Hello world!</div>

.. -> source

.. invisible-code-block: python

  import os
  import imp
  import sys
  import tempfile
  f = tempfile.NamedTemporaryFile(suffix=".py")
  try:
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
  try:
      # register skin directory
      from zope.configuration.xmlconfig import string
      _ = string("""
         <configure xmlns="http://namespaces.repoze.org/bfg"
                    package="%(module)s">
         <include package="repoze.bfg.includes" file="meta.zcml" />
         <include package="repoze.bfg.skins" />
           %(configuration)s
         </configure>""".strip() % locals())

      # Wait a while for the discoverer to start up
      import time
      time.sleep(0.5)

      # add new file for discovery
      g = tempfile.NamedTemporaryFile(dir=dir, suffix=".pt")
      try:
          g.write(source)
          g.flush()

          # sleep for a short while to discover the new file
          import time
          time.sleep(0.5)

          name = os.path.splitext(os.path.basename(g.name))[0]

          # verify existence
          from zope.component import queryUtility
          from repoze.bfg.skins.interfaces import ISkinObject
          template = queryUtility(ISkinObject, name=name)
          assert template is not None, "Template does not exist: " + name
          if template:
              output = template()
      finally:
          g.close()

  finally:
      os.removedirs(dir)

  >>> print output
  200 OK
  Content-Length: 23
  Content-Type: text/html; charset=UTF-8
  <BLANKLINE>
  <div>Hello world!</div>

Compatibility
-------------
- Mac OS X 10.5+ (requires the ``MacFSEvents`` library)
- Linux 2.6.13+ with Libc >= 2.4 (requires ``pyinotify`` library)


Imperative configuration
========================
If you prefer imperative configuration over declarative you can use the
``register_path`` method to configure skins::

  from repoze.bfg.skins.configuration import register_path
  register_path("templates", discovery=True)


