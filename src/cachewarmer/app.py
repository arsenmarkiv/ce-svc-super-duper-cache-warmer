import logging

from dnapythonutils import logs
from flask import Flask, jsonify, request
from src.cachewarmer.api import cache_warming

logs.init_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/actuator/health')
def health_check():
    return jsonify({'status': 'UP'})


@app.route('/')
def hello_world():
    """
    A simple test route for verifying flask is working.

    :return: string containing "Hello, World!"
    """
    logger.info("Hello world called!")
    return 'Hello, World!'


async def main():
    """
    App must contain a function that returns the WSGI app
    object. This function is referenced in `gradle.properties`
    as 'mainFunction`. This function is required for gunicorn.
    """
    return app


@app.route('/cache/warm', methods=['GET'])
def warm_cache():
    period_type = request.args.get('periodType')
    threads_count = request.args.get('threadsCount')

    res = cache_warming.execute_requests(period_type, threads_count)

    print(res)

    return 'ok'


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
