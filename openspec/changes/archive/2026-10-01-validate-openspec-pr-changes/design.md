# Design

## Context

The repository provides reusable workflows rather than PR-triggered workflows. The enabled Python and Docker CI workflows in `.github/workflows` and `.gitea/workflows` check out repositories with full history. OpenSpec is configured with the spec-driven schema, and the CLI offers an `--archived` validation mode for checking archived changes' task completion. Disabled workflow directories are outside scope.

## Goals / Non-Goals

**Goals:**
- Apply the same conditional OpenSpec gate to enabled Gitea and GitHub CI workflows that can run for pull requests.
- Detect OpenSpec-managed files from the caller's PR change set, install the CLI only when needed, validate changed content, and reject active or incomplete changes.
- Preserve normal CI behavior when no OpenSpec-managed paths changed.

**Non-Goals:**
- Enable or modify disabled workflows.
- Change the repository's OpenSpec schema or archive format.
- Add OpenSpec checks to release, deployment, or other non-CI workflows.

## Decisions

- Keep the check within reusable CI jobs and derive the PR base/head comparison from the calling workflow context, with platform-specific handling for GitHub and Gitea. The reusable definitions are the common integration point; the implementation must account for the caller providing usable PR metadata and fail clearly if OpenSpec paths are changed but the comparison cannot be established.
- Trigger on OpenSpec-managed content such as active or archived change artifacts and durable specs. Use the PR diff to determine the affected change directories, and reject a touched active change directory because the PR's work has not been archived.
- For relevant PRs, run OpenSpec validation on affected content and the CLI's archived-completion check. Scope validation where supported so unrelated archived work does not make a PR fail; confirm the CLI's name/path behavior during implementation.
- Use a pinned or otherwise reproducible OpenSpec CLI installation method that works on both GitHub-hosted and Gitea-hosted Ubuntu runners.

## Risks / Trade-offs

- Reusable workflows may not expose equivalent event fields on both platforms. → Add platform-specific detection using each platform's caller context and verify behavior with representative PR metadata.
- A broad archived validation may fail due to unrelated historical changes. → Prefer validating only archived change identifiers found in the PR diff, while retaining the check that those identifiers are not still active.
- CLI installation adds time to PRs that touch OpenSpec. → Keep installation conditional on the detected changed paths.
- PR diff metadata may be absent for manual or non-PR calls. → Skip only when there are no OpenSpec changes to evaluate; report a clear failure if relevant changes cannot be classified.
