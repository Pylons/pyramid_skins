.. Dhi documentation master file, created by
   sphinx-quickstart on Sun Nov  1 16:08:00 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The flexible skinning solution
==============================

This package provides an extension to the `BFG
<http://bfg.repoze.org/>`_ framework for integrating code with
templates and resources -- what's known as the *application skin*.

You can use the package in a variety of ways. It's designed to be
immediately useful for most applications and flexible enough to scale
to complex use-cases.

Some examples:

- Make it easy for users of your package to **override** one or more included resources.
- Provide **flexibility** for your site's content section by using
  HTML templates instead of static HTML.
- Use custom templates or resources for a particular **subset** of pages.

Integration is available for templates, routes and views. Discovery at
run-time is supported [#]_.

First look
----------

Skin objects live in a global namespace. You can organize the space
using directory nesting. The following example illustrates the mapping
from the file system to the skin object space (where ``./``
corresponds to some package path)::

  ./skins/index.pt          =>  "index"
  ./skins/images/logo.png   =>  "images/logo.png"

         ↳ mount point

The mount point constitutes a *skin directory*. You can register as
many skin directories as you need. The files found under each
directory will be entered into the global skin object space. In this
way, new registrations can override previous ones.

Note in the example that ``index.pt`` appears on the skin side without
its file extension. This is a behavior of the *skin factory* for
template files (with the ``.pt`` extension).

We come back to this in much more detail, but here's how you would
register the ``./skins`` directory using ZCML (we use the relative
path here, assuming the ZCML configuration file is in the same
directory)::

  <configure xmlns="http://namespaces.repoze.org/bfg">
    <include package="repoze.bfg.skins" />
    <skins path="skins" />
  </configure>

That's it! This is all you need to start using skin objects in Python
code. The ``index`` name now maps to the ``./skins/index.pt`` file on
disk::

  from repoze.bfg.skins import SkinObject
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
<stefan.eletzhofer@inquant.de>`_. Available as-is under the BSD
license. To contribute or get support for this package, please visit
the ``#repoze`` channel on Freenode IRC or write to the `repoze-dev
mailinglist <repoze-dev@lists.repoze.org>`_.

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
