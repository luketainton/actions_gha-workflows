# Proposal

## Why

Python Unified CI provides a consistent place for projects to run quality checks, but it currently has no optional static type checking stage. Projects that use Pyrefly must maintain this check separately, so enabling it through the reusable workflow will make type checking easier to adopt consistently.

## What Changes

- Add an opt-in `pyrefly` boolean input to Python Unified CI, defaulting to `false` so existing callers retain current behavior.
- When enabled, add Pyrefly using the calling project's selected package manager and run it as a distinct CI stage.
- Document how projects should declare Pyrefly in their development dependencies and enable the stage.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `python-unified-ci`: Define optional Pyrefly type checking through the reusable workflow.

## Impact

- `.github/workflows/ci-python-unified.yml` reusable workflow inputs and steps.
- `docs/ci-python-unified.md` usage and dependency guidance.
- OpenSpec capability spec and workflow validation coverage.
