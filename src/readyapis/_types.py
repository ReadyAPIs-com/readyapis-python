"""Response wrapper for Ready APIs.

Every Ready APIs response uses a JSON:API-flavored envelope::

    {
        "data": {"id": "...", "type": "...", "attributes": {...}},
        "meta": {...},
        "links": {...}
    }

Or for list endpoints, ``data`` is a list of those resource objects.

The :class:`Response` wrapper lets you access fields ergonomically:

    result = client.geo.zip("30301")
    result.city                  # "Atlanta"  (auto-flattens .data.attributes)
    result.state                 # "GA"
    result.data                  # the raw .data dict
    result.attributes            # the raw .data.attributes dict
    result["city"]               # also works
    result.meta["credits_used"]  # access raw meta
    result.raw                   # full underlying dict
"""

from __future__ import annotations

from typing import Any, Iterator, Union


class Response:
    """Thin proxy over a Ready APIs JSON response.

    Resolution order for attribute access (e.g. ``result.city``):

    1. Top-level key on the envelope (rare; e.g. ``data``, ``meta``, ``links``).
    2. The ``data.attributes`` dict (most common — flattens JSON:API attributes).
    3. The ``data`` dict itself (e.g. for the ``id`` / ``type`` fields).

    For list responses (``data`` is a list), attribute access into ``attributes``
    is disabled — iterate over the response or use ``response.items`` instead.
    """

    __slots__ = ("_payload",)

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload if isinstance(payload, dict) else {"data": payload}

    # ── raw access ──────────────────────────────────────────────────────────

    @property
    def raw(self) -> dict[str, Any]:
        """The full response body as a Python dict."""
        return self._payload

    @property
    def data(self) -> Any:
        """The ``data`` field of the response (dict or list)."""
        return self._payload.get("data")

    @property
    def meta(self) -> dict[str, Any]:
        """The ``meta`` field of the response (always a dict, possibly empty)."""
        m = self._payload.get("meta")
        return m if isinstance(m, dict) else {}

    @property
    def links(self) -> dict[str, Any]:
        """The ``links`` field of the response (always a dict, possibly empty)."""
        ln = self._payload.get("links")
        return ln if isinstance(ln, dict) else {}

    @property
    def attributes(self) -> dict[str, Any]:
        """The ``data.attributes`` dict for single-resource responses, else ``{}``."""
        d = self._payload.get("data")
        if isinstance(d, dict):
            attrs = d.get("attributes")
            if isinstance(attrs, dict):
                return attrs
        return {}

    @property
    def items(self) -> list["Response"]:
        """For list responses, wrap each item in its own ``Response``.

        Returns an empty list for single-resource responses.
        """
        d = self._payload.get("data")
        if isinstance(d, list):
            return [Response({"data": item}) for item in d]
        return []

    @property
    def is_list(self) -> bool:
        """True if ``data`` is a list (collection response)."""
        return isinstance(self._payload.get("data"), list)

    # ── ergonomic attribute access ──────────────────────────────────────────

    def __getattr__(self, name: str) -> Any:
        # __slots__ + dunder lookups: bail early on internals
        if name.startswith("_"):
            raise AttributeError(name)
        payload = self._payload
        if name in payload:
            return payload[name]
        d = payload.get("data")
        if isinstance(d, dict):
            attrs = d.get("attributes")
            if isinstance(attrs, dict) and name in attrs:
                return attrs[name]
            if name in d:
                return d[name]
        raise AttributeError(
            f"{type(self).__name__!s} has no attribute {name!r}. "
            f"Available: {sorted(self.attributes.keys())[:6]}{'...' if len(self.attributes) > 6 else ''}"
        )

    def __getitem__(self, key: Union[str, int]) -> Any:
        if isinstance(key, int):
            d = self._payload.get("data")
            if isinstance(d, list):
                return Response({"data": d[key]})
            raise TypeError("integer indexing only valid for list responses")
        # string key: same fall-through as __getattr__
        payload = self._payload
        if key in payload:
            return payload[key]
        d = payload.get("data")
        if isinstance(d, dict):
            attrs = d.get("attributes")
            if isinstance(attrs, dict) and key in attrs:
                return attrs[key]
            if key in d:
                return d[key]
        raise KeyError(key)

    def __iter__(self) -> Iterator["Response"]:
        return iter(self.items)

    def __len__(self) -> int:
        if self.is_list:
            return len(self._payload["data"])
        return 1

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        if key in self._payload:
            return True
        d = self._payload.get("data")
        if isinstance(d, dict):
            if key in d:
                return True
            attrs = d.get("attributes")
            if isinstance(attrs, dict) and key in attrs:
                return True
        return False

    def get(self, key: str, default: Any = None) -> Any:
        """Safe lookup. Returns ``default`` if the key is not found."""
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    def __repr__(self) -> str:
        d = self._payload.get("data")
        if isinstance(d, list):
            return f"Response(list, len={len(d)})"
        if isinstance(d, dict):
            type_ = d.get("type", "?")
            id_ = d.get("id", "?")
            return f"Response(type={type_!r}, id={id_!r})"
        return f"Response({self._payload!r})"
