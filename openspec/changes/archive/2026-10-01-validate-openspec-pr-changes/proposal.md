# Proposal

## Why

Pull requests can modify OpenSpec-managed work without CI checking that the change is valid or complete. A conditional CI gate will catch invalid artifacts and ensure work is archived before it can pass.

## What Changes

- Add conditional OpenSpec change detection, CLI installation, validation, and archived-completion checks to enabled Gitea and GitHub CI workflows.
- Skip the OpenSpec checks for pull requests that do not contain OpenSpec-managed changes and leave disabled workflows untouched.

## Capabilities

### New Capabilities

- `openspec-pr-validation`: CI validates OpenSpec-managed pull request changes and requires their changes to be archived with all tasks complete.

### Modified Capabilities

None.

## Impact

- Affected reusable CI workflow definitions under `.github/workflows` and `.gitea/workflows`.
- Adds conditional installation and invocation of the OpenSpec CLI to applicable CI runs.
- Workflow callers must expose sufficient pull request context for change detection; exact event and diff handling will be designed for GitHub and Gitea compatibility.
