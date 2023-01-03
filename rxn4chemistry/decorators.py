"""Decorators for IBM RXN for Chemistry API."""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import threading
import time
from functools import partial, wraps
from typing import Any, Callable, Optional

import requests

from .callbacks import default_on_success
from .response_handler import ResponseHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

MAXIMUM_REQUESTS_PER_MINUTE = 1e5
MININUM_TIMEOUT_BETWEEN_REQUESTS = 1e-5  # expressed in seconds
LAST_REQUEST_TIME = int(time.time()) - 86400  # added a one day offset
REQUEST_COUNT = 0


class RequestsPerMinuteExceeded(RuntimeError):
    """Exception raised when too many requests are sent in a minute."""

    pass


class RequestTimeoutNotElapsed(RuntimeError):
    """Exception raised when the timeout between requests has not elapsed."""

    pass


def ibm_rxn_api_limits(function: Callable) -> Callable:
    """
    Decorator to handle the limits in the RXN API.

    Args:
        function (Callable): function to decorate.

    Raises:
        RequestsPerMinuteExceeded: too many requests in a minute.
        RequestTimeoutNotElapsed: consecutive requests too close in time.

    Returns:
        Callable: a function wrapped with the decorator.
    """

    def _too_many_requests():
        raise RequestsPerMinuteExceeded(
            "Too many requests per minute. Maximum supported: {}".format(
                MAXIMUM_REQUESTS_PER_MINUTE
            )
        )

    def _too_frequent_requests():
        raise RequestTimeoutNotElapsed(
            "Too frequent requests. Wait at least {}s ".format(
                MININUM_TIMEOUT_BETWEEN_REQUESTS
            )
            + "between consecutive requests to the API"
        )

    @wraps(function)
    def _wrapper(*args, **kwargs):
        global LAST_REQUEST_TIME
        global REQUEST_COUNT
        current_request_time = time.time()
        # test frequency
        if (
            current_request_time - LAST_REQUEST_TIME
        ) < MININUM_TIMEOUT_BETWEEN_REQUESTS:
            _too_frequent_requests()
        # optionally reset request count.
        if (
            current_request_time - LAST_REQUEST_TIME
        ) >= 60:  # more than on minute passed
            request_count_lock = threading.Lock()
            with request_count_lock:
                REQUEST_COUNT = 0
        if REQUEST_COUNT >= MAXIMUM_REQUESTS_PER_MINUTE:
            _too_many_requests()
        # perform the function call
        result = function(*args, **kwargs)
        # update last request time
        last_request_time_lock = threading.Lock()
        with last_request_time_lock:
            LAST_REQUEST_TIME = current_request_time
        # update count
        request_count_lock = threading.Lock()
        with request_count_lock:
            REQUEST_COUNT += 1
        return result

    return _wrapper


def response_handling(
    function: Optional[Callable] = None,
    success_status_code: int = 200,
    on_success: Callable[[requests.models.Response], Any] = default_on_success,
) -> Callable:
    """
    Decorator to handle request responses.

    Args:
        function (Callable, optional): function to decorate.
        success_status_code (int): status expected on success.
        on_success (Callable): function to call on success.

    Returns:
        Callable: a function wrapped with the decorator.
    """
    if function is None:
        return partial(
            response_handling,
            success_status_code=success_status_code,
            on_success=on_success,
        )

    @wraps(function)
    def _wrapper(*args, **kwargs):

        logger.debug(
            f"request {function.__name__} with args={args} and kwargs={kwargs}"
        )
        response = function(*args, **kwargs)
        logger.debug(f"response {response.text}")

        response_handler = ResponseHandler(
            response=response,
            success_status_code=success_status_code,
            on_success=on_success,
        )
        return response_handler.handle()

    return _wrapper
