Traversal
=========
These are a couple templates for traversal tree nodes that I found myself
reusing everywhere.

ISmartLookupResource
--------------------
This is useful if you have nested resources in your tree, like
``/user/1234/post/9876``. You can have a ``UserResource`` context in your path
that has a ``user`` attribute, and a ``PostResource`` context that has a
``post`` attribute. As long as your final context inherits from
``ISmartLookupResource``, it can access both the ``user`` and the ``post``
directly.

.. code-block:: python

    @view_config(context=PostResource)
    def get_user_post(context, request):
        if context.user.is_cool():
            return context.post

This is also useful because it means you don't have to pass the request object
down your tree heirarchy. You can just attach it to the root and your nodes
will be able to access it.

IStaticResource
---------------
Resource for static paths:

.. code-block:: python

    class MyResource(IStaticResource):
        subobjects = {
            'foo': foo_factory,
            'bar': bar_factory,
        }

This does what you think it does. But it prevents you from forgetting to set
the ``__parent__`` and ``__name__`` attributes on the child. Because that
produces terrible and subtle bugs.

IModelResource
--------------
Template for retrieving assets from a SQLAlchemy connection. Here's an example:

.. code-block:: python

    class UserResource(IModelResource):
        __model__ = User
        __modelname__ = 'user'

    @view_config(context=UserResource)
    def get_user(context, request):
        return context.user

This can be customized quite a bit, so look at the docstrings on
:class:`~pyramid_duh.route.IModelResource` for more info.

Where is They?
--------------
Just import them

.. code-block:: python

    from pyramid_duh import ISmartLookupResource, IStaticResource, IModelResource
