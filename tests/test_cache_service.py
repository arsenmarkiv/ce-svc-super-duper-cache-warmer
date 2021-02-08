import asyncio
import os
import sys
import unittest

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'cachemanager'))

from src.cachemanager import cache_service
from src.cachemanager.cache_service import NotValidPeriodType, NoSuchDirectoryException

json_data = {
    "turnaroundId": "43f13350-a4df-4428-92fc-68ae75a2949c",
    "groupBy": {
        "geography": [
            "country"
        ],
        "product": [
            "assetClass"
        ]
    },
    "filterBy": {
        "geography": {
            "country": [
                "US"
            ]
        }
    },
    "dateRange": {
        "end": "20190930",
        "periodType": "monthly"
    },
    "attributes": [
        {
            "return": [
                "changeNetFlowRatio"
            ]
        },
        {
            "function": [
                "change"
            ],
            "against": [
                "netFlowRatio"
            ]
        }
    ]
}

json_response = {
    "request":
        json_data
}


class AsyncMock:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *error_info):
        return self

    async def json(self):
        return json_response


def test_get_url_for_service(monkeypatch):
    monkeypatch.setenv('SERVICE_TO_SERVICE_PROTOCOL', 'http')
    monkeypatch.setenv('SERVICE_TO_SERVICE_REGION', 'dev.az')
    monkeypatch.setenv('SERVICE_TO_SERVICE_PORT', '12345')

    url = cache_service.get_url_for_service('dist-analytics')

    assert url == 'http://dist-analytics.dev.az:12345/dist-analytics/'


def test_get_analytics_api_url(monkeypatch):
    monkeypatch.setenv('ANALYTICS_API_BASE_URL', "some_url")

    url = cache_service.get_analytics_api_url('1', 'some_endpoint')

    assert url == 'some_url/v1/some_endpoint'


@pytest.mark.asyncio
async def test_requests_with_asyncio_and_aiohttp_2(monkeypatch):
    def mock_token_response(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = 'qwerty123'
        return 'qwerty123'

    def mock_request(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status = 200
        return mock_response

    monkeypatch.setenv('AZURE_AD_TENANT_ID', "TENANT_ID")
    monkeypatch.setenv('APP_REGISTAR_CLIENT_ID', "CLIENT_ID")
    monkeypatch.setenv('OAUTH_CLIENT_ID', 'OAUTH_CLIENT')
    monkeypatch.setenv('OAUTH_CLIENT_SECRET', 'CLIIENT_SECRET')

    monkeypatch.setattr('src.cachemanager.cache_service.oauth_client.retrieve_token', mock_token_response)
    monkeypatch.setattr('src.cachemanager.cache_service.aiohttp.ClientSession.request', mock_request)
    result = await cache_service.requests_with_asyncio_and_aiohttp('summary', 'POST', json_data)

    assert result == '43f13350-a4df-4428-92fc-68ae75a2949c'


@pytest.mark.asyncio
async def test_gather_with_concurrency(event_loop):
    n = 5
    tasks = [event_loop.create_task(asyncio.sleep(1, result=x))
             for x in range(10)]
    results = await cache_service.gather_with_concurrency(n, *tasks)

    assert results == list(range(10))


async def mock_async_function(*args, **kwargs):
    return json_data


@pytest.mark.asyncio
async def test_call_summary_api(monkeypatch):
    calls = []
    monkeypatch.setattr("src.cachemanager.cache_service.requests_with_asyncio_and_aiohttp",
                        lambda *args, **kwargs: calls.append(json_data))

    with pytest.raises(NotValidPeriodType):
        await cache_service.call_summary_api('non-clear', 4)

    with unittest.mock.patch('src.cachemanager.cache_service.gather_with_concurrency',
                             wraps=mock_async_function):
        monthly_result = await cache_service.call_summary_api('monthly', 4)

    assert monthly_result['turnaroundId'] == "43f13350-a4df-4428-92fc-68ae75a2949c"


def test_data_generator():
    path = os.path.join(os.path.dirname(__file__), 'resources')
    good_path = os.path.join(path, 'monthly')
    bad_path = os.path.join(path, 'daily')
    try:
        success = next(cache_service.data_generator(good_path)) is not None
    except StopIteration:
        success = False

    assert success is True

    try:
        success = next(cache_service.data_generator(bad_path)) is not None
    except StopIteration:
        success = False

    assert success is False


async def test_parse_resources():
    good_period = "quarterly"
    bad_period = "light-year"

    good_result = await cache_service.parse_resources(good_period)

    assert good_result is not None

    with pytest.raises(NoSuchDirectoryException):
        await cache_service.parse_resources(bad_period)


def test_execute_requests(monkeypatch):
    with unittest.mock.patch('src.cachemanager.cache_service.call_summary_api',
                             wraps=mock_async_function):
        response = cache_service.execute_requests('trailing-months', 10)

        assert response['turnaroundId'] == "43f13350-a4df-4428-92fc-68ae75a2949c"
