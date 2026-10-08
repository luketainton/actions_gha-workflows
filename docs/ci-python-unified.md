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
