""" Utilities for auth """


class MixedAuthenticationPolicy(object):

    """
    Auth policy that is backed by multiple other auth policies

    Checks authentication against each contained policy in order. The first one
    to return a non-None userid is used. Principals are merged.

    """
    def __init__(self, *policies):
        self._policies = list(policies)

    def add_policy(self, policy):
        """ Add another authentication policy """
        self._policies.append(policy)

    def authenticated_userid(self, request):
        """ Return the authenticated userid or ``None`` if no
        authenticated userid can be found. This method of the policy
        should ensure that a record exists in whatever persistent store is
        used related to the user (the user should not have been deleted);
        if a record associated with the current id does not exist in a
        persistent store, it should return ``None``."""
        for policy in self._policies:
            userid = policy.authenticated_userid(request)
            if userid is not None:
                return userid

    def unauthenticated_userid(self, request):
        """ Return the *unauthenticated* userid.  This method performs the
        same duty as ``authenticated_userid`` but is permitted to return the
        userid based only on data present in the request; it needn't (and
        shouldn't) check any persistent store to ensure that the user record
        related to the request userid exists."""
        for policy in self._policies:
            userid = policy.unauthenticated_userid(request)
            if userid is not None:
                return userid

    def effective_principals(self, request):
        """ Return a sequence representing the effective principals
        including the userid and any groups belonged to by the current
        user, including 'system' groups such as
        ``pyramid.security.Everyone`` and
        ``pyramid.security.Authenticated``. """
        principals = set()
        for policy in self._policies:
            principals.update(policy.effective_principals(request))
        return list(principals)

    def remember(self, request, principal, **kw):
        """ Return a set of headers suitable for 'remembering' the
        principal named ``principal`` when set in a response.  An
        individual authentication policy and its consumers can decide
        on the composition and meaning of **kw. """
        headers = []
        for policy in self._policies:
            headers.extend(policy.remember(request, principal, **kw))
        return headers

    def forget(self, request):
        """ Return a set of headers suitable for 'forgetting' the
        current user on subsequent requests. """
        headers = []
        for policy in self._policies:
            headers.extend(policy.forget(request))
        return headers


def _add_authentication_policy(config, policy):
    """ Config directive that adds another auth policy to Steward """
    config.registry.authentication_policy.add_policy(policy)


def includeme(config):
    """ Configure the app """
    config.add_directive('add_authentication_policy',
                         _add_authentication_policy)

    config.registry.authentication_policy = MixedAuthenticationPolicy()
