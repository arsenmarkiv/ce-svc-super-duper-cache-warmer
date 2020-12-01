import asyncio
import glob
import os
import sys

import aiohttp
from aiohttp import ClientTimeout
from flask import json

from src.cachewarmer import exceptions
from src.cachewarmer.auth import dna_oauth
from src.cachewarmer.period_type import PeriodType


def get_url_for_service(service: str) -> str:
    return '{protocol}://{app_name}.{name}:{port}/{app_name}/'.format(
        protocol=os.environ.get('SERVICE_TO_SERVICE_PROTOCOL'),
        name=os.environ.get('SERVICE_TO_SERVICE_REGION'),
        port=os.environ.get('SERVICE_TO_SERVICE_PORT'),
        app_name=service
    )


def get_analytics_api_url(api_version, endpoint) -> str:
    base_url = os.environ.get('ANALYTICS_API_BASE_URL', get_url_for_service('svc-distanalytics'))

    full_url = f"{base_url}/v{api_version}/{endpoint}"

    return full_url


# def run_with_executor(url, method="GET", data=None, threads=5, verify_ssl=False, api_version='33', access_token=None):
#     access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCIsImtpZCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCJ9.eyJhdWQiOiJlNWZmMzkyYy1iYjM5LTRjZGItOWM1MC0xODNmOGJhMTVjMWYiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81N2Y3NDA4YS1iMGZmLTQ5MWEtYTc1Ni0zNTdhYjAxN2VmMzMvIiwiaWF0IjoxNjA2NDg1MzMwLCJuYmYiOjE2MDY0ODUzMzAsImV4cCI6MTYwNjQ4OTIzMCwiYWlvIjoiRTJSZ1lJaFdTTjFXbWp6blJ2bzIxMzJQcHh6ZEF3QT0iLCJhcHBpZCI6IjVlNjMxZDU0LTgzYWEtNGU0OC1hMDU4LWE4YTQyMGI5MDNiYSIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzU3Zjc0MDhhLWIwZmYtNDkxYS1hNzU2LTM1N2FiMDE3ZWYzMy8iLCJvaWQiOiIwNjY1ODVhNS1hYmJjLTRhYjgtODFmYy04ZTQ1MGE2Mjk5YjQiLCJyaCI6IjAuQVRnQWlrRDNWXy13R2ttblZqVjZzQmZ2TTFRZFkxNnFnMGhPb0Zpb3BDQzVBN280QUFBLiIsInN1YiI6IjA2NjU4NWE1LWFiYmMtNGFiOC04MWZjLThlNDUwYTYyOTliNCIsInRpZCI6IjU3Zjc0MDhhLWIwZmYtNDkxYS1hNzU2LTM1N2FiMDE3ZWYzMyIsInV0aSI6IlUwcnlQRkNsYTBlTlZ6eE5QaHNxQVEiLCJ2ZXIiOiIxLjAifQ.dmBl6_0W6rs9OlBqxpEv0SURKrgE_EZolXxS6kYD31ohGf1zevhTmeTZDo8ytZNcns4lNAcNM8TIRa5Ca8HecxY8TX_PnD-Ys4LHpd3AEPwqBbjLdc-iQbhdeoi1VXpAifFAAL8_EMrbYPKv4Ozb-68b0TIEf6q-6nDSqn7SiFDPMb2tkZyyyEV6pu61YQtxooD52nuByEkNtboi1vUnmJNO5OmwqINvZW-VzhYyjVmC90kMzSE3E5D6x--FNlLD4vdo7HcGiXxI7IgbCgTcVIL8aF7c87OfO2GuJhPf0ANuRPt4Jzth6ln1u85fgZ8gHmMBVY2oUW1C1rv4GaM9Gw'
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'Bearer ' + access_token
#     }
#     dist_analytics_url = get_analytics_api_url()
#     full_url = f"{dist_analytics_url}/v{api_version}/{url}"
#
#     with ThreadPoolExecutor(max_workers=threads) as executor:
#         fn = request(method, full_url, data=json.dumps(data), headers=headers)
#         q = Queue()
#         q.put()
#         executor.map(fn, full_url, timeout=30)

@dna_oauth.add_access_token_kwarg(tenant_id=os.getenv('AZURE_AD_TENANT_ID'),
                                  resource=os.getenv('APP_REGISTRAR_CLIENT_ID'),
                                  client_id=os.getenv('OAUTH_CLIENT_ID'),
                                  client_secret=os.getenv('OAUTH_CLIENT_SECRET'))
async def requests_with_asyncio_and_aiohttp(url, method="GET", data=None, verify_ssl=False, api_version='33',
                                            access_token=None):
    if access_token is None:
        access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCIsImtpZCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCJ9.eyJhdWQiOiJlNWZmMzkyYy1iYjM5LTRjZGItOWM1MC0xODNmOGJhMTVjMWYiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81N2Y3NDA4YS1iMGZmLTQ5MWEtYTc1Ni0zNTdhYjAxN2VmMzMvIiwiaWF0IjoxNjA2NzMzNDgyLCJuYmYiOjE2MDY3MzM0ODIsImV4cCI6MTYwNjczNzM4MiwiYWlvIjoiRTJSZ1lIQXMzOTl5V3VSQnMvNWZ4UVA1K1dlWkFRPT0iLCJhcHBpZCI6IjVlNjMxZDU0LTgzYWEtNGU0OC1hMDU4LWE4YTQyMGI5MDNiYSIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzU3Zjc0MDhhLWIwZmYtNDkxYS1hNzU2LTM1N2FiMDE3ZWYzMy8iLCJvaWQiOiIwNjY1ODVhNS1hYmJjLTRhYjgtODFmYy04ZTQ1MGE2Mjk5YjQiLCJyaCI6IjAuQVRnQWlrRDNWXy13R2ttblZqVjZzQmZ2TTFRZFkxNnFnMGhPb0Zpb3BDQzVBN280QUFBLiIsInN1YiI6IjA2NjU4NWE1LWFiYmMtNGFiOC04MWZjLThlNDUwYTYyOTliNCIsInRpZCI6IjU3Zjc0MDhhLWIwZmYtNDkxYS1hNzU2LTM1N2FiMDE3ZWYzMyIsInV0aSI6ImNZQlhCbzljS1VtcE9hM2dxMUtqQVEiLCJ2ZXIiOiIxLjAifQ.NsPa8q3-b8OefUwd1u7la7LW4dYbImwz3EJsCsK8IBosZQx14KOuhyuex3i6iMpTx8sGArDMmgr7Fin9uVMrnAX2DV9yYr6wSvk2E6e2wayQ9bQZFtvDL039x0U3Evgm-UJ_WqbK3msV54rQ3ZzOwVA_HQglY54UQcC7keOXJROqT81opjBiPjnKAOtAPJlMbHassSgEpE4pBXYQI8FRN6wPtGsFUT2SHnuNRX27sShyegbFRp0SsD-Y8Zt0WnZxWDtfN_hrIOiMeyKnybS7JFTeMy2nDSWkxWMQMDOc8Ii0Dm14S7lW6DQWS25NP_bxImkm69k9OPxxOnNuXohqUA'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    dist_analytics_url = get_analytics_api_url(url, api_version)

    connector = aiohttp.TCPConnector(limit=5, limit_per_host=5)
    timeout = ClientTimeout(total=40 * 60)

    client = aiohttp.ClientSession(connector=connector, timeout=timeout)

    async with client as session:
        async with session.request(method, dist_analytics_url, data=json.dumps(data), headers=headers) as response:

            if response.status == 204:
                return {'data': []}
            if response.status != 200:
                message = f'Non-200 status code ({response.status}) while making api request {dist_analytics_url}: {response.reason}'
                raise exceptions.APIResultException(message, response.status)

            try:
                return response.json()
            except ValueError:
                raise exceptions.APIResultException(f'Failed to decode dist-analytics result: {response.text}')


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def call_summary_api(period: str, threads: int):
    period_types = set(item.value for item in PeriodType)

    if period not in period_types:
        raise exceptions.NotValidPeriodType(period)

    json_data = await parse_resources(period)

    coroutines = [
        requests_with_asyncio_and_aiohttp('summary', 'POST', single_json, False)
        for single_json
        in json_data
    ]

    results = await gather_with_concurrency(int(threads), *coroutines)

    print(results)

    return results


def data_generator(path):
    pattern = os.path.join(path, '*.json')

    for filename in glob.glob(pattern):
        with open(filename, 'r') as infile:
            data = infile.read()
            yield json.loads(data)


# TODO: add GitHub files parsing functionality
async def parse_resources(folder_name):
    project_path = os.path.abspath(os.path.split(sys.argv[0])[0])
    path = os.path.join(project_path, 'resources', folder_name)

    # TODO: check if file exist
    requests_arr = [json_file for json_file in data_generator(path)]

    return requests_arr


def execute_requests(period_type, threads_count):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(call_summary_api(period_type, threads_count))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
