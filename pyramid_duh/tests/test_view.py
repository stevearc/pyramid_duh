# encoding: utf-8
""" Tests for view utilities """
import unittest
from mock import MagicMock, patch, call
from pyramid.httpexceptions import HTTPFound
from pyramid.testing import DummyRequest
from pyramid_duh.params import argify
from pyramid_duh.view import SubpathPredicate, addslash, includeme
import pyramid_duh
from pyramid.config import Configurator


class TestSubpath(unittest.TestCase):

    """ Test the subpath predicate """

    def setUp(self):
        super(TestSubpath, self).setUp()
        self.request = DummyRequest()
        self.request.named_subpaths = None

    def test_match(self):
        """ Subpatch matches globs """
        matcher = SubpathPredicate(('*'), None)
        self.request.subpath = ('mypath',)
        result = matcher(None, self.request)
        self.assertTrue(result)

    def test_len_mismatch(self):
        """ Subpath mismatch if incorrect length """
        matcher = SubpathPredicate(('*'), None)
        self.request.subpath = ('mypath', 'path2')
        result = matcher(None, self.request)
        self.assertFalse(result)

    def test_glob_mismatch(self):
        """ No match if glob doesn't match """
        matcher = SubpathPredicate(('foo*'), None)
        self.request.subpath = ('bar',)
        result = matcher(None, self.request)
        self.assertFalse(result)

    def test_match_pcre(self):
        """ Subpath matches PCREs """
        matcher = SubpathPredicate(('/foo.*/r'), None)
        self.request.subpath = ('foo',)
        result = matcher(None, self.request)
        self.assertTrue(result)

    def test_pcre_mismatch(self):
        """ No match if PCRE doesn't match """
        matcher = SubpathPredicate(('/foo.*/r'), None)
        self.request.subpath = ('bar',)
        result = matcher(None, self.request)
        self.assertFalse(result)

    def test_named_subpaths(self):
        """ Named subpaths are extracted """
        matcher = SubpathPredicate(('mypath/*'), None)
        self.request.subpath = ('bar',)
        result = matcher(None, self.request)
        self.assertTrue(result)
        self.assertEqual(self.request.named_subpaths, {'mypath': 'bar'})

    def test_named_subpaths_pcre(self):
        """ Named subpaths are extracted on PCRE match """
        matcher = SubpathPredicate(('mypath/.*/r'), None)
        self.request.subpath = ('bar',)
        result = matcher(None, self.request)
        self.assertTrue(result)
        self.assertEqual(self.request.named_subpaths, {'mypath': 'bar'})

    def test_named_subpaths_pcre_group(self):
        """ Named subpaths can be extracted by PCRE match groups """
        matcher = SubpathPredicate(('mypath/(?P<type>\w+):(?P<value>\w+)/r'),
                                   None)
        self.request.subpath = ('foo:bar',)
        result = matcher(None, self.request)
        self.assertTrue(result)
        self.assertEqual(self.request.named_subpaths, {
            'mypath': 'foo:bar',
            'type': 'foo',
            'value': 'bar',
        })

    def test_pcre_flag_a(self):  # pragma: no cover
        """ Can match ascii-only """
        import re
        if not hasattr(re, 'A'):
            return
        matcher = SubpathPredicate(('path1/\w+/ra'), None)
        self.request.subpath = ('ಠ_ಠ',)
        result = matcher(None, self.request)
        self.assertFalse(result)

    def test_pcre_flag_i(self):
        """ Can do case-insensitive matching """
        matcher = SubpathPredicate(('/foo/ri'), None)
        self.request.subpath = ('FOO',)
        result = matcher(None, self.request)
        self.assertTrue(result)

    def test_optional_subpaths(self):
        """ Subpaths can be marked as optional """
        matcher = SubpathPredicate(('*', 'opt/*/?'), None)
        self.request.subpath = ('foo',)
        result = matcher(None, self.request)
        self.assertTrue(result)
        self.assertTrue('opt' not in self.request.named_subpaths)

        self.request.subpath = ('foo', 'bar')
        result = matcher(None, self.request)
        self.assertTrue(result)
        self.assertTrue('opt' in self.request.named_subpaths)

    def test_non_optional_subpaths(self):
        """ If subpath not marked as optional, it is mandatory """
        matcher = SubpathPredicate(('*', '*'), None)
        self.request.subpath = ('foo',)
        result = matcher(None, self.request)
        self.assertFalse(result)

    def test_format(self):
        """ String format should be readable """
        pred = SubpathPredicate(('*', '*'), None)
        self.assertEqual(pred.text(), "subpath = ('*', '*')")

    def test_include(self):
        """ Including pyramid_duh.view adds the predicate method """
        config = MagicMock()
        includeme(config)
        config.add_view_predicate.assert_called_with('subpath',
                                                     SubpathPredicate)


# pylint: disable=C0111,E1101,E1121
class TestAddslash(unittest.TestCase):

    """ Tests for @addslash """

    def test_addslash_redirect(self):
        """ addslash causes redirect if path_url doesn't end in / """
        @addslash
        def myview(request):  # pragma: no cover
            return 'foobar'
        context = object()
        request = DummyRequest()
        request.path_url = '/noslash'
        ret = myview(context, request)
        self.assertTrue(isinstance(ret, HTTPFound))
        self.assertEqual(ret.location, request.path_url + '/')

    def test_addslash_redirect_query(self):
        """ addslash keeps the query string """
        @addslash
        def myview(request):  # pragma: no cover
            return 'foobar'
        context = object()
        request = DummyRequest()
        request.query_string = 'foo=1&bar=2'
        request.path_url = '/noslash'
        ret = myview(context, request)
        self.assertTrue(isinstance(ret, HTTPFound))
        self.assertEqual(ret.location, request.path_url + '/?' +
                         request.query_string)

    def test_pass_context(self):
        """ addslash passes on the context variable if needed """
        @addslash
        def myview(context, request):
            return context, request
        context = object()
        request = DummyRequest()
        request.path_url = '/'
        ret = myview(context, request)
        self.assertEqual(ret, (context, request))

    def test_pass_request_only(self):
        """ addslash passes on just the request if that's all that's needed """
        @addslash
        def myview(request):
            return request
        context = object()
        request = DummyRequest()
        request.path_url = '/'
        ret = myview(context, request)
        self.assertEqual(ret, request)

    def test_passthrough_argify_unit_tests(self):
        """ addslash doesn't interfere with unit tests that use @argify """
        @addslash
        @argify
        def myview(request, *args, **kwargs):
            return args, kwargs
        args = ('a', 'b')
        kwargs = {'c': 1, 'd': 2}
        request = DummyRequest()
        ret = myview(request, *args, **kwargs)
        self.assertEqual(ret, (args, kwargs))
