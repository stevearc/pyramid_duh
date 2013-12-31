""" Tests for param utilities """
from __future__ import unicode_literals

import datetime
import time

import json
import unittest
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.testing import DummyRequest
from pyramid_duh.compat import is_bytes, is_string
from pyramid_duh.params import argify, _param


class ParamContainer(object):

    """ Simple little container for parameters """

    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

    @classmethod
    def __from_json__(cls, data):
        return cls(**data)


class ParamContainerStatic(ParamContainer):

    """ Container with a static __from_json__ method """

    @staticmethod
    def __from_json__(data):
        return ParamContainerStatic(**data)


class SimpleParamContainer(object):

    """ Container with no __from_json__ method """

    def __init__(self, data):
        self.__dict__.update(data)


class ParamContainerFancy(ParamContainer):

    """ Container that takes request in __from_json__ """

    @classmethod
    def __from_json__(cls, request, data):
        obj = cls(**data)
        obj.request = request
        return obj


class TestParam(unittest.TestCase):

    """ Tests for the request.param() method """

    def test_unicode_param(self):
        """ Pull unicode params off of request object """
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        field = _param(request, 'field')
        self.assertEquals(field, 'myfield')
        self.assertTrue(is_string(field, strict=True))

    def test_str_param(self):
        """ Pull binary string param off of request object """
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        field = _param(request, 'field', type=bytes)
        self.assertEquals(field, b'myfield')
        self.assertTrue(is_bytes(field))

    def test_bytes_param(self):
        """ Pull binary string param off of request object """
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        field = _param(request, 'field', type=bytes)
        self.assertEquals(field, b'myfield')
        self.assertTrue(is_bytes(field))

    def test_int_param(self):
        """ Pull integer off of request object """
        request = DummyRequest()
        request.params = {'field': '1'}
        field = _param(request, 'field', type=int)
        self.assertEquals(field, 1)

    def test_list_param(self):
        """ Pull encoded lists off of request object """
        request = DummyRequest()
        request.params = {'field': json.dumps([1, 2, 3])}
        field = _param(request, 'field', type=list)
        self.assertEquals(field, [1, 2, 3])

    def test_dict_param(self):
        """ Pull encoded lists off of request object """
        request = DummyRequest()
        request.params = {'field': json.dumps({'a': 'b'})}
        field = _param(request, 'field', type=dict)
        self.assertEquals(field, {'a': 'b'})

    def test_datetime_param(self):
        """ Pull datetime off of request object """
        request = DummyRequest()
        now = int(time.time())
        request.params = {'field': now}
        field = _param(request, 'field', type=datetime)
        self.assertEquals(time.mktime(field.timetuple()), now)

    def test_bool_param(self):
        """ Pull bool off of request object """
        request = DummyRequest()
        request.params = {'field': 'true'}
        field = _param(request, 'field', type=bool)
        self.assertTrue(field is True)

    def test_missing_param(self):
        """ Raise HTTPBadRequest if param is missing """
        request = DummyRequest()
        request.params = {}
        request.json_body = {}
        myvar = object()
        field = _param(request, 'field', default=myvar)
        self.assertTrue(field is myvar)

    def test_default_param(self):
        """ Return default value if param is missing """
        request = DummyRequest()
        request.params = {}
        request.json_body = {}
        self.assertRaises(HTTPBadRequest, _param, request, 'field')

    def test_object_param(self):
        """ Hydrate an object from json data """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = _param(request, 'field', type=ParamContainer)
        self.assertTrue(isinstance(field, ParamContainer))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])

    def test_object_param_static(self):
        """ Hydrate an object from json data using static method """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = _param(request, 'field', type=ParamContainerStatic)
        self.assertTrue(isinstance(field, ParamContainerStatic))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])

    def test_object_param_request(self):
        """ Hydrate an object from json data and request """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = _param(request, 'field', type=ParamContainerFancy)
        self.assertTrue(isinstance(field, ParamContainerFancy))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])
        self.assertEqual(field.request, request)

    def test_object_param_simple(self):
        """ Hydrate an object from json data directly from constructor """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = _param(request, 'field', type=SimpleParamContainer)
        self.assertTrue(isinstance(field, SimpleParamContainer))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])

    def test_unicode_json_body(self):
        """ Pull unicode params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': 'myfield'}
        request.headers = {'Content-Type': 'application/json'}
        field = _param(request, 'field')
        self.assertEquals(field, 'myfield')
        self.assertTrue(is_string(field, strict=True))

    def test_str_json_body(self):
        """ Pull str params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': 'myfield'}
        request.headers = {'Content-Type': 'application/json'}
        field = _param(request, 'field', type=bytes)
        self.assertEquals(field, b'myfield')
        self.assertTrue(is_bytes(field))

    def test_list_json_body(self):
        """ Pull list params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': [1, 2, 3]}
        request.headers = {'Content-Type': 'application/json'}
        field = _param(request, 'field', type=list)
        self.assertEquals(field, [1, 2, 3])

    def test_dict_json_body(self):
        """ Pull dict params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': {'a': 'b'}}
        request.headers = {'Content-Type': 'application/json'}
        field = _param(request, 'field', type=dict)
        self.assertEquals(field, {'a': 'b'})

    def test_datetime_json_body(self):
        """ Pull datetime params out of json body """
        request = DummyRequest()
        request.params = {}
        now = int(time.time())
        request.json_body = {'field': now}
        request.headers = {'Content-Type': 'application/json'}
        field = _param(request, 'field', type=datetime)
        self.assertEquals(time.mktime(field.timetuple()), now)

    def test_bool_json_body(self):
        """ Pull bool params out of json body """
        request = DummyRequest()
        request.params = {}
        request.headers = {'Content-Type': 'application/json'}
        request.json_body = {'field': True}
        field = _param(request, 'field', type=bool)
        self.assertTrue(field is True)


# pylint: disable=E1120,W0613,C0111

class TestArgify(unittest.TestCase):

    """ Tests for the argify decorator """
    def test_unicode(self):
        """ Pull unicode parameters from request """
        @argify
        def base_req(request, field):
            return field
        context = object()
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        val = base_req(context, request)
        self.assertEquals(val, 'myfield')

    def test_missing(self):
        """ Raise exception if positional arg is missing """
        @argify
        def req(request, field):
            pass
        context = object()
        request = DummyRequest()
        request.params = {}
        request.json_body = {}
        self.assertRaises(HTTPBadRequest, req, context, request)

    def test_default(self):
        """ Don't raise exception if keyword arg is missing """
        @argify
        def req(request, field='myfield'):
            self.assertEquals(field, 'myfield')
        context = object()
        request = DummyRequest()
        request.params = {}
        request.json_body = {}
        req(context, request)

    def test_bool(self):
        """ Pull bool from request automatically """
        @argify(field=bool)
        def req(request, field):
            self.assertTrue(field is True)
        context = object()
        request = DummyRequest()
        request.params = {'field': 'True'}
        req(context, request)

    def test_list(self):
        """ Pull list from request automatically """
        @argify(field=list)
        def req(request, field):
            self.assertEquals(field, [1, 2, 3])
        context = object()
        request = DummyRequest()
        request.params = {'field': json.dumps([1, 2, 3])}
        req(context, request)

    def test_no_alter_if_test(self):
        """ args & kwargs unchanged if called from a test """
        @argify(field=list)
        def req(request, field):
            self.assertEquals(field, [1, 2, 3])
        request = DummyRequest()
        req(request, [1, 2, 3])

    def test_error_on_mismatch(self):
        """ argify throws error if there's an argument mismatch """
        def req(request, field):
            pass
        decorator = argify(foobar=bool)
        self.assertRaises(TypeError, decorator, req)

    def test_kwargs(self):
        """ argify will pass extra kwargs in **kwargs """
        @argify
        def req(request, f1, f2=None, **kwargs):
            self.assertEquals(f1, 'bar')
            self.assertEquals(kwargs, {'foobar': 'baz'})
        context = object()
        request = DummyRequest()
        request.params = {
            'f1': 'bar',
            'foobar': 'baz',
        }
        req(context, request)

    def test_kwargs_json_body(self):
        """ argify will pass extra kwargs in **kwargs in json body """
        @argify
        def req(request, f1, f2=None, **kwargs):
            self.assertEquals(f1, 'bar')
            self.assertEquals(kwargs, {'foobar': 'baz'})
        context = object()
        request = DummyRequest()
        request.params = {}
        request.headers = {'Content-Type': 'application/json'}
        request.json_body = {
            'f1': 'bar',
            'foobar': 'baz',
        }
        req(context, request)