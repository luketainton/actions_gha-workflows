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
