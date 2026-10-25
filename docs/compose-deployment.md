# Shared Compose deployment and removal

The Gitea reusable workflows `docker-compose-deploy.yml` and
`docker-compose-remove.yml` centralise SSH operations while callers retain their
triggers, path filters and any prerequisite jobs.

Callers use `secrets: inherit` so the called workflow receives the caller's
organisation/repository deployment credentials and application `DC_*` secrets.
The caller's variables provide the organisation directory roots and `DC_*`
configuration. The deployment `.env` contains only `DC_*` values and the three
`PROJECT_*` values; secrets override variables with the same name.

| Input | Default | Meaning |
| --- | --- | --- |
| `project-directory` | empty | Full deployment path; otherwise `ACTIVE_PROJECT_DIR/<repo>` or `/home/<DEPLOY_USERNAME>/<repo>`. |
| `data-directory` | empty | Full data path; otherwise `ACTIVE_PROJECT_DATA_DIR/<repo>` or `PROJECT_DATA_DIR/<repo>`. |
| `docker-executable` | `docker` | One Docker executable name/path on the remote host. NAS callers can use `/usr/local/bin/docker`. |
| `ssh-auth` | `key` | `key` uses `DEPLOY_SSHKEY`; `password` uses `DEPLOY_PASSWORD`. Only the selected credential is sent to SSH/SCP. |
| `notifications` | `true` | Pushover start and completion notifications. Completion runs even after failure. |
| `dry-run` | `false` | Prepare paths/commands and, for deployment, check out the repo and generate `.env`. Skip all SSH, SCP and notifications. |
| `source-files` (deploy) | `./compose.yaml,./.env` | Comma-separated paths passed to SCP. Include extra application/configuration files here. |
| `force-recreate` (deploy) | `false` | Append `--force-recreate` to `up --detach`. |
| `remove-orphans` (deploy) | `false` | Append `--remove-orphans` to `up --detach`. |
| `create-data-directory` (deploy) | `false` | Create the data directory on the remote host as well as the deployment directory. |
| `approval-required` (deploy) | `false` | After pulling images, require an approval before any pre-deployment script or Compose startup. Denial or timeout fails deployment. |
| `approval-approvers` (deploy) | `luke` | Comma-separated permitted approvers; one approval is required. |
| `approval-title` / `approval-body` (deploy) | Generic deployment message | Customise the approval issue title and instructions. |
| `build` (deploy) | `false` | Append `--build` to Compose startup. |
| `replace-project-directory` (deploy) | `false` | Remove the validated deployment directory before recreating it and uploading files. Persistent data must remain outside it. |
| `before-upload` (deploy) | empty | Trusted host shell commands, run inside the deployment directory before uploading files. |
| `before-deploy` (deploy) | empty | Trusted host shell commands, run inside the deployment directory after image pull/approval and before Compose startup. |

Required secrets are `DEPLOY_HOST`, `DEPLOY_USERNAME` and `DEPLOY_PORT`, plus the
credential selected by `ssh-auth`. Notifications require `PUSHOVER_APP_TOKEN`
and `PUSHOVER_USER_TOKEN`. `dry-run` still validates that an SSH credential is
present but never connects to the host. It generates a credential-bearing `.env`
inside the job workspace; this file must never be logged or uploaded as an artifact.

Deployment uploads files, always runs `docker compose pull` on the host, optionally
waits for approval, runs `before-deploy`, then invokes
`docker compose --env-file .env up --detach` with the chosen flags. A failed pull
stops deployment before approval or startup. Build-only services without an
image are left for the build step by Compose. Approval uses the existing manual
approval action with the caller's API URL and token, one required approval,
denial as failure and a 60-minute timeout. Dry-run skips pull and approval along
with all other host operations; local validation uses the runner's Docker CLI,
independently of the remote `docker-executable` setting.

Removal invokes `down`, then deletes the deployment directory only if
shutdown succeeds. Neither operation adds `--volumes`. Removal does not archive
or delete the persistent data directory. Paths must be absolute and contain no
traversal or newlines; the deployment directory must end with the repository
name, and persistent data must be outside that deployment tree.

Example DS1 deployment caller:

```yaml
jobs:
  deploy:
    uses: actions/gha-workflows/.gitea/workflows/docker-compose-deploy.yml@main
    with:
      data-directory: ${{ vars.ACTIVE_PROJECT_DATA_DIR }}/${{ github.event.repository.name }}
      source-files: ./compose.yaml,./app.py,./.env
      force-recreate: true
      remove-orphans: true
    secrets: inherit
```

Keep application tests as a preceding job with `needs: verify` on the caller.
Keep removal under `workflow_dispatch`. Do not put a removal call on PR or push
events unless `dry-run: true` is explicitly set for a deliberate integration test.
For n8n, set `approval-required: true` and supply the instruction to stop running
workflows in `approval-body`. Yaqcp uses `replace-project-directory`,
`before-deploy: ./util/generate_index.sh` and `build: true`. CrowdSec uses
`before-upload` to replace its copied acquis.d configuration directory. These
scripts are trusted deployment configuration: they execute only on normal
deployment, never during dry-run. No explicit directory inputs are needed when
the organisation defaults already describe the existing paths.

Run `python3 -m unittest discover -s tests -p test_compose_deployment.py` to check
path resolution, flags, literal environment values, dry-run gates, and removal
failure handling. The environment round-trip test requires a Compose CLI.
