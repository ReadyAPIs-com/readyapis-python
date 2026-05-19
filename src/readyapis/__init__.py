"""Official Python SDK for Ready APIs.

Quick start:

    from readyapis import Client

    client = Client()  # demo mode, no key needed
    zip_data = client.geo.zip("30301")
    print(zip_data.city, zip_data.state)  # "Atlanta", "GA"

Set ``READYAPIS_API_KEY`` in your environment, or pass ``api_key="ra_live_..."``
explicitly, to hit the production API.
"""

from ._client import Client
from ._errors import (
    ApiError,
    AuthError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from ._types import Response
from ._version import __version__

__all__ = [
    "Client",
    "Response",
    "ApiError",
    "AuthError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "__version__",
]
