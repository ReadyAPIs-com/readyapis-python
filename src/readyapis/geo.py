"""Geo namespace — ZIP, city, IP, county, timezone, nearby, enrich."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ._types import Response

if TYPE_CHECKING:
    from ._client import Client


class GeoNamespace:
    """Location enrichment.

    Wraps the ``/api/v1/geo/*`` endpoints.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def zip(self, zip_code: str) -> Response:
        """Look up a US ZIP code.

        Returns city, state, county, lat/lon, demographics, climate, and FEMA
        flood risk. In demo mode, only allowlisted ZIPs work — try ``"30301"``,
        ``"10001"``, ``"94105"``, ``"60601"``, ``"78701"``, or ``"98101"``.
        """
        return self._client._get(f"/geo/zip/{zip_code}")

    def city(self, name: str, state: str = "") -> Response:
        """Search for ZIPs by city name (and optional state).

        Returns a list of matching ZIP profiles. In demo mode the API only
        accepts a handful of sample cities (Atlanta+GA, New York+NY, etc.) —
        for arbitrary city searches you need a production API key.
        """
        return self._client._get("/geo/city", name=name, state=state)

    def ip(self, ip: str) -> Response:
        """Geolocate an IP address.

        Returns country, city (when known), lat/lon, timezone, ASN, ISP, and
        a hosting/proxy classification.
        """
        return self._client._get("/geo/ip", ip=ip)

    def enrich(
        self,
        zip: Optional[str] = None,
        ip: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Response:
        """One-shot enrichment for whatever signal you have.

        Pass exactly one of ``zip``, ``ip``, or a ``latitude``/``longitude`` pair.
        Returns the full enriched profile (demographics, climate, hazards).
        """
        return self._client._get(
            "/geo/enrich",
            zip=zip,
            ip=ip,
            latitude=latitude,
            longitude=longitude,
        )

    def nearby(
        self,
        lat: float,
        lon: float,
        radius_miles: int = 10,
        limit: Optional[int] = None,
    ) -> Response:
        """List ZIP codes within ``radius_miles`` of a lat/lon point.

        Note: the API takes ``lat`` + ``lon`` (not ``zip``). To search by ZIP,
        call :meth:`zip` first to get coordinates, then pass them here.
        """
        return self._client._get(
            "/geo/nearby",
            lat=lat,
            lon=lon,
            radius_miles=radius_miles,
            limit=limit,
        )

    def county(self, fips: str) -> Response:
        """Look up a US county by 5-digit FIPS code."""
        return self._client._get(f"/geo/county/{fips}")

    def timezone(
        self,
        zip: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Response:
        """Resolve a timezone from a ZIP or a lat/lon pair."""
        return self._client._get(
            "/geo/timezone",
            zip=zip,
            latitude=latitude,
            longitude=longitude,
        )

    def asn(self, ip: Optional[str] = None, asn: Optional[int] = None) -> Response:
        """Look up ASN / ISP info by IP or AS number."""
        return self._client._get("/geo/asn", ip=ip, asn=asn)
