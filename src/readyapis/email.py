"""Email namespace — deliverability + auth posture validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._types import Response

if TYPE_CHECKING:
    from ._client import Client


class EmailNamespace:
    """Email deliverability checks.

    Wraps the ``/api/v1/email/*`` endpoints.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def validate(self, email: str) -> Response:
        """Full deliverability + auth check for an email address.

        Returns syntax validity, MX presence, SPF / DMARC / DKIM posture,
        disposable / free-provider classification, and a 0-100
        ``deliverability_score``.

        In demo mode, only ``"hello@stripe.com"`` is allowlisted.
        """
        return self._client._get("/email/validate", email=email)

    def disposable(self, email: str) -> Response:
        """Quick check: is this a known disposable / throwaway address?"""
        return self._client._get("/email/disposable", email=email)

    def free(self, email: str) -> Response:
        """Quick check: is this a free-provider mailbox (gmail.com, etc.)?"""
        return self._client._get("/email/free", email=email)
