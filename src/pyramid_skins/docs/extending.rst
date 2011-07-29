Extending
=========

You can extend the skins framework using the component architecture.

Factories
---------

When skin files are registered, the filename extension --
e.g. ``".pt"`` -- is used to look up a skin object class (factory);
failing that, the base class is used.

Skin object classes must inherit from the ``SkinObject`` base
class. To register a custom class for some file extension, use the
extension as the utility component name:

.. code-block:: xml

   <utility
      name=".my"
      component=".MySkinObject"
      provides="pyramid_skins.interfaces.ISkinObjectFactory"
      />

An example of such a custom factory is the skin template class. It
overrides the ``refresh`` method (to make sure the template is
recompiled on file change), removes the file extension from the
component name and uses a custom ``render`` method.

This approach could be used to render formatted text files,
e.g. restructured text.
