"""The Ready APIs HTTP client.

The :class:`Client` glues together transport (httpx), auth, retry, and the
six hero namespaces (geo, tax, fx, email, calendar, intel) plus ``meta``.

Usage::

    from readyapis import Client

    # Demo mode — no key needed, hits /demo/api/v1/* with allowlisted params.
    client = Client()

    # Production — explicit key:
    client = Client(api_key="ra_live_...")

    # Production — falls back to READYAPIS_API_KEY in env:
    client = Client()
"""

from __future__ import annotations

import os
import random
import time
from typing import Any, Optional

import httpx

from ._errors import from_response
from ._types import Response
from ._version import __version__ as _SDK_VERSION

_DEFAULT_BASE_URL = "https://readyapis.com"
_DEFAULT_TIMEOUT = 30.0
_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
_RETRY_BACKOFF_SECONDS = (0.5, 1.0, 2.0)


class Client:
    """Ready APIs Python client.

    Args:
        api_key: A ``ra_live_...`` API key. If ``None``, reads ``READYAPIS_API_KEY``
            from the environment. If still ``None``, the client enters **demo mode**
            and hits ``/demo/api/v1/*`` routes (no auth, allowlisted parameters only).
        base_url: Override the API host. Defaults to ``https://readyapis.com``.
            Useful for local development or staging.
        timeout: Per-request timeout in seconds. Default 30.
        retry: If ``True`` (default), retry on 429 and 5xx responses up to 3 times
            with exponential backoff (0.5s, 1s, 2s). Pass ``False`` to disable.
        user_agent: Override the User-Agent header. Defaults to
            ``"readyapis-python/<version>"``.
        http_client: Pass your own pre-configured ``httpx.Client`` instance.
            If omitted, one is created and managed by the client.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
        retry: bool = True,
        user_agent: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("READYAPIS_API_KEY") or None
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry = retry
        self.user_agent = user_agent or f"readyapis-python/{_SDK_VERSION}"
        self.is_demo = api_key is None

        self._owns_http_client = http_client is None
        self._http = http_client or httpx.Client(timeout=timeout)

        # Lazily-imported to avoid circular references at module load time.
        from .geo import GeoNamespace
        from .tax import TaxNamespace
        from .fx import FxNamespace
        from .email import EmailNamespace
        from .calendar import CalendarNamespace
        from .intel import IntelNamespace
        from .meta import MetaNamespace

        self.geo = GeoNamespace(self)
        self.tax = TaxNamespace(self)
        self.fx = FxNamespace(self)
        self.email = EmailNamespace(self)
        self.calendar = CalendarNamespace(self)
        self.intel = IntelNamespace(self)
        self.meta = MetaNamespace(self)

    # ── lifecycle ───────────────────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying HTTP client (if we own it)."""
        if self._owns_http_client:
            self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ── internal HTTP helpers ───────────────────────────────────────────────

    def _build_url(self, path: str) -> str:
        """Resolve a relative API path (e.g. ``"/geo/zip/30301"``) to a full URL.

        Path must start with ``/`` and use the ``/api/v1`` shape (or any path
        starting with ``/``). Demo-mode requests are rewritten to ``/demo``.
        """
        if not path.startswith("/"):
            path = "/" + path
        if not path.startswith("/api/v1") and not path.startswith("/demo"):
            path = "/api/v1" + path
        if self.is_demo and not path.startswith("/demo"):
            path = "/demo" + path
        return self.base_url + path

    def _headers(self, extra: Optional[dict[str, str]] = None) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if extra:
            headers.update(extra)
        return headers

    @staticmethod
    def _clean_params(params: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        if not params:
            return None
        out: dict[str, Any] = {}
        for k, v in params.items():
            if v is None:
                continue
            if isinstance(v, bool):
                out[k] = "true" if v else "false"
            elif isinstance(v, (list, tuple)):
                # comma-joined; the API accepts ``symbols=EUR,GBP,JPY``
                out[k] = ",".join(str(x) for x in v)
            else:
                out[k] = v
        return out

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_body: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Response:
        """Issue a raw request and return a wrapped :class:`Response`.

        End users typically don't call this directly — use the namespace methods
        (e.g. ``client.geo.zip(...)``). But it's exposed so you can hit any
        Ready APIs endpoint that isn't yet wrapped.
        """
        url = self._build_url(path)
        clean_params = self._clean_params(params)
        extra_headers: dict[str, str] = {}
        if idempotency_key:
            extra_headers["Idempotency-Key"] = idempotency_key
        headers = self._headers(extra_headers)

        attempts = 1 + (len(_RETRY_BACKOFF_SECONDS) if self.retry else 0)
        last_exc: Optional[Exception] = None

        for attempt in range(attempts):
            try:
                resp = self._http.request(
                    method.upper(),
                    url,
                    params=clean_params,
                    json=json_body,
                    headers=headers,
                )
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt < attempts - 1:
                    self._sleep_backoff(attempt, None)
                    continue
                raise

            if resp.status_code < 400:
                return Response(self._parse_json(resp))

            retry_after = self._parse_retry_after(resp)
            should_retry = (
                self.retry
                and attempt < attempts - 1
                and resp.status_code in _RETRY_STATUSES
            )
            if should_retry:
                self._sleep_backoff(attempt, retry_after)
                continue

            raise from_response(
                resp.status_code,
                self._parse_json(resp),
                retry_after=retry_after,
            )

        # Unreachable, but satisfies type checkers.
        if last_exc:
            raise last_exc
        raise RuntimeError("request loop exited without returning")

    @staticmethod
    def _parse_json(resp: httpx.Response) -> dict[str, Any]:
        try:
            data = resp.json()
        except ValueError:
            return {"error": {"code": "invalid_response", "message": resp.text or "non-JSON response"}}
        return data if isinstance(data, dict) else {"data": data}

    @staticmethod
    def _parse_retry_after(resp: httpx.Response) -> Optional[float]:
        raw = resp.headers.get("Retry-After")
        if not raw:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _sleep_backoff(attempt: int, retry_after: Optional[float]) -> None:
        if retry_after is not None:
            time.sleep(min(retry_after, 30.0))
            return
        base = _RETRY_BACKOFF_SECONDS[min(attempt, len(_RETRY_BACKOFF_SECONDS) - 1)]
        # Small jitter so retries don't thunder-herd.
        time.sleep(base + random.uniform(0, base / 4))

    # ── convenience GET/POST shortcuts for namespaces ──────────────────────

    def _get(self, path: str, **params: Any) -> Response:
        return self.request("GET", path, params=params or None)

    def _post(
        self,
        path: str,
        body: Optional[dict[str, Any]] = None,
        *,
        idempotency_key: Optional[str] = None,
    ) -> Response:
        return self.request("POST", path, json_body=body, idempotency_key=idempotency_key)
