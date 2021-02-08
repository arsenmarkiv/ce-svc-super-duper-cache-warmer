import logging
import os
import sys

from flask import Flask, jsonify, request

sys.path.append(os.path.dirname(__file__))

from exceptions import CacheServiceException, MissingParameterException
from environment import Variables
from error_handler import AppException, app_error_handler, generic_error_handler, \
    page_not_found_error_handler, cache_manager_error_handler
import cache_service
from custom_logging import init_logging

init_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

env_variables = Variables('load')

app.register_error_handler(AppException, app_error_handler)
app.register_error_handler(Exception, generic_error_handler)
app.register_error_handler(404, page_not_found_error_handler)
app.register_error_handler(CacheServiceException, cache_manager_error_handler)


async def main():
    return app


if __name__ == '__main__':
    app.run(
        host=env_variables.host,
        port=env_variables.port,
        debug=env_variables.debug_mode
    )


@app.route('/health')
def health_check():
    return jsonify({'status': 'UP'})


@app.route('/cache', methods=['GET'])
def warm_cache():
    period_type = request.args.get('periodType')
    threads_count = request.args.get('threadsCount', None)

    if period_type is None:
        raise MissingParameterException()

    logger.info(f'Cache warming for period type {period_type} requested')

    res = cache_service.execute_requests(period_type, threads_count)

    return jsonify(res)
