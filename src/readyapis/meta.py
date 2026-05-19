"""Meta namespace — whoami, catalog, dataset metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._errors import ApiError
from ._types import Response

if TYPE_CHECKING:
    from ._client import Client


class MetaNamespace:
    """Meta endpoints — identity probe, API catalog, dataset metadata.

    Wraps the ``/api/v1/meta/*`` endpoints.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def whoami(self) -> Response:
        """Verify the configured API key.

        Returns plan slug, monthly credit balance, redacted key prefix, and
        rate-limit ceiling. Costs zero credits — intended as a startup probe.

        Raises:
            ApiError: ``whoami`` requires an API key. Calling it in demo mode
                (without a key) will raise immediately rather than hit the
                server, since ``/demo/api/v1/meta/whoami`` does not exist.
        """
        if self._client.is_demo:
            raise ApiError(
                "meta.whoami() requires an API key. Set READYAPIS_API_KEY or "
                "pass api_key= to Client(). Demo mode has no whoami endpoint.",
                status_code=0,
                code="demo_mode_unsupported",
            )
        return self._client._get("/meta/whoami")

    def catalog(self) -> Response:
        """List all available datasets / APIs and their coverage metadata.

        Free to call in both demo and production modes.
        """
        return self._client._get("/meta/catalog")

    def dataset(self, slug: str) -> Response:
        """Coverage and provenance metadata for a single dataset."""
        return self._client._get(f"/meta/datasets/{slug}")
