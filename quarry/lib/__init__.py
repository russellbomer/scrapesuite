"""
Quarry Core Library

Provides foundational utilities used by all scraping tools:
- HTTP client with rate limiting, retry logic, robots.txt compliance
- Token bucket rate limiter for per-domain request throttling  
- CSS selector utilities for robust element targeting
- Robots.txt parsing and policy enforcement
"""

from .http import create_session, get_html, get_rate_limiter, set_rate_limiter
from .policy import check_robots, is_allowed_domain
from .ratelimit import DomainRateLimiter, TokenBucket
from .robots import RobotsCache
from .selectors import (
    SelectorChain,
    build_fallback_chain,
    build_robust_selector,
    extract_structural_pattern,
    simplify_selector,
    validate_selector,
)

__all__ = [
    # HTTP utilities
    "create_session",
    "get_html",
    "get_rate_limiter",
    "set_rate_limiter",
    # Rate limiting
    "DomainRateLimiter",
    "TokenBucket",
    # Selector utilities
    "SelectorChain",
    "build_robust_selector",
    "simplify_selector",
    "validate_selector",
    "extract_structural_pattern",
    "build_fallback_chain",
    # Robots & Policy
    "RobotsCache",
    "check_robots",
    "is_allowed_domain",
]
