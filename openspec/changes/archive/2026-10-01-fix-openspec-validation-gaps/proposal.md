# Proposal

## Why

The OpenSpec PR gate can accept a changed main spec alongside an unrelated archive, and can reject valid date-prefixed change names. Its global archived-task check can also fail a PR because of unrelated historical work. Tighten the association and scope checks and add regression coverage.

## What Changes

- Require changed main spec capabilities to have corresponding delta specs in archived changes included in the PR.
- Recognize archive directory names that are already date-prefixed.
- Filter archived-task validation findings to archive directories touched by the PR, so unrelated historical findings do not block it.
- Add committed tests for PR path detection and archive/spec association behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `openspec-pr-validation`: require capability-specific archive association, accept pre-dated change names, and scope archived-task failures to PR-touched changes.

## Impact

- All enabled `.github/workflows/ci-*` and `.gitea/workflows/ci-*` workflow definitions.
- New standard-library regression tests for the inline workflow scripts.
- No new runtime dependency; validation continues to use the pinned OpenSpec CLI.
