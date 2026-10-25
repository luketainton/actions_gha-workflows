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

The runner must have the selected Compose executable installed. Podman also
requires an installed Compose provider supporting `config --quiet`, because
`podman compose` delegates to that provider. This workflow does not start
containers. Normal Compose
interpolation and referenced environment files still apply: required values
and files must be available on the runner (for example, a checked-in `.env`
containing non-sensitive validation values). It does not generate deployment
environment files or automatically forward caller secrets or variables.
