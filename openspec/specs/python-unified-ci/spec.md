# Python Unified CI Specification

## Purpose

Python Unified CI gives Python projects a reusable workflow for consistent quality checks, including optional static type checking when a calling project enables it.

## Requirements

### Requirement: Optional Pyrefly type checking
Python Unified CI SHALL run Pyrefly when the calling workflow enables the Pyrefly option, using the selected package manager to install and invoke it.

#### Scenario: Pyrefly is enabled
- **WHEN** a calling workflow enables Pyrefly and selects a supported package manager
- **THEN** Python Unified CI installs Pyrefly through that package manager and runs the Pyrefly check as a CI stage

#### Scenario: Pyrefly is disabled
- **WHEN** a calling workflow does not enable Pyrefly
- **THEN** Python Unified CI skips Pyrefly installation and execution

#### Scenario: Pyrefly dependency or check fails
- **WHEN** Pyrefly cannot be installed or its check reports an error
- **THEN** the Pyrefly stage fails and causes the CI job to fail

### Requirement: Optional Qualor analysis on Gitea
The Gitea Unified Python CI workflow SHALL run Qualor as a step in the existing
CI job when enabled for branch pushes, manual branch runs, and pull requests
originating in the same repository.
It SHALL authenticate with a project analysis token resolved through 1Password
from the `QUALOR_TOKEN` entry in the instance-wide
`GLOBAL_ONEPASSWORD_REFERENCES` variable.

#### Scenario: Qualor is enabled for a branch
- **WHEN** a caller enables Qualor and runs CI on a branch push or manual branch run
- **THEN** CI scans the branch and reports to the configured Qualor project

#### Scenario: Qualor is enabled for a same-repository pull request
- **WHEN** a caller enables Qualor for a pull request originating in the same repository
- **THEN** CI scans the pull request head and reports its number and target branch to Qualor

#### Scenario: Qualor is disabled or the event is unsupported
- **WHEN** the caller leaves Qualor disabled or the event is a fork pull request, a pull_request_target event, or a tag
- **THEN** the Qualor step is skipped and the other Python checks run as configured

#### Scenario: An enabled scan fails
- **WHEN** the token is missing, the scanner fails, or the quality gate fails for an enabled scan
- **THEN** the CI job fails

#### Scenario: Qualor needs a project token
- **WHEN** Qualor is enabled for a supported event
- **THEN** CI looks up `QUALOR_TOKEN` in `GLOBAL_ONEPASSWORD_REFERENCES`, resolves that reference through 1Password, and supplies the token to Qualor
- **AND** missing or invalid references and failed secret retrieval fail the CI job
