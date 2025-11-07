"""Polite HTTP client with retry, backoff, and rate limiting."""

import random
import time

import requests

# Store throttle state in a mutable container to avoid using the `global` statement.
# This keeps behavior identical but avoids module-level `global` usage flagged by ruff.
_THROTTLE = {"last_time": None}
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
    headers = {"User-Agent": ua}

    for attempt in range(max_retries):
        # Rate limiting: 1 RPS with jitter
        if _THROTTLE["last_time"] is not None:
            elapsed = time.time() - _THROTTLE["last_time"]
            min_interval = 1.0 / _RPS
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed + random.uniform(0, 0.1)
                time.sleep(sleep_time)

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            _THROTTLE["last_time"] = time.time()
            return response.text
        except requests.RequestException:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff: 0.5, 1, 2 seconds
            backoff = 0.5 * (2**attempt)
            time.sleep(backoff)

    raise RuntimeError("Unexpected end of retry loop")
