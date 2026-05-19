"""Calendar namespace — holidays, business days."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ._types import Response

if TYPE_CHECKING:
    from ._client import Client


class CalendarNamespace:
    """Holiday calendars and business-day arithmetic.

    Wraps the ``/api/v1/calendar/*`` endpoints.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def holidays(self, country: str = "US", year: int = 2026) -> Response:
        """Federal / public holidays for a country + year.

        Currently the API exposes US federal holidays. State-level US holidays
        are available via :meth:`state_holidays`.
        """
        return self._client._get("/calendar/holidays", country=country, year=year)

    def state_holidays(self, state: str, year: int = 2026) -> Response:
        """US state-level holiday calendar for a two-letter state code."""
        return self._client._get("/calendar/state-holidays", state=state, year=year)

    def business_days(
        self,
        start: str,
        end: str,
        country: str = "US",
    ) -> Response:
        """Count business days between two dates (inclusive).

        Args:
            start: ISO date (``"YYYY-MM-DD"``).
            end: ISO date (``"YYYY-MM-DD"``).
            country: Country code; affects which holidays are excluded.

        Note: The underlying API parameter names are ``from`` / ``to`` (which
        are reserved words in Python), so this method renames them to
        ``start`` / ``end``.
        """
        # The API expects `from`/`to` query params; remap.
        return self._client.request(
            "GET",
            "/calendar/business-days/between",
            params={"from": start, "to": end, "country": country},
        )

    def add_business_days(
        self,
        start: str,
        days: int,
        country: str = "US",
    ) -> Response:
        """Add (or subtract) business days from a starting date."""
        return self._client.request(
            "GET",
            "/calendar/business-days/add",
            params={"from": start, "days": days, "country": country},
        )

    def is_business_day(self, date: str, country: str = "US") -> Response:
        """Is this date a business day in ``country``?"""
        return self._client._get("/calendar/is-business-day", date=date, country=country)

    def next_business_day(
        self,
        date: Optional[str] = None,
        country: str = "US",
    ) -> Response:
        """The next business day on or after ``date`` (defaults to today)."""
        return self._client._get(
            "/calendar/next-business-day",
            date=date,
            country=country,
        )
