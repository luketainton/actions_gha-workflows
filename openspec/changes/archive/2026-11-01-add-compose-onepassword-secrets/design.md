# Design

## Context

The reusable Gitea deploy workflow builds a private .env from inherited DC_*
variables and secrets. See proposal.md for motivation. The implementation in
PR #140 precedes this change record; these artifacts describe that implementation.

## Goals / Non-Goals

**Goals:** Preserve caller names, ordinary values, secret precedence and literal
encoding while adding optional reference resolution before upload.

**Non-Goals:** Resolve deployment SSH credentials or notifications from
1Password, change removal, provision service accounts, or run a production deploy.

## Decisions

### Reuse effective DC_* values

Merge caller variables followed by secrets, then select only values starting
with op://. A separate reference-map input would duplicate existing caller
configuration. An opt-in boolean keeps existing callers compatible.

### Use both official actions at v5.0.1

Run configure followed by load-secrets with export-env enabled, after checkout
and before .env generation. Use explicit GitHub URLs for Gitea action resolution.
Pass the selected references as a JSON environment mapping. Skip both actions
when the mapping is empty; fail early if enabled without a token.

The linked guide showed v4, but the upstream latest release checked during
implementation was v5.0.1. Both action manifests use Node.js 24.

### Select authentication by inherited secret name

Default onepassword-token-secret to ONEPASSWORD_SERVICE_ACCOUNT_TOKEN. Resolve
the same indexed secret for validation and configure. This supports secrets:
inherit without exposing a token through a plain workflow input; explicit secret
callers can map a custom token to the declared default secret instead.

### Reuse the private environment writer

For selected references only, replace the source value with the exported runner
environment value. Fail if the value is missing or still equals the reference.
Continue using the existing dollar escaping, JSON quoting and mode 0600.
Unrelated runner environment values and the service account token are excluded.

### Resolve during enabled dry runs

Dry runs prepare the real .env for local Compose validation. They therefore
read 1Password when enabled, while existing gates continue to prevent all host
operations and notifications.

## Risks / Trade-offs

- Configure exports the token to later job steps; use a service account scoped to the required vaults.
- Upstream action masking protects loaded values in logs; the generated .env still contains credentials and must remain private.
- Gitea runner execution and live authentication are not verified locally; validate the opt-in path with a caller dry run before normal deployment.
- Existing full-suite workflow inventory and unrelated strict-spec warnings are recorded separately from focused validation.

## Migration Plan

Merge the reusable workflow, replace selected DC_* values with op:// references,
ensure token inheritance, and enable onepassword-enabled. A caller can select a
custom inherited token by name. To roll back, restore direct DC_* secret values
and disable loading together; disabling alone leaves reference strings literal.
