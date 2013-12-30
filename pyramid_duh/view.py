""" Utilities for view configuration """
import fnmatch
import itertools
import re

import inspect
from functools import partial, wraps
from pyramid.httpexceptions import HTTPFound


class SubpathPredicate(object):

    """
    Generate a custom predicate that matches subpaths

    Parameters
    ----------
    *paths : list
        List of globs or regexes. The subpaths must match these exactly.
    pcre : bool
        Use PCRE's instead of globs (default False)

    Notes
    -----
    This view will match ``/simple/foo``, ``/simple/bar/``, and
    ``/simple/lkjlfkjalkdsf``. It will **not** match ``/simple`` or
    ``/simple/foo/bar``.

    .. code-block:: python

        @view_config(context=Root, name='simple', subpath=('*'))
        def simple(request):
            request.response.body = '<h1>Hello</h1>'
            return request.response

    """

    def __init__(self, paths, config, pcre=False):
        self.paths = paths
        self.config = config
        if pcre:
            self.match = lambda pattern, path: bool(re.match('^%s$' % pattern,
                                                             path))
        else:
            self.match = lambda pattern, path: fnmatch.fnmatch(path, pattern)

    def text(self):
        """ Display name """
        return 'subpath = %s' % (self.paths,)

    phash = text

    def __call__(self, context, request):
        if len(request.subpath) != len(self.paths):
            return False
        for pattern, path in itertools.izip(self.paths, request.subpath):
            if not self.match(pattern, path):
                return False
        return True


def addslash(fxn):
    """ View decorator that adds a trailing slash """
    argspec = inspect.getargspec(fxn)

    @wraps(fxn)
    def slash_redirect(*args):
        """ Perform the redirect or pass though to view """
        if len(args) == 1:
            request = args[0]
        else:
            request = args[1]
        if not request.url.endswith('/'):
            return HTTPFound(location=request.url + '/')
        if len(argspec.args) == 1 and argspec.varargs is None:
            return fxn(request)
        else:
            return fxn(*args)

    return slash_redirect


def includeme(config):
    """ Add the custom view predicates """
    config.add_view_predicate('subpath', SubpathPredicate)
    config.add_view_predicate('subpath_pcre', partial(SubpathPredicate,
                                                      pcre=True))
