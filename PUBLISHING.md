# Releasing a new version

Releases are tag-driven. Pushing a `v*.*.*` tag triggers
`.github/workflows/publish.yml`, which builds the sdist + wheel and
uploads to PyPI via the trusted-publisher OIDC flow (no API token in
GitHub secrets).

## Cutting a release

1. Update `src/readyapis/_version.py` and `pyproject.toml` to the new version.
2. Add a `## [X.Y.Z]` section to `CHANGELOG.md` summarizing user-visible changes.
3. Open a PR, get CI green, merge.
4. Tag the merge commit and push:

   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

5. Watch the publish workflow on Actions. The job:
   - Installs `build`, runs `python -m build` to produce `dist/`.
   - Imports the freshly-built wheel as a smoke test.
   - Uploads to PyPI via OIDC trusted publishing.

6. Verify on PyPI: <https://pypi.org/project/readyapis/>. Should appear
   within a minute.

## One-time setup (already done for the canonical repo)

Trusted-publisher configuration on PyPI side:

1. Visit <https://pypi.org/manage/project/readyapis/settings/publishing/>.
2. Add a new pending publisher:
   - **Owner**: `ReadyAPIs-com`
   - **Repository**: `readyapis-python`
   - **Workflow**: `publish.yml`
   - **Environment**: leave blank (or pin to a release env if you set one up)

After the first successful run the pending-publisher graduates and
subsequent tag pushes publish without further setup.

## Versioning

SemVer. Breaking changes bump major. New endpoint coverage bumps minor.
Bug fixes / docs bump patch. Pre-1.0: minor bumps may include breaking
changes for surface that has fewer than five external consumers,
documented in CHANGELOG.
