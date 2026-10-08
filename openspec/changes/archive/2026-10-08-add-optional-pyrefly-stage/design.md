# Design

## Context

See proposal.md - Why. The reusable workflow accepts `pip`, `poetry`, and `uv`, installs baseline CI tools, and has a boolean `security-scan` option that conditionally adds a tool before running its check through the selected environment. Pyrefly will follow that established optional-tool pattern.

## Goals / Non-Goals

**Goals:**
- Keep Pyrefly opt-in for existing workflow callers.
- Add and invoke Pyrefly using the selected project's package manager.
- Keep type checking as a distinct named stage with normal CI failure behavior.

**Non-Goals:**
- Configure project-specific Pyrefly rules or file selection.
- Change the workflow's default checks or package-manager support.

## Decisions

- Add a `pyrefly` boolean workflow input defaulting to `false`. This preserves behavior for existing callers while allowing explicit adoption.
- When enabled, add Pyrefly to the workflow's CI development dependencies for Poetry and uv, analogous to the optional pip-audit dependency steps. For pip, use the installed project's environment and ensure Pyrefly is available through the dependency installation approach documented for pip projects.
- Run Pyrefly through the selected environment: `pyrefly check` for pip, `poetry run pyrefly check` for Poetry, and `uv run pyrefly check` for uv. This uses Pyrefly's documented CLI and keeps command execution aligned with the project's dependency environment.
- Place the check after the selected environment has been synchronized with the optional dependency and alongside the Ruff checks. Do not run a second type check when the input is false.

## Risks / Trade-offs

- [Pyrefly CLI behavior can change between releases] -> Invoke the documented `pyrefly check` command through the selected package manager environment.
- [Dynamically adding a dependency may alter the lockfile in the checkout] -> Follow the existing CI behavior for optional tools and avoid committing generated lockfile changes.

## Migration Plan

No migration is required. Existing callers omit the new input and retain the default disabled behavior. Callers can opt in by declaring Pyrefly as a development dependency and setting `pyrefly: true`; rollback is setting it to false or removing the input.
