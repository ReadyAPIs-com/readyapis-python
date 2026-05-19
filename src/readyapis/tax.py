"""Tax namespace — federal + state calculations, brackets, deductions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ._types import Response

if TYPE_CHECKING:
    from ._client import Client


class TaxNamespace:
    """US tax calculations and reference data.

    Wraps the ``/api/v1/tax/*`` endpoints.

    Tax data is reference data only — not tax, legal, or financial advice.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def calculate(
        self,
        income: float,
        state: Optional[str] = None,
        year: int = 2026,
        filing_status: str = "single",
        *,
        additional_income: Optional[float] = None,
        self_employment_income: Optional[float] = None,
        long_term_capital_gains: Optional[float] = None,
        deductions: Optional[float] = None,
    ) -> Response:
        """Compute federal + (optionally) state income tax + FICA.

        Args:
            income: W-2 / wage income in dollars.
            state: Two-letter state code (e.g. ``"NY"``). Omit for federal-only.
            year: Tax year. Defaults to 2026.
            filing_status: One of ``"single"``, ``"married_joint"``,
                ``"married_separate"``, ``"head_of_household"``.
            additional_income: Other ordinary income (interest, side gigs).
            self_employment_income: Schedule C / SE income (subject to SE tax).
            long_term_capital_gains: LTCG, taxed at preferential rates.
            deductions: Override the standard deduction with an itemized amount.
        """
        return self._client._get(
            "/tax/calculate",
            income=income,
            state=state,
            year=year,
            filing_status=filing_status,
            additional_income=additional_income,
            self_employment_income=self_employment_income,
            long_term_capital_gains=long_term_capital_gains,
            deductions=deductions,
        )

    def brackets(
        self,
        year: int = 2026,
        state: Optional[str] = None,
        filing_status: Optional[str] = None,
    ) -> Response:
        """Get tax brackets.

        Returns federal brackets unless ``state`` is provided, in which case
        you get that state's brackets (which is the data behind state income
        tax in :meth:`calculate`).
        """
        if state:
            return self._client._get(
                f"/tax/state/{state}/brackets",
                year=year,
                filing_status=filing_status,
            )
        return self._client._get(
            "/tax/federal/brackets",
            year=year,
            filing_status=filing_status,
        )

    def deductions(
        self,
        year: int = 2026,
        filing_status: str = "single",
    ) -> Response:
        """Get the standard deduction for a year + filing status."""
        return self._client._get(
            "/tax/standard-deduction",
            year=year,
            filing_status=filing_status,
        )

    def mileage_rates(self, year: int = 2026) -> Response:
        """IRS standard mileage rates (business / medical / charity) for the year."""
        return self._client._get("/tax/mileage-rates", year=year)

    def retirement_limits(self, year: int = 2026) -> Response:
        """401(k), IRA, HSA, and similar contribution limits for the year."""
        return self._client._get("/tax/retirement-limits", year=year)

    def deadlines(self, year: int = 2026) -> Response:
        """Federal tax filing and quarterly estimated payment deadlines."""
        return self._client._get("/tax/deadlines", year=year)

    def summary(
        self,
        income: float,
        state: Optional[str] = None,
        year: int = 2026,
        filing_status: str = "single",
    ) -> Response:
        """One-shot tax overview: bracket, marginal + effective rate, take-home."""
        return self._client._get(
            "/tax/summary",
            income=income,
            state=state,
            year=year,
            filing_status=filing_status,
        )
