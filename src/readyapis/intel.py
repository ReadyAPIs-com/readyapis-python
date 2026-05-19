"""Intel namespace — composite signals: site risk, company signals, etc."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ._types import Response

if TYPE_CHECKING:
    from ._client import Client


# Demo mode requires one of these site profiles. Production accepts more.
_DEMO_SITE_PROFILES = (
    "data_center_site",
    "insurance_underwriting",
    "remote_office",
    "retail_storefront",
    "small_office",
    "warehouse_distribution",
)


class IntelNamespace:
    """Composite intelligence signals.

    Wraps the ``/api/v1/intel/*`` endpoints — these are blended scores
    computed from multiple underlying datasets (FEMA + USGS + NOAA for
    site risk, SEC + WHOIS + hiring for company signals, etc.).
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def site_risk(
        self,
        zip: str,
        site_profile: str = "insurance_underwriting",
    ) -> Response:
        """Composite site-risk score for a US ZIP.

        Blends FEMA flood, USGS seismic, NOAA wind/wildfire, climate, and EIA
        grid-reliability signals into a single 0-100 score with an
        underwriting tier (A / B / C / D) and red-flag list.

        Args:
            zip: US ZIP code. Demo allowlist: ``10001``, ``30301``, ``30303``,
                ``60601``, ``78701``, ``94105``, ``98101``.
            site_profile: One of ``data_center_site``,
                ``insurance_underwriting``, ``remote_office``,
                ``retail_storefront``, ``small_office``,
                ``warehouse_distribution``. (Production accepts additional
                values like ``commercial_property``.)
        """
        return self._client._get(
            "/intel/site-risk",
            zip=zip,
            site_profile=site_profile,
        )

    def company_signal(
        self,
        domain: Optional[str] = None,
        ticker: Optional[str] = None,
        profile: str = "enterprise_sales",
    ) -> Response:
        """B2B buyer-signal score (0-100) for a company by domain or ticker."""
        return self._client._get(
            "/intel/company-signal",
            domain=domain,
            ticker=ticker,
            profile=profile,
        )

    def company_change(
        self,
        domain: Optional[str] = None,
        ticker: Optional[str] = None,
    ) -> Response:
        """Detect recent material changes for a company."""
        return self._client._get(
            "/intel/company-change",
            domain=domain,
            ticker=ticker,
        )

    def compliance_signal(self, domain: str) -> Response:
        """Compliance posture (SPF/DMARC, HSTS, CSP, etc.) for a domain."""
        return self._client._get("/intel/compliance-signal", domain=domain)

    def counterparty_risk(self, domain: str) -> Response:
        """Counterparty risk score for a vendor / partner domain."""
        return self._client._get("/intel/counterparty-risk", domain=domain)

    def cyber_risk(self, domain: str) -> Response:
        """External cyber-risk posture for a domain."""
        return self._client._get("/intel/cyber-risk", domain=domain)

    def funding_signal(
        self,
        domain: Optional[str] = None,
        ticker: Optional[str] = None,
    ) -> Response:
        """Recent funding / capital-raise signal for a company."""
        return self._client._get(
            "/intel/funding-signal",
            domain=domain,
            ticker=ticker,
        )

    def hiring_signal(self, domain: str) -> Response:
        """Hiring momentum signal for a company."""
        return self._client._get("/intel/hiring-signal", domain=domain)

    def location_score(self, zip: str, profile: str = "retail_storefront") -> Response:
        """Composite location desirability score for a ZIP + business profile."""
        return self._client._get("/intel/location-score", zip=zip, profile=profile)

    def remote_hire_cost(self, country: str, role: str) -> Response:
        """Estimated total cost-of-hire for a remote employee."""
        return self._client._get(
            "/intel/remote-hire-cost",
            country=country,
            role=role,
        )

    def tech_stack(self, domain: str) -> Response:
        """Detected technology stack for a domain."""
        return self._client._get("/intel/tech-stack", domain=domain)

    def rank(
        self,
        candidates: list[dict],
        objective: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> Response:
        """Rank a list of candidates by an objective.

        POST endpoint; supports an optional ``idempotency_key`` for safe retries.
        """
        return self._client._post(
            "/intel/rank",
            {"candidates": candidates, "objective": objective},
            idempotency_key=idempotency_key,
        )
