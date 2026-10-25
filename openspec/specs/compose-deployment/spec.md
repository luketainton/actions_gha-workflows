# Shared Compose Deployment Specification

## Purpose

Share deployment and removal mechanics across DS1 and NAS repositories while
preserving caller-specific triggers, prerequisites, project paths and files.

## Requirements

### Requirement: Pull before deployment
Deployment SHALL always pull images after uploading the selected manifest and
environment, before requesting approval, running pre-deployment commands, or
starting containers. Pull failure SHALL stop deployment.

#### Scenario: Standard deployment
- **WHEN** a normal deployment reaches the uploaded manifest
- **THEN** it runs Compose pull before any deployment approval or startup

### Requirement: Optional deployment approval
Deployment SHALL expose boolean `approval-required` defaulting to false, and
SHALL support caller-specific approvers and approval instructions.

#### Scenario: Approval required
- **WHEN** approval-required is true
- **THEN** deployment waits after image pull and continues only after an authorised approval; denial or timeout fails deployment

#### Scenario: Approval omitted
- **WHEN** approval-required is false or omitted
- **THEN** deployment continues from pull to startup without requesting approval

### Requirement: Preserve specialised deployment steps
Deployment SHALL provide opt-in build and deployment-directory replacement,
and trusted before-upload and before-deploy host scripts. Persistent data
SHALL remain outside the replaceable deployment directory.

#### Scenario: Generated application build
- **WHEN** a caller enables directory replacement, a generation script and build
- **THEN** replacement precedes upload and generation precedes Compose startup with build enabled

#### Scenario: Dry-run of specialised deployment
- **WHEN** dry-run is true
- **THEN** no cleanup, image pull, approval request, custom host script or build executes

### Requirement: Caller context and deployment configuration
The workflows SHALL resolve paths from explicit inputs or caller organisation
variables and SHALL use only the selected SSH authentication method.

#### Scenario: DS1 caller
- **WHEN** no project override or organisation project root is supplied
- **THEN** the deployment directory is `/home/<DEPLOY_USERNAME>/<repository>`

#### Scenario: NAS caller
- **WHEN** the caller has `ACTIVE_PROJECT_DIR` and `PROJECT_DATA_DIR`
- **THEN** deployment and data paths are derived from those roots and the repository name

### Requirement: Compose environment generation
Deployment SHALL write inherited caller `DC_*` variables and secrets plus
resolved `PROJECT_NAME`, `PROJECT_FOLDER` and `PROJECT_DATA_FOLDER` to a private
`.env` file without printing its values. Secrets SHALL override same-name variables.

#### Scenario: Literal application secret
- **WHEN** a secret contains quotes, backslashes, newlines or dollar signs
- **THEN** Compose receives the original value without shell evaluation or unintended interpolation

### Requirement: Preserve deployment choices
Deployment SHALL accept an upload file list and independent force-recreate and
remove-orphans flags, both defaulting to false.

#### Scenario: Test repository pilot
- **WHEN** test opts into both flags and uploads compose.yaml, app.py and .env
- **THEN** the shared deployment uses those files and flags after the caller's verification job succeeds

### Requirement: Bounded removal
Removal SHALL run Compose down before deleting the deployment directory, SHALL
stop on failure, and SHALL NOT delete persistent data or request volume deletion.
Deployment paths SHALL be absolute, traversal-free, and end with the repository
name. Persistent data SHALL be outside the deployment directory tree.

#### Scenario: Shutdown failure
- **WHEN** Compose down returns nonzero
- **THEN** removal fails and leaves the deployment directory intact

### Requirement: Dry-run verification
Both workflows SHALL expose a dry-run option defaulting to false.

#### Scenario: Dry run selected
- **WHEN** dry-run is true
- **THEN** no SSH, SCP, notification, deployment or removal action executes
