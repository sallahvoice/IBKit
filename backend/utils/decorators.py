"""Common decorators for timing, caching, retry, and singleton patterns."""

import hashlib
import json
import time
from functools import wraps
from pathlib import Path


def timing(func):
    """Time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {(end - start) * 1000:.4f} ms to execute")
        return result
    return wrapper


def default_key(args, kwargs):
    """Generate cache key from function arguments."""
    raw = repr((args, sorted(kwargs.items())))
    return hashlib.sha256(raw.encode()).hexdigest()


def disk_cache(ttl: int =86400, namespace: str ="default", key_fn=None):
    """Cache function results to disk with TTL."""
    def decorator(func):
        cache_dir = Path.cwd() / ".functions_cache" / namespace
        cache_dir.mkdir(parents=True, exist_ok=True)

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (key_fn or default_key)(args, kwargs)
            cache_file = cache_dir / f"{key}.json"
            # Check if cached result exists and is not expired
            if (
                cache_file.exists()
                and time.time() - cache_file.stat().st_mtime < ttl
            ):
                with open(cache_file, encoding='utf-8') as file:
                    return json.load(file)
            # Execute original function and cache result
            result = func(*args, **kwargs)
            with open(cache_file, "w", encoding='utf-8') as file:
                json.dump(result, file)
            return result
        return wrapper
    return decorator


class RetryErrror(Exception):
    """Exception raised when all retry attempts are exhausted."""

def retry(max_attempts: int =3, delay: float =1.0, backoff_factor: float =2.0):
    """Retry function on exception with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    last_exception = (
                        f"{func.__name__} failed after attempt {attempt} due to: {exc}"
                    )
                    if attempt < max_attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff_factor

            raise RetryErrror(last_exception) from None
        return wrapper
    return decorator


def singleton(cls):
    """Ensure a class has only one instance."""
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper