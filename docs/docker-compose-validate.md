# Docker Compose validation

`docker-compose-validate.yml` checks out the caller's repository and runs
`docker compose config --quiet`. Exit code 0 passes the job; any nonzero exit
code fails it. The resolved configuration is not printed. Set `runtime: podman`
to run `podman compose config --quiet` instead.

| Optional input | Type | Default | Effect |
| --- | --- | --- | --- |
| `runtime` | string | `docker` | Select `docker` or `podman`; other values fail validation. |
| `legacy` | boolean | `false` | Use `docker-compose` instead of `docker compose`; ignored when `runtime: podman`. |
| `manifest-file` | string | `''` | Pass a single manifest path with `-f`; empty uses Compose's normal file discovery. |
| `env-file-content` | string | `''` | Write validation-only content to `.env` after checkout; empty leaves any existing file unchanged. |

Gitea caller:

```yaml
name: Validate Compose
on: [push, pull_request]
jobs:
  validate:
    uses: actions/gha-workflows/.gitea/workflows/docker-compose-validate.yml@main
    with:
      runtime: docker
      legacy: false
      manifest-file: compose.yaml
```

For GitHub, use the corresponding `.github/workflows/docker-compose-validate.yml`
path in the repository hosted on GitHub. All inputs can be omitted. To select
the legacy executable and a custom path, set `legacy: true` and, for example,
`manifest-file: deploy/docker-compose.yml`.

For Podman, set `runtime: podman`. This always invokes `podman compose`, even
when `legacy: true`.

When a manifest references an untracked `.env`, provide non-sensitive validation
values through `env-file-content`:

```yaml
      env-file-content: |
        PROJECT_NAME=test
```

Nonempty content replaces `.env` in the checked-out repository for this job.
For a manifest in a subdirectory, this still writes `.env` at the repository
root; any additional referenced environment files must already be available.
The content is written literally without shell evaluation or printing it.

The runner must have the selected Compose executable installed. Podman also
requires an installed Compose provider supporting `config --quiet`, because
`podman compose` delegates to that provider. This workflow does not start
containers. Normal Compose
interpolation and referenced environment files still apply: required values
and files must be available on the runner (for example, using `env-file-content`
for non-sensitive validation values). It does not generate deployment
environment files or automatically forward caller secrets or variables.
