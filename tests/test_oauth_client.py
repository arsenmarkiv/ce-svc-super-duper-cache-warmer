import os
import sys
import requests_mock
import pytest

from src.cachemanager import oauth_client
from src.cachemanager.oauth_client import TokenRetrieveException

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'cachemanager'))


def test_retrieve_token(monkeypatch):

    with requests_mock.mock() as mock:
        mock.post('https://login.microsoftonline.com/tenant_id/oauth2/token', text='{"access_token": "qwerty123"}')
        mock.patch('dna_oauth.retrieve_token')

        assert oauth_client.retrieve_token('tenant_id', 'resource', 'client_id', 'client_secret') == "qwerty123"
        assert mock.call_count == 1


def test_retrieve_token_bad(monkeypatch):
    with requests_mock.mock() as mock:
        mock.post('https://login.microsoftonline.com/bad/oauth2/token', status_code=500, reason='Bad credentials')
        mock.patch('dna_oauth.retrieve_token')

        with pytest.raises(TokenRetrieveException):
            oauth_client.retrieve_token('bad', 'bad', 'client_id', 'client_secret')
