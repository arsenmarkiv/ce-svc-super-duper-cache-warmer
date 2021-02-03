import logging
import os
import sys

sys.path.append(os.path.dirname(__file__))

from common.exceptions import CacheServiceException
from main import app
from common.environment import Variables
from common.error_handler import AppException, app_error_handler, generic_error_handler, \
    page_not_found_error_handler, cache_manager_error_handler

# This configures logging to use the correct format for ALA
logger = logging.getLogger(__name__)

env_variables = Variables('load')

app.register_error_handler(AppException, app_error_handler)
app.register_error_handler(Exception, generic_error_handler)
app.register_error_handler(404, page_not_found_error_handler)
app.register_error_handler(CacheServiceException, cache_manager_error_handler)
logger.info('DA cache manager app initialized successfully')


async def main():
    """
    App must contain a function that returns the WSGI app
    object. This function is referenced in `gradle.properties`
    as 'mainFunction`. This function is required for gunicorn.
    """
    return app


if __name__ == '__main__':
    """
    Run the application
    """
    app.run(
        host=env_variables.host,
        port=env_variables.port,
        debug=env_variables.debug_mode
    )
