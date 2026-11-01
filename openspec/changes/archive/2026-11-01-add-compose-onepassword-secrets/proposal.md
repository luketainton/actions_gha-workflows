# Proposal

## Why

Compose callers currently store application secret values directly in Actions.
Allow callers to replace those values with 1Password references while retaining
the existing DC_* names and deployment behavior.

## What Changes

- Add optional 1Password loading, disabled by default, before generating .env.
- Resolve effective DC_* references after applying secret-over-variable precedence.
- Default to ONEPASSWORD_SERVICE_ACCOUNT_TOKEN and allow another inherited token secret by name.
- Use the configure and load-secrets actions at v5.0.1 and document caller setup.
- Record regression coverage and verification limits with the completed change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `compose-deployment`: Optional reference resolution before generating the private deployment environment, including dry-run preparation.

## Impact

Affects .gitea/workflows/docker-compose-deploy.yml, its caller documentation,
Compose deployment specification, and tests. Enabled callers need a service
account with vault access, connectivity to 1Password, and a Node.js 24 capable
runner. Existing callers remain unchanged. This record completes the OpenSpec
artifacts for the implementation already submitted in Gitea PR #140; it does not
claim a live authenticated deployment has been run.
