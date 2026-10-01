# Tasks

## 1. Implement conditional detection and validation

- [x] 1.1 Add a conditional OpenSpec path-detection, CLI installation, and validation step to every enabled GitHub CI workflow; verify non-OpenSpec PR changes skip the step and OpenSpec PR changes invoke it.
- [x] 1.2 Add equivalent platform-aware handling to every enabled Gitea CI workflow; verify both platforms derive the PR change set correctly and fail clearly when changed OpenSpec files cannot be classified.
- [x] 1.3 Require each PR-touched OpenSpec change to be archived and have completed tasks before its CI job passes; verify active changes and incomplete archived changes fail while complete archived changes pass.

## 2. Integration verification

- [x] 2.1 Review the final workflow inventory to confirm disabled workflows and non-CI workflows are unchanged, and verify the OpenSpec validation gate appears in every enabled GitHub and Gitea CI definition.
- [x] 2.2 Validate the change artifacts with `openspec validate --all` and verify the CI diff and platform expressions are syntactically valid using the repository's available workflow validation tooling.
