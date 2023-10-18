#!/usr/bin/env python3
"""
Cache module
"""

import sys
import redis
import uuid
from typing import Union, Callable
from functools import wraps


# Define the count_calls decorator
def count_calls(method: Callable) -> Callable:
    """
    Decorator to count how many times methods of the Cache class are called

    :param method: The method to be wrapped
    :return: Wrapped method that increments the count for the key
    and returns the value returned by the original method
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrap
        :param self:
        :param args:
        :param kwargs:
        :return:
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


# Define the call_history decorator
def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function

    :param method: The method to be wrapped
    :return: Wrapped method that appends inputs and outputs to Redis lists
    """
    # Use the qualified name of the decorated method
    key = method.__qualname__
    input_key = "".join([key, ":inputs"])
    output_key = "".join([key, ":outputs"])

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Append input arguments as a string
        self._redis.rpush(input_key, str(args))

        # Execute the wrapped function to retrieve the output
        output = method(self, *args, **kwargs)

        # Append the output to the output list
        self._redis.rpush(output_key, str(output))
        return output

    return wrapper


class Cache:
    """
    Cache class for storing data in Redis
    """
    def __init__(self):
        """
        Initialize Cache with a Redis client instance and flush the database
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the input data in Redis using a random key and return the key

        :param data: Data to store (str, bytes, int, or float)
        :return: Random key used to store the data
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        Retrieve data using key and optionally apply
        the provided conversion function

        :param key: Key to retrieve data from Redis
        :param fn: Callable function to convert the data (optional)
        :return: Data retrieved from Redis with an optional conversion
        """
        data = self._redis.get(key)
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Retrieve a string from Redis using the given key

        :param key: Key to retrieve a string from Redis
        :return: String data retrieved from Redis
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """
        Retrieve an integer from Redis using the given key

        :param key: Key to retrieve an integer from Redis
        :return: Integer data retrieved from Redis
        """
        return self.get(key, fn=int)

    def replay(self, func: Callable):
        """
        Display the history of calls of a particular function.

        :param func: The function to replay.
        """
        input_key = "{}:inputs".format(func.__qualname__)
        output_key = "{}:outputs".format(func.__qualname__)

        inputs = self._redis.lrange(input_key, 0, -1)
        outputs = self._redis.lrange(output_key, 0, -1)

        if not inputs or not outputs:
            print(f"{func.__qualname__} was not called.")
        else:
            print(f"{func.__qualname__} was called {len(inputs)} times:")
            for input_args, output in zip(inputs, outputs):
                print(f"{func}({input_args.decode()}) -> {output.decode()}")
