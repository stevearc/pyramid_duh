Pyramid Duh
===========
:Master Build: |build|_ |coverage|_
:0.1 Build: |build-0.1|_ |coverage-0.1|_
:Documentation: http://pyramid_duh.readthedocs.org/
:Downloads: http://pypi.python.org/pypi/pyramid_duh
:Source: https://github.com/stevearc/pyramid_duh

.. |build| image:: https://travis-ci.org/stevearc/pyramid_duh.png?branch=master
.. _build: https://travis-ci.org/stevearc/pyramid_duh
.. |coverage| image:: https://coveralls.io/repos/stevearc/pyramid_duh/badge.png?branch=master
.. _coverage: https://coveralls.io/r/stevearc/pyramid_duh?branch=master

.. |build-0.1| image:: https://travis-ci.org/stevearc/pyramid_duh.png?branch=0.1
.. _build-0.1: https://travis-ci.org/stevearc/pyramid_duh
.. |coverage-0.1| image:: https://coveralls.io/repos/stevearc/pyramid_duh/badge.png?branch=0.1
.. _coverage-0.1: https://coveralls.io/r/stevearc/pyramid_duh?branch=0.1

This is just a collection of utilities that I found myself putting into *every
single* pyramid project I made. So now they're all in one place.

Here's a quick taste.

Don't do this::

    def register_user(request):
        username = request.POST['username']
        password = request.POST['password']
        birthdate = request.POST['birthdate']

Do this::

    @argify(birthdate=date)
    def register_user(request, username, password, birthdate):
        ...

What urls does this match?

::

    @view_config(context=Root, name='package')
    def get_or_list_packages(request):
        ...

Well, it matches

* ``/package``
* ``/package/``
* ``/package/1234``
* ``/package/wait/hold/on``
* ``/package/this/seems/confusing``

Whaaaat? Let's fix that::

    @view_config(context=Root, name='package', subpath=())
    def list_packages(request):
        # return a list of packages

    @view_config(context=Root, name='package', subpath=('id/*')
    def get_package(request):
        package_id = request.named_subpaths['id']
        # fetch a single package

The first one matches

* ``/package``
* ``/package/``

The second matches

* ``/package/*``
* ``/package/*/``

But that still seems sloppy. You *demand* consistency!

::

    @view_config(context=Root, name='package', subpath=())
    @addslash
    def list_packages(request):
        # return a list of packages

    @view_config(context=Root, name='package', subpath=('id/*')
    @addslash
    def get_package(request):
        package_id = request.named_subpaths['id']
        # fetch a single package

Now it's just ``/package/`` and ``/package/*/``

That's the sales pitch. Read the docs for more details.
