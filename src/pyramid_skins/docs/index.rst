.. Dhi documentation master file, created by
   sphinx-quickstart on Sun Nov  1 16:08:00 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The flexible skinning solution
==============================

This package provides an extension to the `Pyramid
<http://pylonshq.com/pyramid/>`_ framework for integrating code with
templates and resources -- what's known as the *application skin*.

You can use the package in a variety of ways. It's designed to be
immediately useful for most applications and flexible enough to scale
to complex use-cases.

Some examples:

- Make it easy for users of your package to **override** one or more included resources.
- Provide **flexibility** for your site's content section by using
  HTML templates instead of static HTML.
- Use custom templates or resources for a particular **subset** of pages.
- Use automatic **discovery** to integrate with external applications [#]_.

Integration is available for templates, routes and views.

First look
----------

Skin objects live in a global namespace. You can organize the space
using directory nesting and/or request types.

The following example illustrates the mapping
from the file system to the skin object space (where ``./``
corresponds to some package path)::

  ./skins/index.pt          =>  "index"
  ./skins/images/logo.png   =>  "images/logo.png"

         ↳ mount point

The mount point constitutes a *skin directory*. You can register as
many skin directories as you need. The files found under each
directory will be entered into the global skin object space. In this
way, new registrations can override previous ones.

Note in the example that ``index.pt`` appears without its file
extension. This is a behavior of the *skin factory* for template files
(with the ``.pt`` extension).

Here's how you would configure this using Pyramid's *imperative*
configurator::

  from pyramid.config import Configurator
  config = Configurator()

  import pyramid_skins
  config.include(pyramid_skins)
  config.register_path("pyramid_skins:tests/skins")

If you're instead using the `pyramid_zcml
<http://pypi.python.org/pypi/pyramid_zcml/>`_ extension to configure
your application using ZCML, this is supported through the ``skins``
directive. We come back to this in much more detail, but here's how
you would register the same skin directory using ZCML:

.. code-block:: xml

  <configure xmlns="http://pylonshq.com/pyramid">
    <include package="pyramid_skins" />
    <skins path="tests/skins" />
  </configure>

That's it! This is all you need to start using skin objects in Python
code. The ``index`` name now maps to the ``./skins/index.pt`` file on
disk::

  from pyramid_skins import SkinObject
  index = SkinObject("index")

This is a callable; it renders the template and returns an HTTP
response object. If you provide keyword arguments, they will be passed
into the template. Note that for skin templates (like ``"index"``), the
optional first two positional arguments are mapped to ``context`` and
``request``.


Support and development
-----------------------

The package is written and maintained by `Malthe Borch
<mailto:mborch@gmail.com>`_ and `Stefan Eletzhofer
<stefan.eletzhofer@inquant.de>`_. Available *as is* under the BSD
license. To contribute or get support for this package, please visit
the ``#pyramid`` channel on Freenode IRC or write to the `pylons
mailinglist <pylons-discuss@googlegroups.org>`_.

The package has 100% test coverage. This documentation itself is
tested using the :mod:`manuel` library which works with the standard
testrunner. You can run all tests from the command-line using::

  $ python setup.py test

This allows you to make sure the package is compatible with your
platform.

Contents
========

.. toctree::
   :maxdepth: 2

   registration
   templates
   routing
   extending
   glossary

Indices and tables
==================

* :ref:`search`
* :ref:`glossary`

.. [#] Available on Mac OS 10.5+ (requires ``MacFSEvents`` library) and Linux 2.6.13+ with Libc >= 2.4 (requires ``pyinotify`` library)
