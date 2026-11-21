## ADDED Requirements

### Requirement: Optional Qualor analysis on Gitea
The Gitea Unified Python CI workflow SHALL run Qualor as a step in the existing
CI job when enabled for branch pushes, manual branch runs, and pull requests
originating in the same repository.
It SHALL authenticate with a caller-supplied project analysis token.

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
