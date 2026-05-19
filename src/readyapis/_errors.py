"""Exception classes for Ready APIs SDK.

The server always returns a JSON error envelope::

    {"error": {"code": "...", "message": "...", "help_url": "..."}}

These exceptions surface that envelope verbatim, plus the HTTP status code and
the parsed body so callers can branch on ``err.code`` or inspect ``err.body``.
"""

from __future__ import annotations

from typing import Any, Optional


class ApiError(Exception):
    """Base exception for all Ready APIs errors.

    Attributes:
        message: Human-readable error message from the API.
        status_code: HTTP status code from the response.
        code: Machine-readable error code from the API (e.g. ``"invalid_api_key"``).
        body: The parsed JSON body of the response, if any.
        retry_after: Seconds to wait before retrying (set on 429 responses).
    """

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        code: Optional[str] = None,
        body: Optional[dict[str, Any]] = None,
        retry_after: Optional[float] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.body = body or {}
        self.retry_after = retry_after

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(status_code={self.status_code}, "
            f"code={self.code!r}, message={self.message!r})"
        )


class AuthError(ApiError):
    """401 / 403 — missing, invalid, or unauthorized API key."""


class NotFoundError(ApiError):
    """404 — resource or endpoint not found."""


class RateLimitError(ApiError):
    """429 — rate limit exceeded. Check ``retry_after``."""


class ServerError(ApiError):
    """5xx — Ready APIs is having a problem on its end."""


def from_response(status_code: int, body: dict[str, Any], retry_after: Optional[float] = None) -> ApiError:
    """Construct the appropriate ApiError subclass for a response."""
    err = body.get("error") if isinstance(body, dict) else None
    code = err.get("code") if isinstance(err, dict) else None
    message = (
        err.get("message")
        if isinstance(err, dict) and err.get("message")
        else f"HTTP {status_code}"
    )

    if status_code in (401, 403):
        cls = AuthError
    elif status_code == 404:
        cls = NotFoundError
    elif status_code == 429:
        cls = RateLimitError
    elif 500 <= status_code < 600:
        cls = ServerError
    else:
        cls = ApiError

    return cls(message=message, status_code=status_code, code=code, body=body, retry_after=retry_after)
