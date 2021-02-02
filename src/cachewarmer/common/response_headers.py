from flask import request


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
