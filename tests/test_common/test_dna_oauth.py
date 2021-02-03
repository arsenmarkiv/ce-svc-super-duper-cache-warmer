import os
import sys

import requests
from src.cachemanager.common import dna_oauth

sys.path.append(os.path.join(os.path.dirname(__file__), '...', 'src', 'cachemanager', 'common'))

def foo(access_token):
    return access_token


def stale_token_2nd_time(access_token):
    if hasattr(stale_token_2nd_time, 'count'):
        stale_token_2nd_time.count += 1
    else:
        stale_token_2nd_time.count = 1

    if stale_token_2nd_time.count == 2:
        raise requests.exceptions.SSLError()

    return access_token


def test_add_access_token_kwarg_get_token(monkeypatch, requests_mock):
    monkeypatch.setattr('src.cachemanager.common.dna_oauth.access_token', lambda *args: 'access_token_1')
    decorator = dna_oauth.add_access_token_kwarg(tenant_id='tenant_id', resource='resource', client_id='client_id',
                                                 client_secret='client_secret')
    decorated = decorator(foo)
    assert "access_token_1" == decorated()


def test_add_access_token_kwarg_cache_token(monkeypatch, requests_mock):
    monkeypatch.setattr('src.cachemanager.common.dna_oauth.access_token', lambda *args: 'access_token_1')
    decorator = dna_oauth.add_access_token_kwarg(tenant_id='tenant_id', resource='resource', client_id='client_id',
                                                 client_secret='client_secret')
    decorated = decorator(foo)
    assert "access_token_1" == decorated()
    monkeypatch.setattr('src.cachemanager.common.dna_oauth.access_token', lambda *args: 'access_token_2')
    assert "access_token_1" == decorated()


def test_add_access_token_kwarg_stale_token(monkeypatch, requests_mock):
    monkeypatch.setattr('src.cachemanager.common.dna_oauth.access_token', lambda *args: 'access_token_1')
    decorator = dna_oauth.add_access_token_kwarg(tenant_id='tenant_id', resource='resource', client_id='client_id',
                                                 client_secret='client_secret')
    decorated = decorator(stale_token_2nd_time)
    assert "access_token_1" == decorated()

    monkeypatch.setattr('src.cachemanager.common.dna_oauth.access_token', lambda *args: 'access_token_2')
    assert "access_token_2" == decorated()
