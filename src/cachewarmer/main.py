import logging

from flask import Flask, jsonify, request
from dnapythonutils import logs

# This configures logging to use the correct format for ALA
from .common.exceptions import MissingParameterException
from .services import cache_service

logs.init_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)


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
