import logging
import requests

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

errorHandler = logging.FileHandler("error.log")
errorHandler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(errorHandler)


def retrieve_token(tenant_id, resource, client_id, client_secret):

    microsoft_token_url = 'https://login.microsoftonline.com/{0}/oauth2/token'.format(tenant_id)

    data = {'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': resource
            }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url=microsoft_token_url, data=data, headers=headers)

    if response.status_code != 200:
        message = f'Non-200 status code ({response.status_code}) while making api request {microsoft_token_url}: ' \
                  f'{response.reason}'
        logger.error(message, response.status_code)
    else:
        logger.info('token retrieved successfully')

    return response.json()['access_token']
