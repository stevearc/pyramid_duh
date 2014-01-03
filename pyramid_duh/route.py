""" Utilities for traversal """
from pyramid.httpexceptions import HTTPNotFound


class ISmartLookupResource(object):

    """
    Resource base class that allows hierarchical lookup of attributes

    Potential use case: /user/1234/post/5678

    At the /user/1234 point in traversal you can set a 'user' attribute on the
    resource. At the 'post/5678' point in traversal you can set a 'post'
    attribute on *that* resource. Then the request can access both of them from
    the context directly:

    .. code-block:: python

        def get_user_post(context, request):
            user = context.user
            if user.is_cool():
                return context.post

    """
    __name__ = ''
    __parent__ = None

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError()
        current = self.__parent__
        while current is not None:
            try:
                return getattr(current, name)
            except AttributeError:
                # If this node was doing smart lookup, we don't need to
                if isinstance(current, ISmartLookupResource):
                    break
                current = current.__parent__
        raise AttributeError("'%s' not found on any parents of %s" %
                             (name, self))


class IStaticResource(ISmartLookupResource):

    """ Simple resource base class for static-mapping of paths """
    subobjects = {}

    def __getitem__(self, name):
        child = self.subobjects[name]()
        child.__parent__ = self
        child.__name__ = name
        return child


class IModelResource(ISmartLookupResource):

    """
    Resource base class for wrapping models in a sqlalchemy database

    Notes
    -----
    Requires any parent node to set the 'request' attribute

    """
    __model__ = None
    __modelname__ = 'model'

    def __init__(self, model=None):
        setattr(self, self.__modelname__, model)

    @property
    def db(self):
        """
        Access the SQLAlchemy session on the request

        Override this if your session is named something other than 'db'

        """
        return self.request.db

    def get_model(self, name):
        """
        Retrieve a model from the database

        Override this for custom queries

        """
        return self.db.query(self.__model__).filter_by(id=name).first()

    def create_model(self, name):
        """
        Override this if you wish to allow 'PUT' request to create a model

        """
        raise KeyError

    def __getitem__(self, name):
        if getattr(self, self.__modelname__) is None:
            model = self.get_model(name)
            if model is None and self.request.method == 'PUT':
                model = self.create_model(name)
            if model is not None:
                child = self.__class__(model)
                child.__parent__ = self
                child.__name__ = name
                return child
            else:
                raise HTTPNotFound()
        raise KeyError
