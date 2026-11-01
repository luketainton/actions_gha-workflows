# Tasks

## 1. Optional retrieval and authentication

- [x] 1.1 Add the disabled-by-default switch, inherited token-name selector, and both official actions; verify defaults, shared token expression, action versions, order and conditional gates with source review and actionlint.
- [x] 1.2 Select effective DC_* references after secret precedence; verify reference filtering, ordinary-value precedence, empty references and missing authentication with the regression tests.

## 2. Compose environment integration

- [x] 2.1 Substitute resolved values before private .env generation and fail on unresolved values; verify literal encoding, disabled behavior, mode 0600 and token exclusion with regression tests and preserve existing dry-run host gates.
- [x] 2.2 Document caller opt-in, token override and dry-run behavior; verify docs/compose-deployment.md agrees with the workflow and the capability delta is already present in the main spec.

## 3. Integration verification

- [x] 3.1 Run the 14 Compose deployment tests, actionlint, strict change/spec validation and whitespace checks; record requirement/scenario mapping and live-runner limitations in verification.md.

## Workflow follow-up

- Archive the completed change after confirming main-spec synchronization.
- Validate the archive and update Gitea PR #140 through LabMCP-Gitea.
