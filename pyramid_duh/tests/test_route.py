""" Unit tests for route module """
from mock import MagicMock, patch
from pyramid.httpexceptions import HTTPNotFound
from pyramid.testing import DummyRequest
from pyramid_duh.route import (ISmartLookupResource, IStaticResource,
                               IModelResource)


try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest

# pylint: disable=W0104


class TestSmartLookup(unittest.TestCase):

    """ Tests for smart lookup nodes """

    def test_smart_lookup_self(self):
        """ ISmartLookupResource can find object on self """
        resource = ISmartLookupResource()
        resource.foobar = 'baz'
        self.assertEqual(resource.foobar, 'baz')

    def test_smart_lookup_parent(self):
        """ ISmartLookupResource can find object on parent """
        parent = ISmartLookupResource()
        resource = ISmartLookupResource()
        resource.__parent__ = parent
        parent.foobar = 'baz'
        self.assertEqual(resource.foobar, 'baz')

    def test_smart_lookup_grandparent(self):
        """ ISmartLookupResource can find object on grandparent """
        grandparent = ISmartLookupResource()
        parent = ISmartLookupResource()
        parent.__parent__ = grandparent
        resource = ISmartLookupResource()
        resource.__parent__ = parent
        grandparent.foobar = 'baz'
        self.assertEqual(resource.foobar, 'baz')

    def test_smart_lookup_missing(self):
        """ ISmartLookupResource raises AttributeError if object missing """
        grandparent = ISmartLookupResource()
        parent = ISmartLookupResource()
        parent.__parent__ = grandparent
        resource = ISmartLookupResource()
        resource.__parent__ = parent
        with self.assertRaises(AttributeError):
            resource.foobar

    def test_smart_lookup_no_private(self):
        """ ISmartLookupResource doesn't look up private fields """
        parent = ISmartLookupResource()
        resource = ISmartLookupResource()
        resource.__parent__ = parent
        parent._foobar = 'baz'
        with self.assertRaises(AttributeError):
            resource._foobar


class TestStaticResource(unittest.TestCase):

    """ Tests for static resource nodes """

    def test_static_resource(self):
        """ Generate next resource if path in map """
        resource = IStaticResource()
        factory = MagicMock()
        resource.subobjects = {'myroute': factory}
        result = resource['myroute']
        self.assertEqual(result, factory())
        # Set __parent__ and __name__
        self.assertEqual(result.__name__, 'myroute')
        self.assertEqual(result.__parent__, resource)

    def test_missing_resource(self):
        """ Raise KeyError if route doesn't match named paths """
        resource = IStaticResource()
        factory = MagicMock()
        resource.subobjects = {'myroute': factory}
        with self.assertRaises(KeyError):
            resource['foobar']


class TestModelResource(unittest.TestCase):

    """ Tests for model resource nodes """

    @patch('pyramid_duh.route.IModelResource.get_model')
    def test_fetch_model(self, get_model):
        """ Fetch resource by id """
        resource = IModelResource()
        ret = resource['foobar']
        self.assertTrue(isinstance(ret, IModelResource))
        self.assertEqual(ret.__parent__, resource)
        self.assertEqual(ret.__name__, 'foobar')
        get_model.assert_called_with('foobar')
        self.assertEqual(ret.model, get_model())

    @patch('pyramid_duh.route.IModelResource.create_model')
    @patch('pyramid_duh.route.IModelResource.get_model')
    def test_put_create(self, get_model, create_model):
        """ Put request can create a new model """
        resource = IModelResource()
        request = DummyRequest()
        request.method = 'PUT'
        resource.request = request
        get_model.return_value = None
        ret = resource['foobar']
        self.assertTrue(isinstance(ret, IModelResource))
        self.assertEqual(ret.__parent__, resource)
        self.assertEqual(ret.__name__, 'foobar')
        get_model.assert_called_with('foobar')
        create_model.assert_called_with('foobar')
        self.assertEqual(ret.model, create_model())

    def test_no_subpaths(self):
        """ If resource already contains model, further paths raise KeyError """
        resource = IModelResource()
        resource.model = MagicMock()
        with self.assertRaises(KeyError):
            resource['foobar']

    @patch('pyramid_duh.route.IModelResource.db')
    def test_default_fetch(self, db):
        """ Default db fetch operation """
        resource = IModelResource()
        resource['foobar']
        db.query.assert_called_with(resource.__model__)

    def test_default_db(self):
        """ The default sqlalchemy database is request.db """
        request = MagicMock()
        resource = IModelResource()
        resource.request = request
        self.assertEqual(resource.db, request.db)

    def test_default_create(self):
        """ Default create operation raises keyerror """
        resource = IModelResource()
        with self.assertRaises(KeyError):
            resource.create_model('foobar')

    @patch('pyramid_duh.route.IModelResource.get_model')
    def test_404(self, get_model):
        """ If model is not found, raise 404 """
        resource = IModelResource()
        request = DummyRequest()
        request.method = 'GET'
        resource.request = request
        get_model.return_value = None
        with self.assertRaises(HTTPNotFound):
            resource['foobar']
