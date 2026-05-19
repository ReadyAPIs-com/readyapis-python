# Changelog

All notable changes to the Ready APIs Python SDK are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-05-19

### Added

- Initial release. Six hero APIs covered: geo, tax, fx, email, calendar, intel.
- Identity + catalog metadata endpoints (`Client.meta`).
- Typed return objects via lightweight `_types` (no Pydantic dependency).
- Demo mode: no-API-key calls hit `/demo/api/v1/*` with allowlisted params,
  zero-friction for tinkering and CI.
- `READYAPIS_API_KEY` env var support; explicit `api_key=` override.
- Configurable base URL (`READYAPIS_BASE_URL` or `Client(base_url=...)`).
- httpx-based — one HTTP dependency, sync-only client today.

[Unreleased]: https://github.com/ReadyAPIs-com/readyapis-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ReadyAPIs-com/readyapis-python/releases/tag/v0.1.0
