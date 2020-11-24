import pytest
import json
from flask import Flask, request

from src.dnahelloworld.app import app, main


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        
def test_health_check(client):
    response = client.get('/actuator/health')
    assert {'status': 'UP'} == response.json

def test_app(client):
    ret = client.get('/')
    assert ret.status_code == 200
    assert ret.data == b'Hello, World!'


def test_main_func():
    returned_app = main()
    assert isinstance(returned_app, Flask)
