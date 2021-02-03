import asyncio
import os
import sys
import unittest
import pytest
import requests_mock

from src.cachemanager.common import exceptions
from src.cachemanager.common.exceptions import NotValidPeriodType, NoSuchDirectoryException
from src.cachemanager.services import cache_service
from src.cachemanager.services.cache_service import requests_with_asyncio_and_aiohttp, gather_with_concurrency, \
    call_summary_api, data_generator, parse_resources, execute_requests


sys.path.append(os.path.join(os.path.dirname(__file__), '...', 'src', 'cachemanager'))


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


def test_requests_with_asyncio_and_aiohttp(monkeypatch):
    monkeypatch.setenv('ANALYTICS_API_BASE_URL', 'analytics_url')
    monkeypatch.setattr('src.cachemanager.common.dna_oauth.access_token', lambda *args: 'TOKEN')

    with requests_mock.mock() as mock:
        mock.post('http://dist_analytics/v1/endpoint', text='"REQUEST_BODY')
        mock.patch('cache_service.requests_with_asyncio_and_aiohttp')
        assert cache_service.requests_with_asyncio_and_aiohttp('endpoint') == "REQUEST_BODY"
        assert mock.call_count == 1

        mock.post('http://dist_analytics/v1/endpoint', text='"REQUEST_BODY', status_code=500)
        mock.patch('cache_service.requests_with_asyncio_and_aiohttp')
        with pytest.raises(exceptions.ApiResultsException):
            cache_service.requests_with_asyncio_and_aiohttp('url')


class AsyncMock:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *error_info):
        return self

    async def json(self):
        return json_response


@pytest.mark.asyncio
async def test_requests_with_asyncio_and_aiohttp(monkeypatch):
    monkeypatch.setattr('src.cachemanager.common.dna_oauth.access_token', lambda *args: 'TOKEN')

    def mock_request(self, *args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status = 200
        # mock_response.json = json_response
        return mock_response

    monkeypatch.setattr('src.cachemanager.services.cache_service.aiohttp.ClientSession.request', mock_request)
    result = await requests_with_asyncio_and_aiohttp('summary', 'POST', json_data)

    assert result == '43f13350-a4df-4428-92fc-68ae75a2949c'


@pytest.mark.asyncio
async def test_gather_with_concurrency(event_loop):
    n = 5
    tasks = [event_loop.create_task(asyncio.sleep(1, result=x))
             for x in range(10)]
    results = await gather_with_concurrency(n, *tasks)

    assert results == list(range(10))


async def mock_async_function(*args, **kwargs):
    return json_data


@pytest.mark.asyncio
async def test_call_summary_api(monkeypatch):
    calls = []
    monkeypatch.setattr("src.cachemanager.services.cache_service.requests_with_asyncio_and_aiohttp",
                        lambda *args, **kwargs: calls.append(json_data))

    with pytest.raises(NotValidPeriodType):
        await call_summary_api('non-clear', 4)

    with unittest.mock.patch('src.cachemanager.services.cache_service.gather_with_concurrency',
                             wraps=mock_async_function):
        monthly_result = await call_summary_api('monthly', 4)

    assert monthly_result['turnaroundId'] == "43f13350-a4df-4428-92fc-68ae75a2949c"


def test_data_generator():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources')
    good_path = os.path.join(path, 'monthly')
    bad_path = os.path.join(path, 'daily')
    try:
        success = next(data_generator(good_path)) is not None
    except StopIteration as e:
        success = False

    assert success is True

    try:
        success = next(data_generator(bad_path)) is not None
    except StopIteration as e:
        success = False

    assert success is False


async def test_parse_resources():
    good_period = "quarterly"
    bad_period = "light-year"

    good_result = await parse_resources(good_period)

    assert good_result is not None

    with pytest.raises(NoSuchDirectoryException):
        await parse_resources(bad_period)


def test_execute_requests(monkeypatch):
    with unittest.mock.patch('src.cachemanager.services.cache_service.call_summary_api',
                             wraps=mock_async_function):
        response = execute_requests('trailing-months', 10)

        assert response['turnaroundId'] == "43f13350-a4df-4428-92fc-68ae75a2949c"
