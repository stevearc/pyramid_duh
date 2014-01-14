Subpath Predicate
=================
One of the problems people have with pyramid's traversal is that it doesn't
allow you to set view predicates on the subpath. If you aren't already
intimately familiar with the details of resource lookup via traversal, `you'll
need this <https://pyramid.readthedocs.org/en/latest/narr/traversal.html>`_.

So we've got the ``context``, which is the last found resource. The ``name``,
which is the first url segment that had no new context, and then the
``subpath``, which is *everything else*. Here's a thing:

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar')
    def my_view(request):
        # do stuff

Let's say that ``MyCtxt`` corresponds to a url of ``'/mything'``. What urls
will map to ``my_view``?

* ``/mything/foobar`` - Ok, that's good
* ``/mything/foobar/`` - Oh, trailing slashes too! That's cool.
* ``/mything/foobar/baz`` - Wait...what?
* ``/mything/foobar/baz/barrel/full/of/monkeys`` - I don't...I didn't tell you to do that...
* ``/mything/foobar/baz/barrel/full/of/monkeys/oh/god/why/please/make/it/stop``

This is silly. But it gets worse.

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar')
    def my_view(request):
        # do stuff

    @view_config(context=MyCtxt)
    def root_view(request):
        # do stuff

Okay, so we've defined two endpoints:

* ``/mything/`` - ``root_view``
* ``/mything/foobar`` - ``my_view``

But also these:

* ``/mything/wabbit/season`` - ``root_view``
* ``/mything/foobars`` - ``root_view``
* ``/mything/foobar/baz`` - ``my_view``

And what happens if we *need* the subpath in a view?

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar')
    def my_view(request):
        if len(request.subpath) != 2:
            raise HTTPNotFound()
        if request.subpath[0] not in ('foo', 'bar'):
            raise HTTPNotFound()

That's not really okay. I'm not okay with that.

The Solution
------------
.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=())
    def my_view(request):
        # do things

Huh...that looks easy. What does it match?

* ``/mything/foobar``
* ``/mything/foobar/``

Oh hey, that's exactly what I wanted it to do with no crazy unexpected
behavior. Awesome.

BUT NOT AWESOME ENOUGH. GIVE ME MOARRRRR

Oh, let's say you want the subpaths to match ``/post/{id}`` but nothing else.

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=('post', '*'))
    def my_view(request):
        # do things

Oh, I guess that was easy too. But I want that post id. Is there a better way
to get it that indexing the subpath?

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=('post', 'id/*'))
    def my_view(request):
        id = request.named_subpaths['id']
        # do things

Ooooooooooooooooooooooo

Yeah, and it does PCRE as well. In case you need that.

.. code-block:: python

    @view_config(context=MyCtxt, name='foobar', subpath=('type/post|tweet/r', 'id/*'))
    def my_view(request):
        item_type = request.named_subpaths['type']
        id = request.named_subpaths['id']
        # do things

Check the docs on :class:`~pyramid_duh.view.SubpathPredicate` for all of the
formats, and :meth:`~pyramid_duh.view.match` for details on match flags.

How Does I Do?
--------------
Just include ``pyramid_duh`` (which comes with parameter magic), or just
``pyramid_duh.view``:

.. code-block:: python

    config.include('pyramid_duh')

Or in the config file:

.. code-block:: ini

    pyramid.includes =
        pyramid_duh
