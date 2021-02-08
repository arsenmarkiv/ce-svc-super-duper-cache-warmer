import logging
import datetime

from flask import jsonify, make_response, request

import constants
from constants import StatusCode, Error, ErrorMessage
from exceptions import CacheServiceException

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, status=400, error=None, message=None):
        super(AppException, self).__init__()
        self.status = status
        self.error = error
        self.message = message


def app_error_handler(e):
    """
    handles Appexception
    Params:
        e (AppException): propogated appexception
    Returns:
        response (dict):
            data (list): list of error codes
            status (str): Failure
        http status code
    """
    logger.error(f'caught an AppException {e}')
    response = response_builder(e.status, e.error, e.message)
    return response


def generic_error_handler(e):
    """
    handles Exception
    Params:
        e (Exception): propogated exception
    Returns:
        response (dict):
            data (list): list of error codes
            status (str): Failure
        http status code
    """
    logger.error(f'Caught an generic exception: {e}')
    response = response_builder(StatusCode.INTERNAL_SERVER_ERROR, Error.INTERNAL_SERVER_ERROR,
                                ErrorMessage.INTERNAL_SERVER_ERROR)
    return response


def cache_manager_error_handler(e: CacheServiceException):
    """
    handles CacheServiceException
    Params:
        e (CacheServiceException or its sub-classes)
    Returns:
        response (dict):
            data (list): list of error codes
            status (str): Failure
        http status code
    """
    logger.error(f'Caught a cache service exception: {e}')
    response = response_builder(e.status_code, e.error, e.message)
    return response


def page_not_found_error_handler(e):
    """
    handles page not found
    Params:
        e (Exception): propogated exception
    Returns:
        response (string)
        http status code
    """
    return response_builder(StatusCode.NOT_FOUND, Error.NOT_FOUND, ErrorMessage.NOT_FOUND)


def add_response_headers(response, origin=None):
    """
    Adds headers to response
    """
    origin = request.headers.get('Origin') if origin is None else origin
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    response.headers['Access-Control-Allow-Methods'] = (
        'POST, GET, OPTIONS, DELETE'
    )
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'


def response_builder(status, error, errormessage):
    response = make_response(jsonify({
        constants.TIMESTAMP: datetime.datetime.now(),
        constants.STATUS: status,
        constants.ERROR: error,
        constants.MESSAGE: errormessage,
        constants.PATH: request.path
    }), status)
    origin = request.headers.get('Origin')
    add_response_headers(response, origin)
    return response
