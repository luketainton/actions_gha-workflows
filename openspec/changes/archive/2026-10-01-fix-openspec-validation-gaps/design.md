# Design

## Context

See proposal.md for the verification findings. The existing gate repeats the same scripts in each enabled CI workflow. OpenSpec 1.13.2 exposes archived task findings as JSON under `itemFindings`, with each archived directory's id, but `--archived` evaluates the entire archive.

## Goals / Non-Goals

**Goals:**
- Require each changed main-spec capability to be represented by a delta spec in an archived change directory touched by the PR.
- Match active change names to both exact archive directory names and date-prefixed archive names.
- Fail only on archived-task findings whose IDs were touched by this PR, while failing closed on CLI errors or malformed output.
- Add standard-library regression tests that execute the actual inline scripts from representative GitHub and Gitea workflows.

**Non-Goals:**
- Change the OpenSpec CLI or its global archived validation behavior.
- Run CI on a live GitHub or Gitea server from this workspace.

## Decisions

- Collect each changed archived directory ID and the capability paths in its changed `specs/` delta files from the PR diff. Every changed main spec capability must appear in at least one such archived delta; this prevents an unrelated archived change from satisfying the gate.
- Associate active change IDs by exact equality first, then by removing a single leading `YYYY-MM-DD-` prefix from the archive directory. Exact equality preserves change names that already have a date prefix.
- Invoke archived validation with `--report findings --json`. Parse and validate the report shape, then fail only when `itemFindings` includes an ID touched by the PR. A command failure without a valid findings report remains a hard failure.
- Keep the existing CLI scan over the full archive because this OpenSpec version has no per-ID archived validation option. Filtering its findings preserves CLI task-progress semantics without allowing unrelated historical failures to block the PR.
- Put regression scenarios in a Python `unittest` module using only the standard library, temporary Git repositories, and a fake CLI executable. Extract and execute the workflow's actual Python heredocs, and assert the common scripts stay in sync across enabled Gitea and GitHub CI variants.

## Risks / Trade-offs

- The CLI still traverses every archived change. → Ignore only validated findings whose IDs are outside the PR-touched archive set; malformed output and process errors without a valid report fail closed.
- Inline script duplication can drift. → Regression tests compare the embedded scripts across every enabled CI workflow.
- Local tests cannot establish live runner behavior. → Validate Gitea and GitHub syntax separately and retain live-runner execution as an external integration check.
