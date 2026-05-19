"""FX namespace — exchange rates, conversion, historical."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from ._types import Response

if TYPE_CHECKING:
    from ._client import Client


class FxNamespace:
    """Foreign exchange rates and conversion.

    Wraps the ``/api/v1/fx/*`` endpoints.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def rates(
        self,
        base: str = "USD",
        symbols: Optional[Union[list[str], str]] = None,
    ) -> Response:
        """Get current exchange rates, rebased to ``base``.

        Args:
            base: Three-letter base currency code (e.g. ``"USD"``).
            symbols: Restrict to a subset (e.g. ``["EUR", "GBP", "JPY"]``).
                Pass a list or a comma-joined string. Omit for all currencies.
        """
        return self._client._get("/fx/rates", base=base, symbols=symbols)

    def convert(
        self,
        amount: float,
        from_: str,
        to: str,
        *,
        date: Optional[str] = None,
    ) -> Response:
        """Convert ``amount`` ``from_`` one currency ``to`` another.

        Args:
            amount: The amount to convert.
            from_: Source currency code. (Underscore avoids the Python keyword.)
            to: Destination currency code.
            date: Optional ISO date (``"YYYY-MM-DD"``) for historical rates.
        """
        return self._client._get(
            "/fx/convert",
            amount=amount,
            **{"from": from_},
            to=to,
            date=date,
        )

    def historical(self, date: str, base: str = "USD") -> Response:
        """Historical rates for a specific date (``"YYYY-MM-DD"``)."""
        return self._client._get("/fx/historical", date=date, base=base)

    def timeseries(
        self,
        start: str,
        end: str,
        base: str = "USD",
        symbols: Optional[Union[list[str], str]] = None,
    ) -> Response:
        """Time series of daily rates from ``start`` to ``end`` (inclusive)."""
        return self._client._get(
            "/fx/timeseries",
            start=start,
            end=end,
            base=base,
            symbols=symbols,
        )

    def currencies(self) -> Response:
        """List all supported currency codes."""
        return self._client._get("/fx/currencies")
