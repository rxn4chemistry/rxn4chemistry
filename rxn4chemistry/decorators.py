"""Decorators for IBM RXN for Chemistry API."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)
import time
import logging
import threading
from typing import Callable
from functools import wraps, partial

from .callbacks import default_on_success

LOGGER = logging.getLogger('rxn4chemistry:decorators')
MAXIMUM_REQUESTS_PER_MINUTE = 5
MININUM_TIMEOUT_BETWEEN_REQUESTS = 2  # expressed in seconds
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
            'Too many requests per minute. Maximum supported: {}'.
            format(MAXIMUM_REQUESTS_PER_MINUTE)
        )

    def _too_frequent_requests():
        raise RequestTimeoutNotElapsed(
            'Too frequent requests. Wait at least {}s '.
            format(MININUM_TIMEOUT_BETWEEN_REQUESTS) +
            'between consecutive requests to the API'
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
    function: Callable = None,
    success_status_code: int = 200,
    on_success: Callable = default_on_success
) -> Callable:
    """
    Decorator to handle request responses. 

    Args:
        function (Callable): function to decorate.
        success_status_code (int): status expected on success.
        on_success (Callable): function to call on success.

    Returns:
        Callable: a function wrapped with the decorator.
    """
    if function is None:
        return partial(
            response_handling,
            success_status_code=success_status_code,
            on_success=on_success
        )

    @wraps(function)
    def _wrapper(*args, **kwargs):

        response = function(*args, **kwargs)

        if response.status_code == success_status_code:
            return on_success(response)
        elif response.status_code == 401:
            LOGGER.error(
                'There is probably something wrong with your api key. '
                'Please check.'
            )
            LOGGER.debug(response.text)
        else:
            LOGGER.error('Unexpected error.')
            LOGGER.error(response.text)
        response_dict = response.json()
        return {'response': response_dict}

    return _wrapper
