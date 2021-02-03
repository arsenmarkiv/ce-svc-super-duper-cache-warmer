import os
import sys
import inspect

from flask import Flask

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'cachemanager'))

from src.cachemanager import app

# sys.path needs to be updated before any of the tests are loaded.
currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


def test_create_app():
    returned_app = app()
    assert isinstance(returned_app, Flask)
