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

Required secrets are `DEPLOY_HOST`, `DEPLOY_USERNAME` and `DEPLOY_PORT`, plus the
credential selected by `ssh-auth`. Notifications require `PUSHOVER_APP_TOKEN`
and `PUSHOVER_USER_TOKEN`. `dry-run` still validates that an SSH credential is
present but never connects to the host. It generates a credential-bearing `.env`
inside the job workspace; this file must never be logged or uploaded as an artifact.

Deployment invokes `docker compose --env-file .env up --detach` with the chosen
flags. Removal invokes `down`, then deletes the deployment directory only if
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
Flows approvals, remote build/generation steps, custom `.env` quoting needs and
pre-deployment cleanup in specialised repositories are outside this pilot.

Run `python3 -m unittest discover -s tests -p test_compose_deployment.py` to check
path resolution, flags, literal environment values, dry-run gates, and removal
failure handling. The environment round-trip test requires a Compose CLI.
