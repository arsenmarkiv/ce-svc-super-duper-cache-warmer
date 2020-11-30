import functools
import requests
from dnapythonutils.auth.azure_auth import access_token
from src.cachewarmer.exceptions import APIResultException


def add_access_token_kwarg(tenant_id, resource, client_id, client_secret):
    """decorator to handle oauth access token for requests http calls, including cache and refreshing.
    it adds an `access_token` keyword parameter to pass in the access token.

    Assumptions:
    1. the decorated method has keyword arguments either as the specific "access_token" or generic "**kwargs".
    2. the requests calls in the decorated method set verify to False,
       so that requests.exceptions.SSLError is raised when the access token is expired.

    Args:
        tenant_id (string): tenant id for the oauth provider
        resource (string): resource id that requires this token
        client_id (string):
        client_secret (string):

    Example:

    @dna_oauth.add_access_token_kwarg(url=url, resource=resource, client_id=client_id, client_secret=client_secret)
    def method_that_issues_requests(name, **kwargs):
        print(f"Hello {name} {kwargs['access_token']}")

    Caveats:
    because the cached access token is a shared state, there could be a race condition where multiple threads sets
    the access token value at the same time. We could potentially add a lock to it.
    """

    def decorator_access_token(func):
        @functools.wraps(func)
        def wrapper_access_token(*args, **kwargs):
            if not hasattr(wrapper_access_token, 'token'):
                wrapper_access_token.token = access_token(tenant_id, resource, client_id, client_secret)

            try:
                kwargs['access_token'] = wrapper_access_token.token
                return func(*args, **kwargs)
            except (requests.exceptions.SSLError, APIResultException):
                wrapper_access_token.token = access_token(tenant_id, resource, client_id, client_secret)
                kwargs['access_token'] = wrapper_access_token.token
                return func(*args, **kwargs)
        return wrapper_access_token
    return decorator_access_token
