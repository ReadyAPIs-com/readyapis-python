# readyapis-python

[![PyPI](https://img.shields.io/pypi/v/readyapis.svg)](https://pypi.org/project/readyapis/)
[![Python versions](https://img.shields.io/pypi/pyversions/readyapis.svg)](https://pypi.org/project/readyapis/)
[![Test](https://github.com/ReadyAPIs-com/readyapis-python/actions/workflows/test.yml/badge.svg)](https://github.com/ReadyAPIs-com/readyapis-python/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> Official Python SDK for [Ready APIs](https://readyapis.com) — the curated data layer for products and AI agents.

```bash
pip install readyapis
```

Six hero APIs (geo, tax, fx, email, calendar, intel) plus identity / catalog metadata, in one tiny typed client. No Pydantic, no codegen — just `httpx` and the standard library.

## Quick start

```python
from readyapis import Client

# Demo mode — no key needed. Hits /demo/api/v1/* with allowlisted params.
client = Client()

zip_data = client.geo.zip("30301")
print(zip_data.city, zip_data.state)          # "Atlanta" "GA"

tax = client.tax.calculate(income=125000, state="NY", year=2026, filing_status="single")
print(tax.federal["tax"], tax.taxable_income) # 18733.42  108900.0

fx = client.fx.convert(amount=100, from_="USD", to="EUR")
print(fx.converted)                           # 85.4555
```

## Authentication

Set an API key as an environment variable (recommended) or pass it explicitly:

```bash
export READYAPIS_API_KEY=ra_live_...
```

```python
from readyapis import Client

client = Client()                          # reads READYAPIS_API_KEY
client = Client(api_key="ra_live_...")     # explicit override
```

Get a key at <https://readyapis.com/register>. Free tier: 1,000 credits/month.

## Demo mode

If no API key is configured, the client enters **demo mode** automatically. It hits `/demo/api/v1/*` routes, which require no auth but only accept a small set of allowlisted parameters (ZIP `30301`, email `hello@stripe.com`, etc.) — perfect for tinkering and CI.

```python
client = Client()
assert client.is_demo

# Demo allowlist: 10001, 30301, 30303, 60601, 78701, 94105, 98101.
client.geo.zip("30301")                    # OK
client.geo.zip("12345")                    # raises ApiError (demo_parameter_not_allowed)
```

## Namespaces

```python
client.geo.zip("30301")
client.geo.city(name="Atlanta", state="GA")
client.geo.ip("8.8.8.8")
client.geo.enrich(zip="30301")
client.geo.nearby(lat=33.7488, lon=-84.3877, radius_miles=10)

client.tax.calculate(income=125000, state="NY", year=2026, filing_status="single")
client.tax.brackets(year=2026)                    # federal
client.tax.brackets(year=2026, state="NY")        # state
client.tax.deductions(year=2026, filing_status="single")

client.fx.rates(base="USD")
client.fx.rates(base="USD", symbols=["EUR", "GBP", "JPY"])
client.fx.convert(amount=100, from_="USD", to="EUR")

client.email.validate("hello@stripe.com")

client.calendar.holidays(country="US", year=2026)
client.calendar.business_days(start="2026-01-01", end="2026-01-31")

client.intel.site_risk(zip="30301", site_profile="insurance_underwriting")

client.meta.whoami()        # requires API key
client.meta.catalog()       # free
```

The full list of demo-allowed `site_profile` values: `data_center_site`, `insurance_underwriting`, `remote_office`, `retail_storefront`, `small_office`, `warehouse_distribution`. Production mode accepts more.

## Response shape

Every response is wrapped in a `Response` object that proxies the JSON:API-flavored envelope. You can use ergonomic attribute access, dict-style lookup, or get the raw payload.

```python
r = client.geo.zip("30301")

r.city            # "Atlanta"           — flattened from data.attributes
r.state           # "GA"
r["county"]       # "Fulton"            — dict-style works too
r.data            # the full data dict
r.attributes      # just the attributes dict
r.meta            # {credits_used, source, ...}
r.raw             # the full underlying JSON
```

For list responses, iterate or index:

```python
holidays = client.calendar.holidays(country="US", year=2026)
assert holidays.is_list
for h in holidays:
    print(h.date, h.name)
```

## Errors

All errors inherit from `ApiError`. Specific subclasses let you branch on common cases:

```python
from readyapis import Client, ApiError, AuthError, RateLimitError, NotFoundError

try:
    client.geo.zip("99999")
except RateLimitError as e:
    print(f"slow down — retry in {e.retry_after}s")
except AuthError as e:
    print(f"bad key: {e.code}")
except NotFoundError as e:
    print(f"not found: {e.message}")
except ApiError as e:
    print(f"{e.status_code} {e.code}: {e.message}")
    print(e.body)   # full error envelope
```

Every `ApiError` exposes `.status_code`, `.code`, `.message`, `.body`, and (for 429s) `.retry_after`.

## Retry behavior

The client automatically retries `429`, `500`, `502`, `503`, and `504` responses with exponential backoff (0.5s, 1s, 2s — three attempts total) plus small jitter. On `429`, it honors `Retry-After` if present. Disable per-client:

```python
client = Client(retry=False)
```

## Idempotency

`POST` endpoints accept an `idempotency_key` keyword. The server treats two requests with the same key (within the idempotency window) as the same logical operation — safe to retry from the client.

```python
client.intel.rank(
    candidates=[...],
    objective="enterprise_buyer",
    idempotency_key="run-2026-05-14-abc",
)
```

## Configuration

```python
Client(
    api_key=None,                          # str | None — falls back to READYAPIS_API_KEY env
    base_url="https://readyapis.com",      # override for staging/local
    timeout=30.0,                          # per-request seconds
    retry=True,                            # retry 429 + 5xx with backoff
    user_agent=None,                       # override the UA string
    http_client=None,                      # bring your own httpx.Client
)
```

## Compatibility

Python 3.9 and later. Only runtime dependency is `httpx >= 0.24, < 1.0`.

## License

MIT
