import logging
from functools import wraps
from datetime import datetime
from bottle import request, response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler('') heroku does not allow logging into file
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


def log_to_logger(fn):
    """
    Wrap a Bottle request so that a log line is emitted after it's handled.
    (This decorator can be extended to take the desired logger as a param.)
    """

    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        request_time = datetime.now()
        actual_response = fn(*args, **kwargs)
        # modify this to log exactly what you need:
        logger.info(
            "%s %s %s %s %s %s"
            % (request.remote_addr, request_time, request.method, request.url, response.status, str(response.body))
        )
        return actual_response

    return _log_to_logger
