import asyncio
import glob
import logging
import os
import aiohttp

from aiohttp import ClientTimeout
from dnapythonutils import logs
from flask import json

from src.cachemanager.common import dna_oauth
from src.cachemanager.common.exceptions import NoSuchDirectoryException, TokenRetrieveException, ApiResultsException, \
    NotValidPeriodType
from src.cachemanager.common.period_type import PeriodType

logs.init_logging()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

errorHandler = logging.FileHandler("error.log")
errorHandler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(errorHandler)

default_thread_count = os.getenv('DEFAULT_THREAD_COUNT', 5)


def get_url_for_service(service: str) -> str:
    return '{protocol}://{app_name}.{region}:{port}/{app_name}/'.format(
        protocol=os.environ.get('SERVICE_TO_SERVICE_PROTOCOL'),
        region=os.environ.get('SERVICE_TO_SERVICE_REGION'),
        port=os.environ.get('SERVICE_TO_SERVICE_PORT'),
        app_name=service
    )


def get_analytics_api_url(api_version, endpoint) -> str:
    base_url = os.environ.get('ANALYTICS_API_BASE_URL', get_url_for_service('svc-distanalytics'))

    full_url = f"{base_url}/v{api_version}/{endpoint}"

    return full_url


@dna_oauth.add_access_token_kwarg(tenant_id=os.getenv('AZURE_AD_TENANT_ID'),
                                  resource=os.getenv('APP_REGISTRAR_CLIENT_ID'),
                                  client_id=os.getenv('OAUTH_CLIENT_ID'),
                                  client_secret=os.getenv('OAUTH_CLIENT_SECRET'))
async def requests_with_asyncio_and_aiohttp(url, method="POST", data=None, api_version='33', access_token=None):
    if access_token is None:
        raise TokenRetrieveException()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    dist_analytics_url = get_analytics_api_url(api_version, url)

    connector = aiohttp.TCPConnector()
    timeout = ClientTimeout(total=60 * 60)

    client = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async with client as session:
        async with session.request(method, dist_analytics_url, data=json.dumps(data), headers=headers) as response:
            if response.status == 200:
                try:
                    response_json = await response.json()
                    cached_request = response_json['request']
                except ValueError:
                    raise ApiResultsException(f'Failed to decode dist-analytics result: {response.text}')

                logger.info(f'Successfully returned response for request:{cached_request}')

                # return cached_request
            else:
                message = f'Non-200 status code ({response.status}) while making api request {dist_analytics_url}: {response.json()}'
                logger.error(message)
                raise ApiResultsException(message, response.status)


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def call_summary_api(period: str, threads: int):
    period_types = set(item.value for item in PeriodType)

    if period not in period_types:
        raise NotValidPeriodType(period, period_types)

    json_data = await parse_resources(period)

    coroutines = [
        requests_with_asyncio_and_aiohttp('summary', 'POST', single_json)
        for single_json
        in json_data
    ]

    if threads is None:
        threads = default_thread_count

    results = await gather_with_concurrency(int(threads), *coroutines)

    logger.info(f'Successfully cached requests with IDs: {results}')

    return results


def data_generator(path):
    pattern = os.path.join(path, '*.json')

    for filename in glob.glob(pattern):
        with open(filename, 'r') as infile:
            data = infile.read()
            yield json.loads(data)


# TODO: add GitHub files parsing functionality
async def parse_resources(folder_name):
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(project_path, 'resources', folder_name)

    isdir = os.path.exists(path)
    if not isdir:
        raise NoSuchDirectoryException(path)

    requests_arr = [json_file for json_file in data_generator(path)]

    return requests_arr


def execute_requests(period_type, threads_count=10):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(call_summary_api(period_type, threads_count))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
