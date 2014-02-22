.. _subpath:

Subpath Predicate
=================
One problem with pyramid's traversal mechanism is that it doesn't allow you to
set view predicates on the subpath. If you aren't already intimately familiar
with the details of resource lookup via traversal, `here are the docs
<https://pyramid.readthedocs.org/en/latest/narr/traversal.html>`_.

So we've got the ``context``, which is the last found resource. The ``name``,
which is the first url segment that had no new context, and then the
``subpath``, which is all path components after the ``name``.

To enforce a subpath matching, pass in a list or tuple as the vew predicate:

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=())
    def my_view(request):
        # do things

Assuming that ``MyCtxt`` maps to ``/mything``, this view will match
``/mything/foobar`` and ``/mything/foobar/`` only. No subpath allowed. Here is
the format for matching a single subpath:

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=('post', '*'))
    def my_view(request):
        id = request.subpath[0]
        # do things

You can name the subpaths and access them by name:

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=('post', 'id/*'))
    def my_view(request):
        id = request.named_subpaths['id']
        # do things

And there are flags you can pass in that allow, among other things, PCRE
matching:

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=('type/(post|tweet)/r', 'id/*'))
    def my_view(request):
        item_type = request.named_subpaths['type']
        id = request.named_subpaths['id']
        # do things

Check the docs on :class:`~pyramid_duh.view.SubpathPredicate` for all of the
formats, and :meth:`~pyramid_duh.view.match` for details on match flags.

Including
---------
You can use this predicate by including ``pyramid_duh`` in your app (which
comes with some :ref:`other things <params>`), or if you only want the
predicate you can include ``pyramid_duh.view``:

.. code-block:: python

    config.include('pyramid_duh')

Or in the config file:

.. code-block:: ini

    pyramid.includes =
        pyramid_duh
