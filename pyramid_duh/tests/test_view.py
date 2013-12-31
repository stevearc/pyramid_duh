# encoding: utf-8
""" Tests for view utilities """
import unittest
from pyramid.testing import DummyRequest
from pyramid_duh.view import SubpathPredicate


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

    def test_pcre_flag_a(self):
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
