## Why

Gitea Python repos need a shared way to send quality and security analysis to Qualor.

## What Changes

Add an opt-in Qualor step to the existing job with a caller-supplied project token. The step reports branch and same-repository pull request scans.

## Capabilities

### Modified Capabilities

- `python-unified-ci` adds optional Qualor analysis to the Gitea workflow.

## Impact

Affects the Gitea reusable workflow and its caller documentation. All callers can opt in independently.
