""" Utilities for view configuration """
import fnmatch
import re

import functools
import inspect
from pyramid.httpexceptions import HTTPFound

from .compat import is_string
from .params import is_request


def match(pattern, path, flags):
    """
    Check if a pattern matches a path

    Parameters
    ----------
    pattern : str
        Glob or PCRE
    path : str or None
        The path to check, or None if no path
    flags : {'r', 'i', 'a', '?'}
        Special match flags. These may be combined (e.g. 'ri?'). See the notes
        for an explanation of the different values.

    Returns
    -------
    match : bool or SRE_Match
        A boolean indicating the match status, or the regex match object if
        there was a successful PCRE match.

    Notes
    -----
    ====  ==============================================
    Flag  Description
    ====  ==============================================
    r     Match using PCRE (default glob)
    i     Case-insensitive match (must be used with 'r')
    a     ASCII-only match (must be used with 'r', python 3 only)
    ?     Path is optional (return True if path is None)
    ====  ==============================================

    """
    if path is None:
        if '?' in flags:
            return True
        else:
            return False
    if 'r' in flags:
        re_flags = 0
        for char in flags:
            if char == 'i':
                re_flags |= re.I
            elif char == 'a' and hasattr(re, 'A'):  # pragma: no cover
                re_flags |= re.A  # pylint: disable=E1101
        return re.match('^%s$' % pattern, path, re_flags)
    else:
        return fnmatch.fnmatchcase(path, pattern)


class SubpathPredicate(object):

    """
    Generate a custom predicate that matches subpaths

    Parameters
    ----------
    *paths : list
        List of match specs.

    Notes
    -----
    A match spec may take one of three forms:

    .. code-block:: python

        'glob'
        'name/glob'
        'name/glob/flags'

    The name is optional, but if you wish to specify flags then you have to
    include the leading slash:

    .. code-block:: python

        # A match spec with flags and no name
        '/foo.*/r'

    The names will be accessible from the ``request.named_subpaths`` attribute.

    .. code-block:: python

        @view_config(context=Root, name='simple', subpath=('package/*', 'version/*/?'))
        def simple(request)
            pkg = request.named_subpaths['package']
            version = request.named_subpaths.get('version')
            request.response.body = '<h1>%s</h1>' % package
            if version is not None:
                request.response.body += '<h4>version: %s</h4>' % version
            return request.response

    See :meth:`.match` for more information on match flags`

    """

    def __init__(self, paths, config):
        if is_string(paths):
            paths = (paths,)
        self.paths = paths
        self.config = config

    def text(self):
        """ Display name """
        return 'subpath = %s' % (self.paths,)

    phash = text

    def __call__(self, context, request):
        named_subpaths = {}
        if len(request.subpath) > len(self.paths):
            return False
        for i in range(len(self.paths)):
            spec = self.paths[i]
            pieces = spec.split('/', 2)
            if len(pieces) == 1:
                name, pattern, flags = None, pieces[0], ''
            elif len(pieces) == 2:
                name, pattern, flags = pieces[0], pieces[1], ''
            else:
                name, pattern, flags = pieces

            if i < len(request.subpath):
                path = request.subpath[i]
            else:
                path = None
            result = match(pattern, path, flags)
            if not result:
                return False
            if name and path is not None:
                named_subpaths[name] = path
            if hasattr(result, 'groupdict'):
                named_subpaths.update(result.groupdict())

        request.named_subpaths = named_subpaths
        return True


def addslash(fxn):
    """
    View decorator that adds a trailing slash

    Notes
    -----
    Usage:

    .. code-block:: python

        @view_config(context=MyCtxt, renderer='json')
        @addslash
        def do_view(request):
            return 'cool data'

    """
    argspec = inspect.getargspec(fxn)

    @functools.wraps(fxn)
    def slash_redirect(*args, **kwargs):
        """ Perform the redirect or pass though to view """
        # pyramid always calls with (context, request) arguments
        if len(args) == 2 and is_request(args[1]):
            request = args[1]
            if not request.path_url.endswith('/'):
                new_url = request.path_url + '/'
                if request.query_string:
                    new_url += '?' + request.query_string
                return HTTPFound(location=new_url)
            if len(argspec.args) == 1 and argspec.varargs is None:
                return fxn(request)
            else:
                return fxn(*args)
        else:
            # Otherwise, it's likely a unit test. Don't change anything.
            return fxn(*args, **kwargs)

    return slash_redirect


def includeme(config):
    """ Add the custom view predicates """
    config.add_view_predicate('subpath', SubpathPredicate)
