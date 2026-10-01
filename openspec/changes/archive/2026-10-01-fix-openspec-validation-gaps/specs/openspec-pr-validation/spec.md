# Spec Delta

## MODIFIED Requirements

### Requirement: OpenSpec changes must be archived before CI passes

For a pull request that modifies OpenSpec-managed changes, CI SHALL fail if a changed OpenSpec change remains active, if a changed main spec capability has no matching delta in an archived change included in the pull request, or if a PR-touched archived change has incomplete tasks. CI SHALL associate active change names with either an exact archive directory name or the corresponding date-prefixed archive directory name. Incomplete archived changes outside the pull request's changed archive directories SHALL NOT fail this pull request. CI SHALL pass this check only when the associated change is archived and complete.

#### Scenario: Change is archived and complete
- **WHEN** a pull request changes an OpenSpec change that is archived with all tasks complete
- **THEN** the OpenSpec validation checks pass

#### Scenario: Change remains active
- **WHEN** a pull request changes an OpenSpec change that remains in the active changes directory
- **THEN** the OpenSpec validation gate fails and reports that the change must be archived

#### Scenario: Archived change has incomplete tasks
- **WHEN** a pull request changes an archived OpenSpec change whose task list is incomplete
- **THEN** the OpenSpec validation gate fails

#### Scenario: Changed main spec has no matching archived delta
- **WHEN** a pull request changes a main spec capability and includes only an unrelated archived change
- **THEN** the OpenSpec validation gate fails and identifies the capability without a matching archived delta

#### Scenario: Change name already has a date prefix
- **WHEN** a pull request archives a change whose name already begins with a date prefix
- **THEN** CI recognizes the exact archive directory name and accepts the association

#### Scenario: Unrelated archived task is incomplete
- **WHEN** a pull request changes a complete archived change while a different archived change has incomplete tasks
- **THEN** the unrelated archived task finding does not fail this pull request
