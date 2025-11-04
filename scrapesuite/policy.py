"""Policy enforcement: allowlist, robots, rate limiting."""

from dataclasses import dataclass
from urllib.parse import urlparse


def is_allowed_domain(url: str, allowlist: list[str]) -> bool:
    """Check if URL domain is in allowlist."""
    if not allowlist:
        return True

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    for allowed in allowlist:
        allowed_domain = allowed.lower().strip()
        if allowed_domain.startswith("www."):
            allowed_domain = allowed_domain[4:]
        if domain == allowed_domain or domain.endswith("." + allowed_domain):
            return True

    return False


def check_robots(url: str) -> bool:
    """
    Stub robots.txt checker.

    TODO: Implement proper robots.txt parsing and checking.
    For now, returns True (allow all).
    """
    return True


@dataclass
class RateProfile:
    """Rate limiting profile."""

    rps: float = 1.0
    burst: int = 1
