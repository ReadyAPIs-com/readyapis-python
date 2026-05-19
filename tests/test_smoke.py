"""Smoke test for the Ready APIs Python SDK.

Hits each namespace's primary method against the live demo endpoints.
No API key required — runs entirely in demo mode.

Run as ``python tests/test_smoke.py`` (pure stdlib unittest) or
``pytest tests/test_smoke.py`` if you have pytest installed.

Network is required. Each test allows up to 30s for the round-trip.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Allow running directly: `python tests/test_smoke.py` from sdk/python/.
_HERE = Path(__file__).resolve().parent
_SRC = _HERE.parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from readyapis import ApiError, Client, NotFoundError  # noqa: E402


class SmokeTest(unittest.TestCase):
    """Live integration smoke test — uses demo mode (no key)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Client()
        assert cls.client.is_demo, "smoke test must run in demo mode (unset READYAPIS_API_KEY)"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()

    # ── geo ─────────────────────────────────────────────────────────────────

    def test_geo_zip(self) -> None:
        r = self.client.geo.zip("30301")
        self.assertEqual(r.city, "Atlanta")
        self.assertEqual(r.state, "GA")
        self.assertIn("data", r.raw)

    def test_geo_ip(self) -> None:
        r = self.client.geo.ip("8.8.8.8")
        self.assertEqual(r.country_code, "US")
        self.assertEqual(r.asn, 15169)

    def test_geo_enrich(self) -> None:
        r = self.client.geo.enrich(zip="30301")
        self.assertEqual(r.city, "Atlanta")

    def test_geo_nearby(self) -> None:
        # Atlanta's coords — demo allowlist.
        r = self.client.geo.nearby(lat=33.7488, lon=-84.3877, radius_miles=10)
        self.assertTrue(r.is_list)
        self.assertGreater(len(r), 0)

    def test_geo_city(self) -> None:
        r = self.client.geo.city(name="Atlanta", state="GA")
        self.assertTrue(r.is_list)
        self.assertGreater(len(r), 0)

    # ── tax ─────────────────────────────────────────────────────────────────

    def test_tax_calculate(self) -> None:
        r = self.client.tax.calculate(
            income=125000,
            state="NY",
            year=2026,
            filing_status="single",
        )
        self.assertEqual(r.year, 2026)
        self.assertEqual(r.filing_status, "single")
        self.assertGreater(r.federal["tax"], 0)

    def test_tax_brackets(self) -> None:
        r = self.client.tax.brackets(year=2026)
        self.assertTrue(r.is_list)
        self.assertGreater(len(r), 0)

    def test_tax_deductions(self) -> None:
        r = self.client.tax.deductions(year=2026, filing_status="single")
        self.assertTrue(r.is_list)

    # ── fx ──────────────────────────────────────────────────────────────────

    def test_fx_rates(self) -> None:
        r = self.client.fx.rates(base="USD")
        self.assertEqual(r.base, "USD")
        self.assertIn("rates", r.attributes)
        self.assertIn("EUR", r.rates)

    def test_fx_convert(self) -> None:
        r = self.client.fx.convert(amount=100, from_="USD", to="EUR")
        # Field is named "from" in the response; "to" is fine.
        self.assertEqual(r.to, "EUR")
        self.assertEqual(r.amount, 100.0)
        self.assertGreater(r.converted, 0)

    # ── email ──────────────────────────────────────────────────────────────

    def test_email_validate(self) -> None:
        r = self.client.email.validate("hello@stripe.com")
        self.assertEqual(r.domain, "stripe.com")
        self.assertTrue(r.syntax_valid)

    # ── calendar ───────────────────────────────────────────────────────────

    def test_calendar_holidays(self) -> None:
        r = self.client.calendar.holidays(country="US", year=2026)
        self.assertTrue(r.is_list)
        names = [item.name for item in r.items]
        self.assertIn("New Year's Day", names)

    def test_calendar_business_days(self) -> None:
        r = self.client.calendar.business_days(
            start="2026-01-01",
            end="2026-01-31",
            country="US",
        )
        self.assertGreater(r.business_days, 15)

    # ── intel ──────────────────────────────────────────────────────────────

    def test_intel_site_risk(self) -> None:
        r = self.client.intel.site_risk(
            zip="30301",
            site_profile="insurance_underwriting",
        )
        self.assertEqual(r.zip_code, "30301")
        self.assertIn(r.tier, ("A", "B", "C", "D"))
        self.assertGreaterEqual(r.risk_score, 0)
        self.assertLessEqual(r.risk_score, 100)

    # ── meta ───────────────────────────────────────────────────────────────

    def test_meta_catalog(self) -> None:
        r = self.client.meta.catalog()
        self.assertTrue(r.is_list)
        self.assertGreater(len(r), 0)

    def test_meta_whoami_raises_in_demo(self) -> None:
        with self.assertRaises(ApiError) as ctx:
            self.client.meta.whoami()
        self.assertEqual(ctx.exception.code, "demo_mode_unsupported")

    # ── errors ─────────────────────────────────────────────────────────────

    def test_not_found_raises(self) -> None:
        # 99999 isn't a valid ZIP -- expect a structured error.
        with self.assertRaises(ApiError) as ctx:
            self.client.geo.zip("99999")
        # Could be 404 / NotFoundError or a demo guard error — both are ApiError.
        self.assertGreaterEqual(ctx.exception.status_code, 400)


def _run_with_summary() -> int:
    """Run via unittest, print a clear pass/fail summary, return exit code."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(SmokeTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    total = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed
    print()
    print("=" * 60)
    print(f"  SMOKE TEST: {passed}/{total} passed")
    if failed:
        print(f"  {failed} failure(s) — see above.")
    print("=" * 60)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(_run_with_summary())
