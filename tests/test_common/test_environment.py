import os
import sys

from src.cachemanager.common import environment

sys.path.append(os.path.join(os.path.dirname(__file__), '...', 'src', 'cachemanager'))


def test_set_vars(monkeypatch):

    monkeypatch.setenv('FLASK_HOST', 'HOST')
    monkeypatch.setenv('FLASK_ENV', 'ENV')
    monkeypatch.setenv('FLASK_PORT', 'PORT')
    monkeypatch.setenv('FLASK_DEBUG', 'DEBUG_MODE')
    monkeypatch.setenv('URL_PREFIX', 'URL')

    # Get the environment variables
    env = environment.Variables('load')

    assert env.host == 'HOST'
    assert env.port == 'PORT'
    assert env.environment == 'ENV'
    assert env.debug_mode == 'DEBUG_MODE'
    assert env.url_prefix == 'URL'

    monkeypatch.delenv('FLASK_HOST')
    monkeypatch.delenv('FLASK_ENV')
    monkeypatch.delenv('FLASK_PORT')
    monkeypatch.delenv('FLASK_DEBUG')
    monkeypatch.delenv('URL_PREFIX')
