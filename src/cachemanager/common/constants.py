STATUS = 'status'
TIMESTAMP = 'timestamp'
ERROR = 'error'
MESSAGE = 'message'
PATH = 'path'


class StatusCode:
    INTERNAL_SERVER_ERROR = 500
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    BAD_REQUEST = 400


class Error:
    INTERNAL_SERVER_ERROR = 'Internal server error'
    UNAUTHORIZED = 'Unauthorized'
    NOT_FOUND = 'Not found'
    BAD_REQUEST = 'Bad Request'


class ErrorMessage:
    INTERNAL_SERVER_ERROR = 'Internal server error occurred'
    UNAUTHORIZED = 'UNAUTHORIZED'
    NOT_FOUND = '404 page not found'
    BAD_REQUEST = 'Invalid request json'
