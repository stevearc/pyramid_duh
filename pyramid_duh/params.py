""" Utilities for request parameters """
import datetime

import functools
import inspect
import json
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.interfaces import IRequest
from pyramid.settings import asbool
# pylint: disable=F0401,E0611
from zope.interface.exceptions import DoesNotImplement
from zope.interface.verify import verifyObject
# pylint: enable=F0401,E0611


NO_ARG = object()


def _param(request, name, default=NO_ARG, type=None):
    """
    Access a parameter and perform type conversion

    Parameters
    ----------
    request : :class:`~pyramid.request.Request`
    name : str
        The name of the parameter to retrieve
    default : object, optional
        The default value to use if none is found
    type : object, optional
        The type to convert the argument to

    Raises
    ------
    exc : :class:`~pyramid.httpexceptions.HTTPBadRequest`
        If a parameter is requested that does not exist and no default was
        provided

    """
    params, loads = _params_from_request(request, default != NO_ARG)
    return _param_from_dict(params, name, default, type, loads)


def _params_from_request(request, allow_missing):
    """
    Pull the relevant parameters off the request

    Uses query params by default. If no query params are present, it uses
    json_body

    Parameters
    ----------
    request : :class:`~pyramid.request.Request`
    allow_missing : bool
        If False and no params found, raise a 400

    Returns
    -------
    params : dict
    loads : bool
        If true, any lists/dicts in the params need to be json decoded

    """
    if request.params:
        return request.params, True
    else:
        try:
            return request.json_body, False
        except ValueError:
            if allow_missing:
                return {}, False
            else:
                raise HTTPBadRequest('No request parameters found!')


def _param_from_dict(params, name, default=NO_ARG, type=None, loads=True):
    """
    Pull a parameter out of a dict and perform type conversion

    Parameters
    ----------
    params : dict
    name : str
        The name of the parameter to retrieve
    default : object
        The default value to use if the parameter is missing
    type : type
        A python type such as str, list, dict, bool, or datetime
    loads : bool
        If True, json decode list/dict data types

    Raises
    ------
    exc : :class:`~pyramid.httpexceptions.HTTPBadRequest`
        If the parameter is missing and no default specified

    """
    try:
        arg = params[name]
    except KeyError:
        if default is NO_ARG:
            raise HTTPBadRequest('Missing argument %s' % name)
        else:
            return default
    try:
        if type is None or type is unicode:
            return arg
        elif type is str:
            return arg.encode("utf8")
        elif type is list or type is dict:
            if loads:
                arg = json.loads(arg)
            if not isinstance(arg, type):
                raise HTTPBadRequest("Argument '%s' is the wrong type!" % name)
            return arg
        elif type is datetime.datetime or type is datetime:
            return datetime.datetime.fromtimestamp(float(arg))
        elif type is bool:
            return asbool(arg)
        else:
            return type(arg)
    except:
        raise HTTPBadRequest('Badly formatted parameter "%s"' % name)


def argify(*args, **type_kwargs):
    """
    Request decorator for automagically passing in request parameters

    Notes
    -----
    Here is a sample use case::

        @argify(foo=dict, ts=datetime)
        def handle_request(request, foo, ts, bar='baz'):
            # do request handling

    No special type is required for strings::

        @argify
        def handle_request(request, foo, bar='baz'):
            # do request handling (both 'foo' and 'bar' are strings)

    If any positional arguments are missing, it will raise a HTTPBadRequest
    exception. If any keyword arguments are missing, it will simply use
    whatever the default value is.

    Note that unit tests should be unaffected by this decorator. This should be
    valid::

        @argify
        def myrequest(request, var1, var2='foo'):
            return 'bar'

        class TestReq(unittest.TestCase):
            def test_my_request(self):
                request = pyramid.testing.DummyRequest()
                retval = myrequest(request, 5, var2='foobar')
                self.assertEqual(retval, 'bar')

    """
    def wrapper(fxn):
        """ Function decorator """
        argspec = inspect.getargspec(fxn)
        if argspec.defaults is not None:
            required = set(argspec.args[:-len(argspec.defaults)])
            optional = set(argspec.args[-len(argspec.defaults):])
        else:
            required = set(argspec.args)
            optional = ()

        for type_arg in type_kwargs:
            if type_arg not in required and type_arg not in optional:
                raise TypeError("Argument '%s' specified in argify, but not "
                                "present in function definition" % type_arg)

        @functools.wraps(fxn)
        def param_twiddler(*args, **kwargs):
            """ The actual wrapper function that pulls out the params """
            # If the second arg is the request, this is called from pyramid
            if len(args) == 2 and len(kwargs) == 0 and is_request(args[1]):
                context, request = args  # pylint: disable=W0632
                scope = {}
                params, loads = _params_from_request(request,
                                                     len(required) == 0)
                params = dict(params)
                for param in required:
                    if param == 'context':
                        scope['context'] = context
                    elif param == 'request':
                        scope['request'] = request
                    else:
                        scope[param] = _param_from_dict(params, param, NO_ARG,
                                                        type_kwargs.get(param),
                                                        loads=loads)
                        params.pop(param)
                no_val = object()
                for param in optional:
                    val = _param_from_dict(params, param, no_val,
                                           type_kwargs.get(param), loads)
                    params.pop(param, None)
                    if val is not no_val:
                        scope[param] = val
                if argspec.keywords is not None:
                    scope.update(params)
                return fxn(**scope)
            else:
                # Otherwise, it's likely a unit test. Don't alter args at all.
                return fxn(*args, **kwargs)
        return param_twiddler

    if len(args) == 1 and len(type_kwargs) == 0 and inspect.isfunction(args[0]):
        # @argify
        # def fxn(request, var1, var2):
        return wrapper(args[0])
    else:
        # @argify(var1=bool, var2=list)
        # def fxn(request, var1, var2):
        return wrapper


def is_request(obj):
    """ Check if an object looks like a request """
    try:
        return verifyObject(IRequest, obj)
    except DoesNotImplement:
        return False


def includeme(config):
    """ Add parameter utilities """
    config.add_request_method(_param, name='param')
