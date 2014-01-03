""" Tests for auth module """
from mock import patch, MagicMock
from pyramid.config import Configurator
from pyramid.testing import DummyRequest
from pyramid_duh.auth import includeme, MixedAuthenticationPolicy

try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest


class TestAuth(unittest.TestCase):

    """ Tests for auth module """

    def setUp(self):
        super(TestAuth, self).setUp()
        self.request = DummyRequest()

    def tearDown(self):
        super(TestAuth, self).tearDown()
        patch.stopall()

    def test_add_auth_directive(self):
        """ adding a policy via the config directive calls add_policy """
        with patch.object(MixedAuthenticationPolicy,
                          'add_policy') as add_policy:
            config = Configurator()
            includeme(config)
            policy = 'foobar'
            config.add_authentication_policy('foobar')
            add_policy.assert_called_with(policy)

    def test_add_auth_to_mixed(self):
        """ Adding a policy to MixedAuthenticationPolicy stores it in a list """
        policy = MixedAuthenticationPolicy()
        policy.add_policy('foobar')
        self.assertEqual(policy._policies, ['foobar'])

    def test_first_auth_userid(self):
        """ authenticated_userid returns first valid userid """
        p1, p2 = MagicMock(), MagicMock()
        policy = MixedAuthenticationPolicy(p1, p2)
        userid = policy.authenticated_userid(self.request)
        self.assertEqual(userid, p1.authenticated_userid())
        self.assertFalse(p2.authenticated_userid.called)

    def test_no_auth_userid(self):
        """ authenticated_userid returns None if no valid userid """
        p1, p2 = MagicMock(), MagicMock()
        p1.authenticated_userid.return_value = None
        p2.authenticated_userid.return_value = None
        policy = MixedAuthenticationPolicy(p1, p2)
        userid = policy.authenticated_userid(self.request)
        self.assertIsNone(userid)
        self.assertTrue(p1.authenticated_userid.called)
        self.assertTrue(p2.authenticated_userid.called)

    def test_first_unauth_userid(self):
        """ unauthenticated_userid returns first valid userid """
        p1, p2 = MagicMock(), MagicMock()
        policy = MixedAuthenticationPolicy(p1, p2)
        userid = policy.unauthenticated_userid(self.request)
        self.assertEqual(userid, p1.unauthenticated_userid())
        self.assertFalse(p2.unauthenticated_userid.called)

    def test_no_unauth_userid(self):
        """ unauthenticated_userid returns None if no valid userid """
        p1, p2 = MagicMock(), MagicMock()
        p1.unauthenticated_userid.return_value = None
        p2.unauthenticated_userid.return_value = None
        policy = MixedAuthenticationPolicy(p1, p2)
        userid = policy.unauthenticated_userid(self.request)
        self.assertIsNone(userid)
        self.assertTrue(p1.unauthenticated_userid.called)
        self.assertTrue(p2.unauthenticated_userid.called)

    def test_merge_principals(self):
        """ merge all principals from all auth policies """
        p1, p2 = MagicMock(), MagicMock()
        principals = ['foo', 'bar']
        p1.effective_principals.return_value = principals[:1]
        p2.effective_principals.return_value = principals[1:]
        policy = MixedAuthenticationPolicy(p1, p2)
        policy_principals = policy.effective_principals(self.request)
        self.assertItemsEqual(policy_principals, principals)

    def test_merge_remember(self):
        """ merge all remember headers """
        p1, p2 = MagicMock(), MagicMock()
        headers = ['foo', 'bar']
        p1.remember.return_value = headers[:1]
        p2.remember.return_value = headers[1:]
        policy = MixedAuthenticationPolicy(p1, p2)
        remember = policy.remember(self.request, 'foo')
        self.assertItemsEqual(remember, headers)

    def test_merge_forget(self):
        """ merge all forget headers """
        p1, p2 = MagicMock(), MagicMock()
        headers = ['foo', 'bar']
        p1.forget.return_value = headers[:1]
        p2.forget.return_value = headers[1:]
        policy = MixedAuthenticationPolicy(p1, p2)
        forget = policy.forget(self.request)
        self.assertItemsEqual(forget, headers)
