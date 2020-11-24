import logging

from dnapythonutils import logs
from flask import Flask, jsonify

# This configures logging to use the correct format for ALA
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


def main():
    """
    App must contain a function that returns the WSGI app
    object. This function is referenced in `gradle.properties`
    as 'mainFunction`. This function is required for gunicorn.
    """
    return app
