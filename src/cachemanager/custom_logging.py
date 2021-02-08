import logging
import os
import sys


def traceback_handler(exctype, value, trace):
    """
    Logging of exeptions
    """
    logging.exception(f"{exctype}: {value}", exc_info=(
        exctype, value, trace
    ))


def init_logging():
    """
    Initialize generic customized logging
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_level = logging._checkLevel(os.environ.get('LOG_LEVEL', 'INFO'))

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []
    root_logger.addHandler(handler)

    # Add traceback handler
    sys.excepthook = traceback_handler
