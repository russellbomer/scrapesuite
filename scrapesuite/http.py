"""Polite HTTP client with retry, backoff, and rate limiting."""

import random
import time

import requests

_THROTTLE_LAST_TIME: float | None = None
_RPS = 1.0


def get_html(
    url: str,
    *,
    ua: str = "ScrapeSuite/1.0 (+contact@example.com)",
    timeout: int = 15,
    max_retries: int = 3,
) -> str:
    """
    Fetch HTML with retry, exponential backoff, and rate limiting.

    Not used in offline mode or tests.
    """
    global _THROTTLE_LAST_TIME

    headers = {"User-Agent": ua}

    for attempt in range(max_retries):
        # Rate limiting: 1 RPS with jitter
        if _THROTTLE_LAST_TIME is not None:
            elapsed = time.time() - _THROTTLE_LAST_TIME
            min_interval = 1.0 / _RPS
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed + random.uniform(0, 0.1)
                time.sleep(sleep_time)

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            _THROTTLE_LAST_TIME = time.time()
            return response.text
        except requests.RequestException:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff: 0.5, 1, 2 seconds
            backoff = 0.5 * (2**attempt)
            time.sleep(backoff)

    raise RuntimeError("Unexpected end of retry loop")
