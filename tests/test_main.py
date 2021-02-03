import os
import sys

import pytest

from src.cachemanager import app

sys.path.append(os.path.join(os.path.dirname(__file__), '...', 'src', 'cachemanager'))



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get('/health')
    assert {'status': 'UP'} == response.json


def mock_execute_requests_function(period_type, threads_count):
    return ["12345", "67890"]


def test_cache_route(client, monkeypatch):

    monkeypatch.setattr('src.cachemanager.services.cache_service.execute_requests', mock_execute_requests_function)

    response = client.get('/cache?periodType=monthly')

    assert response.status_code == 200
    assert response.data == b'["12345","67890"]\n'

    with app.test_client() as client:
        response = client.get('/cache?periodType=monthly&threadsCount=3')

    assert response.status_code == 200
    assert response.data == b'["12345","67890"]\n'

    with app.test_client() as client:
        response = client.get('/cache')

    assert response.status_code == 400
    assert response.data.find(b"MissingParameterException") > 0
