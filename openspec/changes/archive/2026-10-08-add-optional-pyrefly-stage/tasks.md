# Tasks

## 1. Add the opt-in Pyrefly CI stage

- [x] 1.1 Add the `pyrefly` boolean input with a false default, install Pyrefly through pip, Poetry, or uv only when enabled, and add a package-manager-routed Pyrefly stage; verify enabled and disabled behavior for each supported manager with focused workflow checks.
- [x] 1.2 Extend workflow validation coverage for the new input, dependency setup, and runner branches; run the focused validation command and confirm failures propagate from the Pyrefly stage.

## 2. Document Pyrefly opt-in

- [x] 2.1 Update `docs/ci-python-unified.md` with Pyrefly dependency and caller-input guidance; verify the documented YAML and package-manager instructions match the workflow.
