## Context

The Gitea workflow already runs the Python checks and produces a test coverage artifact.

## Decisions

Run Qualor as a container action at the end of the existing job using the versioned scanner image. Use a clean checkout so changes from preparing lint and test dependencies cannot affect the scan. Use the PR head for same-repository pull request scans. The caller supplies a scoped project token.
