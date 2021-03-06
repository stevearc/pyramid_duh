""" Tests for param utilities """
from __future__ import unicode_literals

import datetime
import time

import calendar
import json
import six
from mock import MagicMock, call, patch
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.testing import DummyRequest

import pyramid_duh
from pyramid_duh.params import argify, param, includeme


try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest


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
        field = param(request, 'field')
        self.assertEquals(field, 'myfield')
        self.assertTrue(isinstance(field, six.text_type))

    def test_unicode_json_body(self):
        """ Pull unicode params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': 'myfield'}
        request.headers = {'Content-Type': 'application/json'}
        field = param(request, 'field')
        self.assertEquals(field, 'myfield')
        self.assertTrue(isinstance(field, six.text_type))

    def test_unicode_param_explicit(self):
        """ Specifying type=unicode checks arg type before returning it """
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        field = param(request, 'field', type=six.text_type)
        self.assertEquals(field, 'myfield')
        self.assertTrue(isinstance(field, six.text_type))

    def test_unicode_param_bad_type(self):
        """ Raise exception if unicode param as incorrect type """
        request = DummyRequest()
        request.params = {'field': 4}
        with self.assertRaises(HTTPBadRequest):
            param(request, 'field', type=six.text_type)

    def test_str_param(self):
        """ Pull binary string param off of request object """
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        field = param(request, 'field', type=bytes)
        self.assertEquals(field, b'myfield')
        self.assertTrue(isinstance(field, six.binary_type))

    def test_str_json_body(self):
        """ Pull str params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': 'myfield'}
        request.headers = {'Content-Type': 'application/json'}
        field = param(request, 'field', type=bytes)
        self.assertEquals(field, b'myfield')
        self.assertTrue(isinstance(field, six.binary_type))

    def test_bytes_param(self):
        """ Pull binary string param off of request object """
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        field = param(request, 'field', type=bytes)
        self.assertEquals(field, b'myfield')
        self.assertTrue(isinstance(field, six.binary_type))

    def test_int_param(self):
        """ Pull integer off of request object """
        request = DummyRequest()
        request.params = {'field': '1'}
        field = param(request, 'field', type=int)
        self.assertEquals(field, 1)

    def test_list_param(self):
        """ Pull encoded lists off of request object """
        request = DummyRequest()
        request.params = {'field': json.dumps([1, 2, 3])}
        field = param(request, 'field', type=list)
        self.assertEquals(field, [1, 2, 3])

    def test_list_json_body(self):
        """ Pull list params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': [1, 2, 3]}
        request.headers = {'Content-Type': 'application/json'}
        field = param(request, 'field', type=list)
        self.assertEquals(field, [1, 2, 3])

    def test_dict_param(self):
        """ Pull encoded dicts off of request object """
        request = DummyRequest()
        request.params = {'field': json.dumps({'a': 'b'})}
        field = param(request, 'field', type=dict)
        self.assertEquals(field, {'a': 'b'})

    def test_dict_json_body(self):
        """ Pull dict params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': {'a': 'b'}}
        request.headers = {'Content-Type': 'application/json'}
        field = param(request, 'field', type=dict)
        self.assertEquals(field, {'a': 'b'})

    def test_dict_param_bad_type(self):
        """ If dict param isn't a dict, raise exception """
        request = DummyRequest()
        request.params = {'field': json.dumps(['a', 'b'])}
        with self.assertRaises(HTTPBadRequest):
            param(request, 'field', type=dict)

    def test_set_param(self):
        """ Pull encoded sets off of request object """
        request = DummyRequest()
        request.params = {'field': json.dumps(['a', 'b'])}
        field = param(request, 'field', type=set)
        self.assertEquals(field, set(['a', 'b']))

    def test_set_json_body(self):
        """ Pull set params out of json body """
        request = DummyRequest()
        request.params = {}
        request.json_body = {'field': set(['a', 'b'])}
        request.headers = {'Content-Type': 'application/json'}
        field = param(request, 'field', type=set)
        self.assertEquals(field, set(['a', 'b']))

    def test_datetime_param(self):
        """ Pull datetime off of request object """
        request = DummyRequest()
        now = int(time.time())
        request.params = {'field': now}
        field = param(request, 'field', type=datetime)
        self.assertEquals(calendar.timegm(field.utctimetuple()), now)

    def test_datetime_json_body(self):
        """ Pull datetime params out of json body """
        request = DummyRequest()
        request.params = {}
        now = int(time.time())
        request.json_body = {'field': now}
        request.headers = {'Content-Type': 'application/json'}
        field = param(request, 'field', type=datetime)
        self.assertEquals(calendar.timegm(field.utctimetuple()), now)

    def test_timedelta_param(self):
        """ Pull timedelta off of request object """
        request = DummyRequest()
        diff = 3600
        request.params = {'field': diff}
        field = param(request, 'field', type=datetime.timedelta)
        self.assertEquals(field, datetime.timedelta(seconds=diff))

    def test_date_param(self):
        """ Pull date off of request object as YYYY-mm-dd """
        request = DummyRequest()
        request.params = {'field': '2014-1-1'}
        field = param(request, 'field', type=datetime.date)
        self.assertEquals(field, datetime.date(2014, 1, 1))

    def test_date_param_ts(self):
        """ Pull date off of request object as unix ts """
        request = DummyRequest()
        now_date = datetime.date(2014, 1, 1)
        now_ts = time.mktime(now_date.timetuple())
        request.params = {'field': now_ts}
        field = param(request, 'field', type=datetime.date)
        self.assertEquals(field, now_date)

    def test_bool_param(self):
        """ Pull bool off of request object """
        request = DummyRequest()
        request.params = {'field': 'true'}
        field = param(request, 'field', type=bool)
        self.assertTrue(field is True)

    def test_bool_json_body(self):
        """ Pull bool params out of json body """
        request = DummyRequest()
        request.params = {}
        request.headers = {'Content-Type': 'application/json'}
        request.json_body = {'field': True}
        field = param(request, 'field', type=bool)
        self.assertTrue(field is True)

    def test_missing_param(self):
        """ Raise HTTPBadRequest if param is missing """
        request = DummyRequest()
        request.params = {}
        request.json_body = {}
        myvar = object()
        field = param(request, 'field', default=myvar)
        self.assertTrue(field is myvar)

    def test_default_param(self):
        """ Return default value if param is missing """
        request = DummyRequest()
        request.params = {}
        request.json_body = {}
        self.assertRaises(HTTPBadRequest, param, request, 'field')

    def test_object_param(self):
        """ Hydrate an object from json data """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = param(request, 'field', type=ParamContainer)
        self.assertTrue(isinstance(field, ParamContainer))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])

    def test_object_param_static(self):
        """ Hydrate an object from json data using static method """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = param(request, 'field', type=ParamContainerStatic)
        self.assertTrue(isinstance(field, ParamContainerStatic))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])

    def test_object_param_request(self):
        """ Hydrate an object from json data and request """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = param(request, 'field', type=ParamContainerFancy)
        self.assertTrue(isinstance(field, ParamContainerFancy))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])
        self.assertEqual(field.request, request)

    def test_object_param_path(self):
        """ Type parameter can be a dotted path """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = param(request, 'field',
                      type='tests.test_params.ParamContainerFancy')
        self.assertTrue(isinstance(field, ParamContainerFancy))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])
        self.assertEqual(field.request, request)

    def test_object_param_simple(self):
        """ Hydrate an object from json data directly from constructor """
        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        field = param(request, 'field', type=SimpleParamContainer)
        self.assertTrue(isinstance(field, SimpleParamContainer))
        self.assertEqual(field.alpha, data['alpha'])
        self.assertEqual(field.beta, data['beta'])

    def test_bad_format(self):
        """ Raise exception if any error during type conversion """
        request = DummyRequest()
        request.params = {'field': 'abc'}
        with self.assertRaises(HTTPBadRequest):
            param(request, 'field', type=int)

    def test_include(self):
        """ Including pyramid_duh.params should add param() as a req method """
        config = MagicMock()
        includeme(config)
        config.add_request_method.assert_called_with(param, name='param')

    @patch('pyramid.config.Configurator.add_request_method')
    def test_include_root(self, add_request_method):
        """ Including pyramid_duh should add param() as a req method """
        config = Configurator()
        pyramid_duh.includeme(config)
        add_request_method.assert_has_calls([call(param, name='param')])

    def test_validate(self):
        """ param() can run a validation check on parameter values """
        request = DummyRequest()
        request.params = {'field': 'foobar'}
        validate = lambda x: x.startswith('foo')
        field = param(request, 'field', validate=validate)
        self.assertEquals(field, 'foobar')

    def test_validate_failure(self):
        """ if param() fails validation check, raise exception """
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        validate = lambda x: x.startswith('foo')
        with self.assertRaises(HTTPBadRequest):
            param(request, 'field', validate=validate)


# pylint: disable=E1120,W0613,C0111,E1101
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
        def req(request, field):  # pragma: no cover
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

    def test_default_override(self):
        """ If keyword arg is present, use that value """
        @argify
        def req(request, field='myfield'):
            self.assertEquals(field, 'otherfield')
        context = object()
        request = DummyRequest()
        request.params = {'field': 'otherfield'}
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
        def req(request, field):  # pragma: no cover
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

    def test_pass_context(self):
        """ argify will pass on context, request arguments to view """
        @argify
        def base_req(context, request, field):
            return context, request, field
        context = object()
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        val = base_req(context, request)
        self.assertEquals(val, (context, request, 'myfield'))

    def test_validate(self):
        """ argify() can run a validation check on parameter values """
        validate = lambda x: x.startswith('foo')

        @argify(field=(six.text_type, validate))
        def base_req(request, field):
            return field
        context = object()
        request = DummyRequest()
        request.params = {'field': 'foobar'}
        val = base_req(context, request)
        self.assertEquals(val, 'foobar')

    def test_validate_failure(self):
        """ if argify fails validation check, raise exception """
        validate = lambda x: x.startswith('foo')

        @argify(field=(six.text_type, validate))
        def base_req(request, field):  # pragma: no cover
            return field
        context = object()
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        with self.assertRaises(HTTPBadRequest):
            base_req(context, request)

    def test_validate_kwargs_failure(self):
        """ if argify fails validation check for kwargs, raise exception """
        validate = lambda x: x.startswith('foo')

        @argify(field=(six.text_type, validate))
        def base_req(request, field=None):  # pragma: no cover
            return field
        context = object()
        request = DummyRequest()
        request.params = {'field': 'myfield'}
        with self.assertRaises(HTTPBadRequest):
            base_req(context, request)

    def test_decorate_class(self):
        """ Argify can decorate view methods of a class """
        class MyView(object):

            def __init__(self, request):
                self.request = request

            @argify
            def myview(self, field):
                return field

        request = DummyRequest()
        request.params = {'field': 'foobar'}
        vc = MyView(request)
        val = vc.myview()
        self.assertEquals(val, 'foobar')

    def test_decorate_class_pass_args(self):
        """ Can pass arguments directly to decorated class """

        class MyView(object):

            def __init__(self, request):
                self.request = request

            @argify
            def myview(self, field):
                return field

        request = DummyRequest()
        vc = MyView(request)
        val = vc.myview('foobar')
        self.assertEquals(val, 'foobar')

    def test_bad_view_class(self):
        """ View classes must have a 'request' attribute """
        class MyView(object):

            def __init__(self, request):
                pass

            @argify
            def myview(self, field):
                return field

        request = DummyRequest()
        vc = MyView(request)
        with self.assertRaises(AttributeError):
            vc.myview('foobar')

    def test_dotted_path(self):
        """ Argify type can be a dotted path to a type """

        @argify(field='tests.test_params.ParamContainerFancy')
        def myview(request, field):
            return field

        request = DummyRequest()
        data = {'alpha': 'a', 'beta': 'b'}
        request.params = {'field': json.dumps(data)}
        context = object()
        ret = myview(context, request)
        self.assertTrue(isinstance(ret, ParamContainerFancy))
        self.assertEqual(ret.alpha, data['alpha'])
        self.assertEqual(ret.beta, data['beta'])
        self.assertEqual(ret.request, request)

    def test_multi_param_arg(self):
        """ Args can be defined to consume multiple parameters """
        class User(object):

            def __init__(self, userid, access_token):
                self.userid = userid
                self.access_token = access_token

            @classmethod
            @argify(userid=int)
            def __from_json__(cls, userid, access_token):
                return cls(userid, access_token)

        @argify(user=User)
        def myview(request, user):
            return user

        context = object()
        request = DummyRequest()
        request.params = {'userid': 1, 'access_token': 'a'}
        val = myview(context, request)
        self.assertEqual(val.userid, 1)
        self.assertEqual(val.access_token, 'a')

    def test_multi_param_arg_test(self):
        """ Tests can pass args directly to multi param view """
        class User(object):

            def __init__(self, userid, access_token):
                self.userid = userid
                self.access_token = access_token

            @classmethod
            @argify(userid=int)
            def __from_json__(cls, userid, access_token):
                return cls(userid, access_token)

        @argify(user=User)
        def myview(request, user):
            return user

        request = DummyRequest()
        user = User(1, 'a')
        val = myview(request, user)
        self.assertTrue(val is user)

    def test_multi_param_static_arg(self):
        """ Classes with static methods can consume multiple parameters """
        class User(object):

            def __init__(self, userid, access_token):
                self.userid = userid
                self.access_token = access_token

            @staticmethod
            @argify(userid=int)
            def __from_json__(userid, access_token):
                return User(userid, access_token)

        @argify(user=User)
        def myview(request, user):
            return user

        context = object()
        request = DummyRequest()
        request.params = {'userid': 1, 'access_token': 'a'}
        val = myview(context, request)
        self.assertEqual(val.userid, 1)
        self.assertEqual(val.access_token, 'a')

    def test_multi_param_static_test(self):
        """ Tests can pass args directly to static method multi param view """
        class User(object):

            def __init__(self, userid, access_token):
                self.userid = userid
                self.access_token = access_token

            @staticmethod
            @argify(userid=int)
            def __from_json__(userid, access_token):
                return User(userid, access_token)

        @argify(user=User)
        def myview(request, user):
            return user

        request = DummyRequest()
        user = User(1, 'a')
        val = myview(request, user)
        self.assertTrue(val is user)

    def test_multi_param_factory(self):
        """ Factory functions can use multi-param args """
        class User(object):

            def __init__(self, userid, access_token):
                self.userid = userid
                self.access_token = access_token

        @argify(userid=int)
        def user_factory(userid, access_token):
            return User(userid, access_token)

        @argify(user=user_factory)
        def myview(request, user):
            return user

        context = object()
        request = DummyRequest()
        request.params = {'userid': 1, 'access_token': 'a'}
        val = myview(context, request)
        self.assertEqual(val.userid, 1)
        self.assertEqual(val.access_token, 'a')

    def test_multi_param_factory_test(self):
        """ Tests can pass args directly to view using multi-param factory """
        class User(object):

            def __init__(self, userid, access_token):
                self.userid = userid
                self.access_token = access_token

        @argify(userid=int)
        def user_factory(userid, access_token):
            return User(userid, access_token)

        @argify(user=user_factory)
        def myview(request, user):
            return user

        request = DummyRequest()
        user = User(1, 'a')
        val = myview(request, user)
        self.assertTrue(val is user)
