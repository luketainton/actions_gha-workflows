# Tasks

## 1. Tighten CI archive association and result handling

- [x] 1.1 Update all enabled GitHub and Gitea CI scripts to associate each changed spec capability with a matching archived delta, accept exact or date-prefixed archive names, and filter validated archive findings to PR-touched IDs; verify the embedded scripts remain identical across all CI variants.
- [x] 1.2 Add standard-library regression tests that execute the workflow scripts for unrelated archives, missing capability deltas, date-prefixed IDs, active changes, and relevant incomplete archives; verify with `python3 -m unittest discover -s tests -p 'test_openspec_ci.py'`.

## 2. Integration verification

- [x] 2.1 Run GitHub and Gitea workflow lint, the regression suite, `openspec validate --all`, and `openspec validate --archived`; verify all pass and the workflow files retain their existing enabled/disabled scope.
