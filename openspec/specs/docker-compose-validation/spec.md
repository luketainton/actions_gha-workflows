# Docker Compose Validation Specification

## Purpose

Provide reusable Gitea and GitHub workflows that validate a calling repository's
Docker Compose configuration without starting containers.

## Requirements

### Requirement: Reusable Compose validation
The workflow SHALL check out the caller repository and run Compose config validation.
It SHALL suppress rendered configuration and preserve the command's exit status.

#### Scenario: Valid configuration
- **WHEN** Compose config exits with status 0
- **THEN** the validation step succeeds

#### Scenario: Invalid configuration
- **WHEN** Compose config exits with a nonzero status
- **THEN** the validation step fails

### Requirement: Optional command selection
The workflow SHALL expose a string `runtime` input defaulting to `docker`,
accepting only `docker` and `podman`, and a boolean `legacy` input defaulting
to false. The workflow SHALL ignore `legacy` when `runtime` is `podman`.

#### Scenario: Modern command selected by default
- **WHEN** `runtime` is omitted or `docker` and `legacy` is omitted or false
- **THEN** validation runs with `docker compose`

#### Scenario: Legacy command selected
- **WHEN** `runtime` is omitted or `docker` and `legacy` is true
- **THEN** validation runs with `docker-compose`

#### Scenario: Podman selected
- **WHEN** `runtime` is `podman`, regardless of the `legacy` value
- **THEN** validation runs with `podman compose`

#### Scenario: Unsupported runtime
- **WHEN** `runtime` is neither `docker` nor `podman`
- **THEN** validation fails with a clear error before invoking Compose

### Requirement: Optional manifest selection
The workflow SHALL expose a string `manifest-file` input defaulting to an empty string.

#### Scenario: Explicit manifest path
- **WHEN** `manifest-file` is nonempty
- **THEN** the path is passed as a single argument following `-f`

#### Scenario: Automatic manifest discovery
- **WHEN** `manifest-file` is empty or omitted
- **THEN** no `-f` option is passed and Compose discovers its configuration normally
