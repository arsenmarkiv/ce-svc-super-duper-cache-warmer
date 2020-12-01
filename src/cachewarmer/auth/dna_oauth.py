import functools
import requests
from dnapythonutils.auth.azure_auth import access_token
from src.cachewarmer.exceptions import APIResultException


def add_access_token_kwarg(tenant_id, resource, client_id, client_secret):

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
