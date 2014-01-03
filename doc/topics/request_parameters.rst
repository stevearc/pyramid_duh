Request Parameters
==================
Why does getting request parameters suck so hard in pyramid? Let's look at the
problem. Say we want to register a new user with a username, password, and
birthdate. Your view might look like this:

.. code-block:: python

    def register_user(request):
        username = request.POST['username']
        password = request.POST['password']
        birthdate = request.POST['birthdate']
        # insert into database

Great. That's great. Wait, what's the birthdate again? A string? Uh oh...let's
fix that:

.. code-block:: python

    def register_user(request):
        username = request.POST['username']
        password = request.POST['password']
        bd_ts = int(request.POST['birthdate'])
        birthdate = datetime.fromtimestamp(bd_ts).date()
        # insert into database

Okay, now that works. But what happens if someone forgets to pass up the
birthdate? ``KeyError``! Which will turn into a 500! That's not right. Let's
fix it:

.. code-block:: python

    def register_user(request):
        try:
            username = request.POST['username']
            password = request.POST['password']
            bd_ts = int(request.POST['birthdate'])
            birthdate = datetime.fromtimestamp(bd_ts).date()
        except KeyError:
            raise HTTPBadRequest("Missing argument")
        # insert into database

Better. But what if the user passes up a birthdate that looks like ``'YYYY-mm-dd'``?

.. code-block:: python

    def register_user(request):
        try:
            username = request.POST['username']
            password = request.POST['password']
            bd_ts = int(request.POST['birthdate'])
            birthdate = datetime.fromtimestamp(bd_ts).date()
        except KeyError:
            raise HTTPBadRequest("Missing argument")
        except ValueError:
            raise HTTPBadRequest("Malformed birthdate")
        # insert into database

Great! Now it's working! But now we realize that we need the user to be able to
register with other arbitrary metadata fields that we can store with the
object. Like their favorite color and the name of their first pet.

.. code-block:: python

    def register_user(request):
        try:
            username = request.POST['username']
            password = request.POST['password']
            bd_ts = int(request.POST['birthdate'])
            birthdate = datetime.fromtimestamp(bd_ts).date()
            metadata = request.POST['metadata']
        except KeyError:
            raise HTTPBadRequest("Missing argument")
        except ValueError:
            raise HTTPBadRequest("Malformed birthdate")
        # insert into database

Wait...what's metadata here? Oh, it's a dict? So...now your client is probably
passing it up with the ``Content-Type`` of ``application/json``. Guess what?
Those don't go to ``request.POST``. They go to ``request.json_body()``.

Now repeat this code for every one of your views, using ``request.POST``,
``request.GET``, and ``request.json_body()`` as appropriate.

NO THANK YOU

The Solution
------------
Luckily, pyramid is awesome and can be customized like nobody's business. It's
not hard to write a wrapper that fixes this madness, but nobody should have to
do it. It's a solved problem. Here's the solution:

.. code-block:: python

    def register_user(request):
        username = request.param('username')
        password = request.param('password')
        birthdate = request.param('birthdate', type=date)
        metadata = request.param('metadata', {}, type=dict)
        # insert into database

Kind of underwhelming, isn't it? It just sits there and looks like you think it
should. It uses GET, POST, and json_body when appropriate. It converts fields
for you to the proper data type. You can specify default values. Coolio.

The Sexy Solution
-----------------
``@argify`` baby. Do it.

.. code-block:: python

    @argify(birthdate=date, metadata=dict)
    def register_user(request, username, password, birthdate, metadata=None):
        # insert into database

Oh-ho-ho! Who's this pretty lady? It's ``argify`` and it's wonderful. You
decorate your views and it pulls the request parameters out for you. If you
need to perform type conversions, specify the type in the decorator. If some
parameters are optional and have default values, those become keyword
arguments.

Perhaps the best part about ``argify`` is that it turns your unit tests from this:

.. code-block:: python

    def test_my_view(self):
        request = DummyRequest()
        params = {
            'username': 'dsa',
            'password': 'conspiracytheory',
            'birthdate': date(1989, 4, 1)
        }
        request.param = lambda x: params[x]
        ret = my_view(request)

To this:

.. code-block:: python

    def test_my_view(self):
        request = DummyRequest()
        username, password = 'dsa', 'conspiracytheory'
        birthdate = date(1989, 4, 1)
        ret = my_view(request, username, password, birthdate)

Note that argify MUST be the closest decorator to the view callable in order
for the argument inspection to work properly.

OMFG HOW DO I USE THIS
----------------------
If you want to use ``request.param``, you can include ``pyramid_duh`` (which comes with some other things), or just ``pyramid_duh.params``:

.. code-block:: python

    config.include('pyramid_duh')

Or in the config file:

.. code-block:: ini

    pyramid.includes =
        pyramid_duh

To use argify just import it. No includes necessary.

.. code-block:: python

    from pyramid_duh import argify

    @argify
    def my_view(request, foo, bar, baz='wibbly'):
        # do stuff
