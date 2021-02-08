import logging
import requests

from exceptions import TokenRetrieveException

logger = logging.getLogger(__name__)


def retrieve_token(tenant_id, resource, client_id, client_secret):
    microsoft_token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'

    data = {'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': resource}

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url=microsoft_token_url, data=data, headers=headers)
    if response.status_code != 200:
        message = f'Non-200 status code ({response.status_code}) while making api request {microsoft_token_url}: ' \
                  f'{response.reason}'
        logger.error(message)
        raise TokenRetrieveException(message)
    else:
        logger.info('token retrieved successfully')
    return response.json()['access_token']
