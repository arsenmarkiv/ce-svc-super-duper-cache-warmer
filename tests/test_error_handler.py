import os
import sys

from flask import current_app

from src.cachemanager.main import app
from src.cachemanager.error_handler import AppException, app_error_handler, generic_error_handler, \
    page_not_found_error_handler
from src.cachemanager.constants import StatusCode, Error, ErrorMessage

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'cachemanager'))


def test_app_error_handler():
    with app.app_context():
        with current_app.test_request_context():
            actual = app_error_handler(AppException(StatusCode.BAD_REQUEST, Error.BAD_REQUEST,
                                                    ErrorMessage.BAD_REQUEST))
            actual_json = actual.get_json()
            assert actual_json["error"] == Error.BAD_REQUEST
            assert actual_json["message"] == ErrorMessage.BAD_REQUEST
            assert actual_json["status"] == StatusCode.BAD_REQUEST


def test_generic_error_handler():
    with app.app_context():
        with current_app.test_request_context():
            actual = generic_error_handler(Exception)
            actual_json = actual.get_json()
            assert actual_json["error"] == Error.INTERNAL_SERVER_ERROR
            assert actual_json["message"] == ErrorMessage.INTERNAL_SERVER_ERROR
            assert actual_json["status"] == StatusCode.INTERNAL_SERVER_ERROR


def test_page_not_found_error_handler():
    with app.app_context():
        with current_app.test_request_context():
            actual = page_not_found_error_handler(Exception)
            actual_json = actual.get_json()
            assert actual_json["error"] == Error.NOT_FOUND
            assert actual_json["message"] == ErrorMessage.NOT_FOUND
            assert actual_json["status"] == StatusCode.NOT_FOUND
