# Spec Delta

## Purpose

Require CI to check OpenSpec-managed pull request changes for structural validity and archival completeness, so incomplete change artifacts cannot pass the applicable CI job.

## ADDED Requirements

### Requirement: Conditional validation of OpenSpec-managed pull request changes

Enabled GitHub and Gitea CI workflows SHALL detect whether a pull request modifies OpenSpec-managed files. When it does, CI SHALL install the OpenSpec CLI and validate the affected OpenSpec content. Pull requests without OpenSpec-managed changes SHALL skip these checks.

#### Scenario: Pull request changes OpenSpec artifacts
- **WHEN** an enabled CI workflow runs for a pull request that modifies OpenSpec-managed files
- **THEN** the workflow installs OpenSpec and runs validation against the applicable OpenSpec content

#### Scenario: Pull request does not change OpenSpec artifacts
- **WHEN** an enabled CI workflow runs for a pull request that does not modify OpenSpec-managed files
- **THEN** the workflow skips OpenSpec installation and validation

### Requirement: OpenSpec changes must be archived before CI passes

For a pull request that modifies OpenSpec-managed changes, CI SHALL fail if the associated change remains active or its archived tasks are incomplete. CI SHALL pass this check only when the change has been archived and passes archived validation.

#### Scenario: Change is archived and complete
- **WHEN** a pull request changes an OpenSpec change that is archived with all tasks complete
- **THEN** the OpenSpec validation checks pass

#### Scenario: Change remains active
- **WHEN** a pull request changes an OpenSpec change that remains in the active changes directory
- **THEN** the OpenSpec validation gate fails and reports that the change must be archived

#### Scenario: Archived change has incomplete tasks
- **WHEN** a pull request changes an archived OpenSpec change whose task list is incomplete
- **THEN** the OpenSpec validation gate fails
