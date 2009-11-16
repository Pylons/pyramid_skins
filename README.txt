Overview
========

.. role:: mod(emphasis)
.. role:: term(emphasis)

This package provides a simple framework to integrate code with
templates and resources.

Features:

- Support for routes and views
- Integrates with Zope Page Templates
- Customization story based on layers

Usage
-----

You can use the package in a variety of ways. It's designed to be
immediately useful without getting in the way or giving up
flexibility. In any case, the objective is to take the separation of
logic from presentation to the next step and also separate the
*wiring* from the codebase.

This is done by using symbolic (but predictable) object names instead
of file system paths::

  ./package/skins/images/logo.png    =>  "images/logo.png"
  ./package/skins/main_template.pt   =>  "main_template"

           ↳ mount point

The mount point constitutes a *skin directory*. You can register as
many skin directories as you need. The objects found are entered in a
global namespace, which means objects can be overriden. The last
registration *wins*.

Note that for the template ``main_template.pt``, the file extension is
left out from the object name. This is a behavior of the *template
factory* -- the default for the ``.pt`` extension.

About
-----

The package is written and maintained by `Malthe Borch
<mailto:mborch@gmail.com>`_ and `Stefan Eletzhofer
<stefan.eletzhofer@inquant.de>`_. Available as-is under the BSD
license.

To contribute or get support for this package, please visit the
#repoze channel on freenode irc or write to the `repoze-dev
mailinglist <repoze-dev@lists.repoze.org>`_.
