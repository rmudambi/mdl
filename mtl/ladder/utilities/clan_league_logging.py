import os
import logging
from logging.handlers import RotatingFileHandler, NTEventLogHandler

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("oauth2client").setLevel(logging.WARNING)


def get_logger():
    logger = logging.getLogger(__name__)

    # create a file handler
    log_file_directory = "log"
    if not os.path.exists(log_file_directory):
        os.makedirs(log_file_directory)
    log_file_path = os.path.join(log_file_directory, "operations.log")

    # 10 log files each of 10MB in size
    file_handler = RotatingFileHandler(log_file_path, 'a', 10 * 1024 * 1024, 10)
    application_event_log__handler = NTEventLogHandler("ClanLeague")

    file_handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    application_event_log__handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(application_event_log__handler)

    return logger
