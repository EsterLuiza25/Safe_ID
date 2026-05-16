from .base import *  # noqa: F401,F403


DEBUG = False
SAFEGUARD_RATE_LIMIT = "1000/min"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "safeguard-tests",
    }
}

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["api"] = SAFEGUARD_RATE_LIMIT
