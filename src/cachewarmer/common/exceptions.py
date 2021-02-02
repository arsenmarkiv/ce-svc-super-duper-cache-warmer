import logging

from dnapythonutils import logs

logs.init_logging()
logger = logging.getLogger(__name__)


class CacheServiceException(Exception):

    def __init__(self, error, message, status_code=None):
        self.status_code = status_code
        self.message = message
        self.error = error

        super().__init__(self.error, self.message, self.status_code)


class ApiResultsException(Exception):

    def __init__(self, message, status_code=None):
        self.status_code = status_code
        self.error = 'ApiResultsException'
        self.message = message

        super().__init__(message)


class NotValidPeriodType(CacheServiceException):

    def __init__(self, period_type, period_types):
        self.status = 400
        self.error = 'NotValidPeriodType'
        self.message = f'Not valid period type option: {period_type}. Use one of {period_types}'

        logger.info(self.message)

        super().__init__(self.error, self.message, self.status)


class NoSuchDirectoryException(CacheServiceException):

    def __init__(self, directory):
        self.status = 500
        self.error = 'NoSuchDirectoryException'
        self.message = f'There is no such directory: {directory}'

        logger.info(self.message)

        super().__init__(self.error, self.message, self.status)


class TokenRetrieveException(CacheServiceException):

    def __init__(self):
        self.status = 500
        self.error = 'TokenRetrieveException'
        self.message = 'There was token retrieve issue'

        logger.info(self.message)

        super().__init__(self.error, self.message, self.status)


class MissingParameterException(CacheServiceException):

    def __init__(self):
        self.status = 400
        self.error = "MissingParameterException"
        self.message = "Period type parameter required"

        logger.info(self.message)

        super().__init__(self.error, self.message, self.status)
