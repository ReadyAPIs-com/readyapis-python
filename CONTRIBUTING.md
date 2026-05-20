# Contributing to `readyapis-python`

Thanks for taking the time to look at the source. This SDK is a thin wrapper around the Ready APIs HTTP surface — most issues are best filed against the upstream platform, but a few belong here.

## What lives in this repo

- The Python client (`src/readyapis/`)
- Type stubs / `__init__.py` re-exports
- Tests under `tests/`
- GitHub Actions for test + PyPI publish (trusted-publisher OIDC)

## What does NOT live in this repo

- API behavior, endpoint accuracy, rate limits, billing — see [readyapis.com/docs](https://readyapis.com/docs/getting-started)
- Dataset corrections (e.g. "this ZIP code is wrong") — email `hello@readyapis.com` with the source you have in mind

## Filing an issue

Good issue includes:

1. Python version (`python --version`)
2. `readyapis` version (`pip show readyapis | grep Version`)
3. Minimal repro — the smallest code that triggers the problem, with secrets redacted
4. What you expected, what happened

If the SDK call returned an error from the server, include the full `error` object — that helps tell SDK bugs from API bugs.

## Submitting a PR

For non-trivial changes, open an issue first so we can discuss the shape. For typo fixes / docstring improvements, just send the PR.

```bash
git clone https://github.com/ReadyAPIs-com/readyapis-python.git
cd readyapis-python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

PRs need:

- Passing CI (test + lint)
- A test covering the change (mock the HTTP layer; we don't hit prod in CI)
- A line in `CHANGELOG.md` under "Unreleased"

## Security

Don't open public issues for security problems. Email `security@readyapis.com` directly. We try to acknowledge within one business day.

## License

By contributing you agree your work is licensed under MIT (the project's license).
