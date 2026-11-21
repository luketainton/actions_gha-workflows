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

Create the project in [Qualor](https://qualor.tainton.uk) and save its project
analysis token in the source repository's Actions secrets as `QUALOR_TOKEN`.
Use the repository's `owner/repo` as the project key, or set
`qualor-project-key` to match the key you chose in Qualor.

```yaml
jobs:
  ci:
    uses: actions/gha-workflows/.gitea/workflows/ci-python-unified.yml@main
    with:
      qualor-enabled: true
    secrets:
      QUALOR_TOKEN: ${{ secrets.QUALOR_TOKEN }}
```

The `qualor-url` input defaults to `https://qualor.tainton.uk`. Override it
if your runner needs a different address to reach the server without a browser
login. The optional scan runs as a container action at the end of the existing
Python CI job, after its regular checks pass. It uses a fresh checkout so that
CI changes to dependency manifests and lockfiles do not affect analysis. Branch
pushes, manual branch runs, and same-repository pull requests can run the step.
Fork pull requests and `pull_request_target` events skip it.

Qualor reports findings in its dashboard and fails the Actions job when the
quality gate fails. Test coverage remains in the regular CI artifact. Run a
scan on the project's main branch to establish a baseline.

See [Qualor's generic CI documentation](https://qualor.dev/docs/other-ci).

### Qualor token from 1Password

Set `qualor-onepassword-key` to the entry in the caller organisation's
`ORG_RENOVATE_ONEPASSWORD_REFERENCES` JSON object that holds the project's
`op://` reference. Pass the organisation's 1Password service account token to
the reusable workflow. The workflow resolves the selected entry in the CI job.

```yaml
    with:
      qualor-enabled: true
      qualor-onepassword-key: QUALOR_TOKEN
    secrets:
      ONEPASSWORD_SERVICE_ACCOUNT_TOKEN: ${{ secrets.ONEPASSWORD_SERVICE_ACCOUNT_TOKEN }}
```
