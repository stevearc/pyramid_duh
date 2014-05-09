""" Utilities for request parameters """
import datetime

import functools
import inspect
import json
import six
from pyramid.httpexceptions import HTTPBadRequest, HTTPException
from pyramid.interfaces import IRequest
from pyramid.path import DottedNameResolver
from pyramid.settings import asbool
# pylint: disable=F0401,E0611
from zope.interface.exceptions import DoesNotImplement
from zope.interface.verify import verifyObject
# pylint: enable=F0401,E0611


NO_ARG = object()
__resolver__ = DottedNameResolver(__name__)


def param(request, name, default=NO_ARG, type=None, validate=None):
    """
    Access a parameter and perform type conversion.

    Parameters
    ----------
    request : :class:`~pyramid.request.Request`
    name : str
        The name of the parameter to retrieve
    default : object, optional
        The default value to use if none is found
    type : object, optional
        The type to convert the argument to. All python primitives are
        supported, as well as ``date`` and ``datetime``. You may also pass in a
        factory function or an object that has a static ``__from_json__``
        method.
    validate : callable, optional
        Callable test to validate parameter value

    Raises
    ------
    exc : :class:`~pyramid.httpexceptions.HTTPBadRequest`
        If a parameter is requested that does not exist and no default was
        provided

    Returns
    -------
    arg : object

    """
    params, loads = _params_from_request(request)
    return _param_from_dict(request, params, name, default, type, validate,
                            loads)


def _params_from_request(request):
    """
    Pull the relevant parameters off the request.

    Parameters
    ----------
    request : :class:`~pyramid.request.Request`

    Returns
    -------
    params : dict
    loads : bool
        If true, any lists/dicts in the params need to be json decoded

    """
    content_type = request.headers.get('Content-Type', '').split(';')[0]
    if content_type == 'application/json':
        return request.json_body, False
    else:
        return request.params, True


def _param_from_dict(request, params, name, default=NO_ARG, type=None,
                     validate=None, loads=True):
    """
    Pull a parameter out of a dict and perform type conversion.

    Parameters
    ----------
    request : :class:`~pyramid.request.Request`
    params : dict
    name : str
        The name of the parameter to retrieve
    default : object
        The default value to use if the parameter is missing
    type : type
        A python type such as str, list, dict, bool, or datetime
    validate : callable, optional
        Callable test to validate parameter value
    loads : bool
        If True, json decode list/dict data types

    Raises
    ------
    exc : :class:`~pyramid.httpexceptions.HTTPBadRequest`
        If the parameter is missing and no default specified

    """
    type = __resolver__.maybe_resolve(type)
    # If the type arg is wrapped with @argify, then it is a multi-param
    # argument and retrieves its parameters directly
    if type is not None:
        if getattr(type, '__argify__', False):
            return type(request.context, request)
        elif hasattr(type, '__from_json__'):
            if getattr(type.__from_json__, '__argify__', False):
                return type.__from_json__(request.context, request)

    try:
        arg = params[name]
    except KeyError:
        if default is NO_ARG:
            raise HTTPBadRequest("Missing argument '%s'" % name)
        else:
            return default
    try:
        if type is None:
            value = arg
        elif type is six.text_type or type is six.string_types:
            if not isinstance(arg, six.string_types):
                raise HTTPBadRequest("Argument '%s' is the wrong type!" % name)
            value = arg
        elif type is six.binary_type:
            value = arg.encode("utf8")
        elif type is list or type is dict:
            if loads:
                arg = json.loads(arg)
            if not isinstance(arg, type):
                raise HTTPBadRequest("Argument '%s' is the wrong type!" % name)
            value = arg
        elif type is set:
            if loads:
                arg = json.loads(arg)
            value = set(arg)
        elif type is datetime.datetime or type is datetime:
            value = datetime.datetime.utcfromtimestamp(float(arg))
        elif type is datetime.timedelta:
            value = datetime.timedelta(seconds=float(arg))
        elif type is datetime.date:
            if (isinstance(arg, six.integer_types) or
                    isinstance(arg, float) or arg.isdigit()):
                value = datetime.datetime.utcfromtimestamp(int(arg)).date()
            else:
                value = datetime.datetime.strptime(arg, '%Y-%m-%d').date()
        elif type is bool:
            value = asbool(arg)
        elif type in six.integer_types or type is float:
            value = type(arg)
        else:
            if loads:
                arg = json.loads(arg)
            if hasattr(type, '__from_json__'):
                argspec = inspect.getargspec(type.__from_json__)
                args = list(argspec.args)
                # Pop the leading 'cls' if this is a classmethod
                if inspect.ismethod(type.__from_json__):
                    args.pop(0)
                if len(args) == 1 and argspec.varargs is None:
                    value = type.__from_json__(arg)
                else:
                    value = type.__from_json__(request, arg)
            else:
                value = type(arg)
        if validate is not None:
            if not validate(value):
                raise HTTPBadRequest("Validation check on '%s' failed" % name)
        return value
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPBadRequest("Badly formatted parameter '%s'" % name)


def argify(*args, **type_kwargs):
    """
    Request decorator for automagically passing in request parameters.

    Notes
    -----
    Here is a sample use case:

    .. code-block:: python

        @argify(foo=dict, ts=datetime)
        def handle_request(request, foo, ts, bar='baz'):
            # do request handling

    No special type is required for strings:

    .. code-block:: python

        @argify
        def handle_request(request, foo, bar='baz'):
            # do request handling (both 'foo' and 'bar' are strings)

    If any positional arguments are missing, it will raise a
    :class:`~pyramid.httpexceptions.HTTPBadRequest` exception. If any keyword
    arguments are missing, it will simply use whatever the default value is.

    Note that unit tests should be unaffected by this decorator. This is valid:

    .. code-block:: python

        @argify
        def myview(request, var1, var2='foo'):
            return 'bar'

        class TestReq(unittest.TestCase):
            def test_my_request(self):
                request = pyramid.testing.DummyRequest()
                retval = myview(request, 5, var2='foobar')
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
            scope = {}
            self = None
            # If @argify is decorating a classmethod, inject the 'cls' arg
            # with no modification
            if 'cls' in required:
                args = list(args)
                scope['cls'] = args.pop(0)
                required.remove('cls')

            if 'self' in required:
                self = args[0]
                if not hasattr(self, 'request'):
                    raise AttributeError("View class %s has no attribute "
                                         "'request'" % self)
                request = self.request
                context = getattr(self, 'context', None)
                # Multiple args passed in, it's likely a unit test.
                # Don't alter args at all.
                if len(args) != 1 or len(kwargs) != 0:
                    return fxn(*args, **kwargs)

            # pyramid always calls with (context, request) arguments
            # If it doesn't, it's likely a unit test. Don't alter args at all.
            elif not (len(args) == 2 and len(kwargs) == 0 and
                      is_request(args[1])):
                return fxn(*args, **kwargs)
            else:
                context, request = args[0], args[1]

            params, loads = _params_from_request(request)
            params = dict(params)
            for arg in required:
                type_spec = type_kwargs.get(arg)
                if (isinstance(type_spec, tuple) or
                        isinstance(type_spec, list)):
                    type_def, validate = type_spec
                else:
                    type_def = type_spec
                    validate = None

                if arg == 'context':
                    scope['context'] = context
                elif arg == 'request':
                    scope['request'] = request
                elif arg == 'self':
                    scope['self'] = self
                else:
                    scope[arg] = _param_from_dict(
                        request, params, arg, NO_ARG,
                        type_def, validate, loads=loads)
                    params.pop(arg, None)
            no_val = object()
            for arg in optional:
                type_spec = type_kwargs.get(arg)
                if (isinstance(type_spec, tuple) or
                        isinstance(type_spec, list)):
                    type_def, validate = type_spec
                else:
                    type_def = type_spec
                    validate = None
                val = _param_from_dict(request, params, arg, no_val,
                                       type_def, validate, loads)
                params.pop(arg, None)
                if val is not no_val:
                    scope[arg] = val
            if argspec.keywords is not None:
                scope.update(params)
            return fxn(**scope)

        param_twiddler.__argify__ = True
        return param_twiddler

    wrapper.__argify__ = True

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
    config.add_request_method(param, name='param')
