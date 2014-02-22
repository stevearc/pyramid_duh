.. _params:

Request Parameters
==================
There are two provided utilities for accessing request parameters. The first is
the ``request.param()`` method. You can use this method by including
``pyramid_duh`` in your app (which comes with some :ref:`other things
<subpath>`), or if you only want the ``param()`` method you can include
``pyramid_duh.params``:

.. code-block:: python

    config.include('pyramid_duh')

Or in the config file:

.. code-block:: ini

    pyramid.includes =
        pyramid_duh

Here is an example use case:

.. code-block:: python

    def register_user(request):
        username = request.param('username')
        password = request.param('password')
        birthdate = request.param('birthdate', type=date)
        metadata = request.param('metadata', {}, type=dict)
        # insert into database

Note that you can pass in default values and perform type conversion. This will
handle both form-encoded data and application/json. If a required argument is
missing, it will raise a 400. For greater detail, see the function docs at
:meth:`~pyramid_duh.params.param`.

Argify
------
Let's make the above example sexier:

.. code-block:: python

    from pyramid_duh import argify

    @argify(birthdate=date, metadata=dict)
    def register_user(request, username, password, birthdate, metadata=None):
        # insert into database

Again, pretty intuitive. If any types are non-unicode, specify them in the
`@argify()` decorator. Positional arguments are required; keyword arguments are
optional. It even supports the value validation of ``request.param()``:

.. code-block:: python

    from pyramid_duh import argify

    def is_natural_number(num):
        return isinstance(num, int) and num > 0

    @argify(age=(int, is_natural_number))
    def set_age(request, username, age):
        # Set user age

It also makes unit tests nicer:

.. code-block:: python

    def test_my_view(self):
        request = DummyRequest()
        ret = my_view(request, 'dsa', 'conspiracytheory', date(1989, 4, 1))

.. note::

    If you're only using ``@argify``, you don't need to include ``pyramid_duh``.

Custom Parameter Types
----------------------
You're now using argument sugar and you're loving it. But you're hungry for
more. You want to auto-convert to your own super-special ``Unicorn`` data type.
Well who doesn't?

Here are the POST parameters:

.. code-block:: javascript

    {
        username: "stevearc",
        pet: {
            "name": "Sparklelord",
            "sparkly": true,
            "cuddly": true
        }
    }

And here is the code to parse that mess:

.. code-block:: python

    class Unicorn(object):
        def __init__(self, name, sparkly, cuddly):
            self.name = name
            self.sparkly = sparkly
            self.cuddly = cuddly

        @classmethod
        def __from_json__(cls, data):
            return cls(**data)


    @argify(pet=Unicorn)
    def set_user_pet(request, username, pet):
        # Set user pet

The ``__from_json__`` method can be a ``classmethod`` or a ``staticmethod``, and the
signature must be either ``(arg)`` or ``(request, arg)``.

.. note::

    I'm using ``@argify``, but this also works with ``request.param()``.

You can also pass in a factory function as the type:

.. code-block:: python

    class Unicorn(object):
        def __init__(self, name, sparkly, cuddly):
            self.name = name
            self.sparkly = sparkly
            self.cuddly = cuddly

    def make_unicorn(data):
        return Unicorn(**data)

    @argify(pet=make_unicorn)
    def set_user_pet(request, username, pet):
        # Set user pet

If you're running into import dependency hell, you can use a dotted path for
the type:

.. code-block:: python

    @argify(pet='mypkg.models.make_unicorn')
    def set_user_pet(request, username, pet):
        # Set user pet

Multi-Parameter Types
---------------------
You can define custom types that will consume multiple request parameters.
Let's look at a new set of POST parameters;

.. code-block:: javascript

    {
        name: "Sparklelord",
        secret: "Radical",
    }

Let's say you want to pass up these parameters as login credentials. You would
like to fetch the named Unicorn from the database and use that in your view.
What would you call that argument? ``unicorn`` would make sense, but there
aren't any parameters named ``unicorn``, so how would you inject a parameter
that is generated from multiple request parameters? All you need to do is take
your type factory function and decorate it with ``@argify`` as well.

.. code-block:: python

    @argify
    def fetch_unicorn(request, name, secret):
        return request.db.query_for_unicorn(name, secret)

    @argify(unicorn=fetch_unicorn)
    def make_rainbows(request, unicorn):
        # Make some fukkin' rainbows

You'll notice here that we're injecting a field named ``unicorn``, which
*doesn't exist* in the POST parameters. You can decorate factory methods or the
``__from_json__`` magic method on type classes.

This particular functionality is kind of magic, and as such I would not
recommend using it frequently because it obfuscates your code. This was really
made with one thing in mind: user authentication. This is a great way to both
authenticate a user and inject the User model into your view with minimal
code duplication.
