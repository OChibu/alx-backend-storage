#!/usr/bin/env python3
"""Expiring Web Cache Module"""

import redis
import requests
from typing import Callable
from functools import wraps

# Initialize a Redis client
redis = redis.Redis()


def wrap_requests(fn: Callable) -> Callable:
    """
    Decorator to cache web responses and track URL access counts

    :param fn: The function to be wrapped
    :return: Wrapped function with caching and access count tracking
    """
    @wraps(fn)
    def wrapper(url: str) -> str:
        """
        Wrapper for the decorator to cache web
        responses and track URL access counts

        :param url: The URL to retrieve the HTML content from
        :return: The HTML content of the URL
        """
        # Increment the access count for the URL
        redis.incr(f"count:{url}")

        # Check if the response is cached in Redis
        cached_response = redis.get(f"cached:{url}")
        if cached_response:
            return cached_response.decode('utf-8')

        # If not cached, call the original function and cache the response
        result = fn(url)
        redis.setex(f"cached:{url}", 10, result)
        return result

    return wrapper


@wrap_requests
def get_page(url: str) -> str:
    """
    Fetch a web page content from a given URL and cache the result

    :param url: The URL to retrieve the HTML content from
    :return: The HTML content of the URL
    """
    response = requests.get(url)
    return response.text
