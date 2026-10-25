import json
import os
from pathlib import Path
import subprocess
import tempfile
import shutil
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = (
    [shutil.which("docker-compose")]
    if shutil.which("docker-compose")
    else ["docker", "compose"]
)


def run_python(script, env, cwd):
    workflow = (ROOT / ".gitea/workflows/docker-compose-deploy.yml").read_text()
    step = (
        "Resolve project paths and commands"
        if script == "resolve.py"
        else "Create Compose environment file"
    )
    block = workflow.split('      - name: "[ON RUNNER] ' + step + '"', 1)[1]
    source = block.split("python3 - <<'PYCODE'\n", 1)[1].split("          PYCODE", 1)[0]
    path = Path(cwd) / script
    path.write_text(textwrap.dedent(source))
    return subprocess.run(
        ["python3", str(path)],
        env={**os.environ, **env},
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def outputs(path):
    lines = path.read_text().splitlines()
    result = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if "<<" in line:
            key, marker = line.split("<<", 1)
            end = lines.index(marker, index + 1)
            result[key] = "\n".join(lines[index + 1 : end])
            index = end + 1
        else:
            key, value = line.split("=", 1)
            result[key] = value
            index += 1
    return result


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cwd = Path(self.temp.name)
        self.out = self.cwd / "output"
        self.env = {
            "PROJECT_NAME": "test",
            "PROJECT_DIRECTORY": "",
            "PROJECT_ROOT": "",
            "DATA_DIRECTORY": "",
            "DATA_ROOT": "/docker",
            "DEPLOY_USERNAME": "deploy",
            "SSH_AUTH": "key",
            "SSH_CREDENTIAL": "dummy-key",
            "DOCKER_EXECUTABLE": "docker",
            "CREATE_DATA_DIRECTORY": "false",
            "FORCE_RECREATE": "true",
            "REMOVE_ORPHANS": "true",
            "GITHUB_OUTPUT": str(self.out),
        }

    def resolve(self):
        result = run_python("resolve.py", self.env, self.cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        return outputs(self.out)

    def test_ds1_preserves_paths_and_flags(self):
        result = self.resolve()
        self.assertEqual(result["project_folder"], "/home/deploy/test")
        self.assertEqual(result["data_folder"], "/docker/test")
        self.assertIn(
            "docker compose --env-file .env up --detach --force-recreate --remove-orphans",
            result["deploy_script"],
        )
        self.assertNotIn("mkdir -p -- /docker/test", result["prepare_script"])

    def test_nas_overrides(self):
        self.env.update(
            PROJECT_ROOT="/volume1/docker/ACTIVE",
            DATA_ROOT="/volume1/docker/DATA",
            DOCKER_EXECUTABLE="/usr/local/bin/docker",
            SSH_AUTH="password",
            CREATE_DATA_DIRECTORY="true",
        )
        result = self.resolve()
        self.assertEqual(result["project_folder"], "/volume1/docker/ACTIVE/test")
        self.assertEqual(result["data_folder"], "/volume1/docker/DATA/test")
        self.assertIn("/usr/local/bin/docker compose", result["deploy_script"])
        self.assertIn("mkdir -p -- /volume1/docker/DATA/test", result["prepare_script"])

    def test_legacy_call_defaults(self):
        self.env.update(FORCE_RECREATE="false", REMOVE_ORPHANS="false")
        self.assertTrue(self.resolve()["deploy_script"].endswith("up --detach"))

    def test_reject_dangerous_or_mistyped_paths(self):
        for path in (
            "/",
            "/home/deploy",
            "/docker/test/../test",
            "/home/deploy/other",
            "/tmp/test\nrm -rf /",
        ):
            with self.subTest(path=path):
                self.env["PROJECT_DIRECTORY"] = path
                self.assertNotEqual(
                    run_python("resolve.py", self.env, self.cwd).returncode, 0
                )

    def test_reject_data_within_deployment_tree(self):
        for path in ("/home/deploy/test", "/home/deploy/test/data"):
            self.env["DATA_DIRECTORY"] = path
            self.assertNotEqual(
                run_python("resolve.py", self.env, self.cwd).returncode, 0
            )

    def test_reject_missing_auth_and_shell_in_executable(self):
        self.env["SSH_CREDENTIAL"] = ""
        self.assertNotEqual(run_python("resolve.py", self.env, self.cwd).returncode, 0)
        self.env.update(
            SSH_CREDENTIAL="dummy", DOCKER_EXECUTABLE="docker; touch INJECTED"
        )
        self.assertNotEqual(run_python("resolve.py", self.env, self.cwd).returncode, 0)

    def test_failed_down_preserves_files_success_preserves_data(self):
        project = self.cwd / "test"
        data = self.cwd / "data"
        project.mkdir()
        data.mkdir()
        sentinel = data / "keep"
        sentinel.touch()
        docker = self.cwd / "docker"
        docker.write_text('#!/bin/sh\nexit "${MOCK_STATUS:-0}"\n')
        docker.chmod(0o755)
        self.env.update(
            PROJECT_DIRECTORY=str(project),
            DATA_DIRECTORY=str(data),
            DOCKER_EXECUTABLE=str(docker),
        )
        script = self.resolve()["remove_script"]
        result = subprocess.run(
            ["sh", "-c", script],
            env={**os.environ, "MOCK_STATUS": "42"},
            capture_output=True,
        )
        self.assertEqual(result.returncode, 42)
        self.assertTrue(project.exists())
        result = subprocess.run(["sh", "-c", script], capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(project.exists())
        self.assertTrue(sentinel.exists())

    def test_dotenv_roundtrip_and_secret_precedence(self):
        value = "quote'\" slash\\ newline\n$HOME ${missing} $$ unicode café"
        env = {
            "ALLVARS": json.dumps({"DC_VALUE": "variable", "UNRELATED": "omit"}),
            "ALLSECRETS": json.dumps({"DC_VALUE": value, "DEPLOY_SSHKEY": "omit"}),
            "PROJECT_NAME": "test",
            "PROJECT_FOLDER": "/home/deploy/test",
            "PROJECT_DATA_FOLDER": "/docker/test",
        }
        result = run_python("dotenv.py", env, self.cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual((self.cwd / ".env").stat().st_mode & 0o777, 0o600)
        (self.cwd / "compose.yaml").write_text(
            "services:\n  app:\n    image: alpine\n    env_file: .env\n"
        )
        result = subprocess.run(
            [*COMPOSE, "config", "--format", "json"],
            cwd=self.cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        parsed = json.loads(result.stdout)["services"]["app"]["environment"]
        # Compose escapes dollars when rendering a reusable configuration.
        self.assertEqual(parsed["DC_VALUE"], value.replace("$", "$$"))
        environment = subprocess.run(
            [*COMPOSE, "config", "--environment"],
            cwd=self.cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("DC_VALUE=" + value + "\n", environment.stdout)
        self.assertEqual(parsed["PROJECT_DATA_FOLDER"], "/docker/test")
        self.assertNotIn("DEPLOY_SSHKEY", parsed)
        self.assertNotIn("UNRELATED", parsed)

    def test_dry_run_gates_all_remote_actions(self):
        for name in ("deploy", "remove"):
            workflow = (
                ROOT / ".gitea/workflows" / f"docker-compose-{name}.yml"
            ).read_text()
            for step in workflow.split("      - name: ")[1:]:
                if "uses: appleboy/" in step:
                    self.assertIn("if: ${{ !inputs.dry-run }}", step)
                if "uses: https://git.tainton.uk/actions/pushover-action" in step:
                    condition = next(
                        line
                        for line in step.splitlines()
                        if line.strip().startswith("if:")
                    )
                    self.assertIn("!inputs.dry-run", condition)


if __name__ == "__main__":
    unittest.main()
