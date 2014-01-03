Add Slash
=========
You have a view. It lies at ``http://example.com/path/to/resource/``. But for
some reason people keep going to ``http://example.com/path/to/resource``. And
it messes up relative asset paths. Well, `pyramid's solution
<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/urldispatch.html#redirecting-to-slash-appended-routes>`_
is a little janky. They define a 404 handler that *always* attempts to add a
slash to *any* view that wasn't found. It works, but it's global and you
wouldn't know about the behavior just from looking at the view callable. So do
this:

.. code-block:: python

    from pyramid_duh import addslash

    @addslash
    def my_view(request):
        # serve my resource

Easy peasy lemon squeezy.
