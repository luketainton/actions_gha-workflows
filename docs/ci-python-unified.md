# Unified Python CI

`ci-python-unified.yml` is a reusable workflow for Python projects. It defaults
to Python 3.14 and accepts a JSON array through `python-versions` for a version
matrix.

The selected project's development dependency group should contain the CI
tools `ruff`, `pytest`, `pytest-cov`, and `coverage`. When `security-scan` is
enabled, the workflow adds `pip-audit` to that group with the selected package
manager before installing it. Set `pyrefly: true` to add Pyrefly through the
selected package manager and run `pyrefly check`. The `pyrefly` input defaults
to `false`.

Example caller:

```yaml
jobs:
  ci:
    uses: actions/gha-workflows/.github/workflows/ci-python-unified.yml@main
    with:
      package-manager: uv
      python-versions: '["3.13", "3.14"]'
      docker-enabled: true
      sonarqube: false
      security-scan: true
      pyrefly: true
```

For Poetry, use a `dev` dependency group. For uv, use dev dependencies (for
example, `uv add --dev ruff pytest pytest-cov coverage`). Pip projects should
provide a `[dev]` extra or a `requirements-dev.txt` file. When Pyrefly is
enabled, the workflow installs it with `python -m pip install pyrefly` for pip
projects and runs it in the selected environment. Poetry and uv projects can
add Pyrefly to their dev group with `poetry add --group dev pyrefly` or
`uv add --dev pyrefly`; the workflow adds it automatically when enabled.

## Optional Qualor scan on Gitea

The workflow reads the `QUALOR_TOKEN` entry in the instance-wide
`GLOBAL_ONEPASSWORD_REFERENCES` Actions variable. Store an `op://` reference
to the Qualor analysis token at that key. The Qualor project key defaults to
`owner/repo`.
Set `qualor-project-key` if the project uses a custom key.

```yaml
jobs:
  ci:
    uses: actions/gha-workflows/.gitea/workflows/ci-python-unified.yml@main
    with:
      qualor-enabled: true
    secrets:
      ONEPASSWORD_SERVICE_ACCOUNT_TOKEN: ${{ secrets.ONEPASSWORD_SERVICE_ACCOUNT_TOKEN }}
```

Use a 1Password service account with read access to the referenced item.
When migrating a caller that passes `QUALOR_TOKEN`, remove that secret from
the workflow call.

The `qualor-url` input defaults to `https://qualor.tainton.uk`. Override it
if your runner needs a different address to reach the server without a browser
login. The optional scan runs as a separate reusable workflow after the Python CI job
passes, downloading its coverage artifact. It uses a fresh checkout so that
CI changes to dependency manifests and lockfiles do not affect analysis. Branch
pushes, manual branch runs, and same-repository pull requests can run the step.
Fork pull requests and `pull_request_target` events skip it.

Qualor reports findings in its dashboard and fails the Actions job when the
quality gate fails. Test coverage remains in the regular CI artifact. Run a
scan on the project's main branch to establish a baseline.

See [Qualor's generic CI documentation](https://qualor.dev/docs/other-ci).

## Standalone Qualor scan

Call the Gitea workflow from a project using any language:

```yaml
jobs:
  qualor:
    uses: actions/gha-workflows/.gitea/workflows/qualor-scan.yml@main
    secrets:
      ONEPASSWORD_SERVICE_ACCOUNT_TOKEN: ${{ secrets.ONEPASSWORD_SERVICE_ACCOUNT_TOKEN }}
```

The same 1Password reference and event restrictions above apply. The optional
`qualor-url` and `qualor-project-key` inputs override their defaults. To
include coverage, upload a report as an Actions artifact in an earlier job,
set `coverage-artifact` to its name, and use `needs` to wait for that job.
The report defaults to `coverage.xml` at the artifact root; set
`coverage-file` to a different path within the artifact if needed. Without
an artifact, the scan runs without a coverage argument. Tag scans record
dependency versions and do not use coverage.
