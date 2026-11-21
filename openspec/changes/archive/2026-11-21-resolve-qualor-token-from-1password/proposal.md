## Why

Gitea projects can keep their Qualor analysis tokens in 1Password and their references in the organisation's existing JSON variable.

## What Changes

Add an optional reference key and resolve that entry in the existing CI job.

## Capabilities

### Modified Capabilities

- `python-unified-ci` resolves an optional Qualor token reference through 1Password.

## Impact

Callers can continue providing a project token directly. Callers that select a reference also supply the 1Password service account token.
