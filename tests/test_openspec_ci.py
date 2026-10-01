"""Regression tests for the inline OpenSpec validation scripts in reusable workflows."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIRS = (ROOT / ".github/workflows", ROOT / ".gitea/workflows")
STEP_NAMES = (
    "Detect OpenSpec-managed PR changes",
    "Validate OpenSpec PR changes",
)


def workflow_files() -> list[Path]:
    return sorted(
        path
        for directory in WORKFLOW_DIRS
        for path in directory.glob("ci-*")
        if path.suffix in {".yml", ".yaml"}
    )


def extract_script(path: Path, step_name: str) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    marker = f"      - name: {step_name}"
    start = lines.index(marker)
    run = lines.index("        run: |", start)
    body = []
    for line in lines[run + 1 :]:
        if line == "          PYCODE":
            break
        body.append(line[10:] if line.startswith("          ") else line)
    else:
        raise AssertionError(f"{path}: missing PYCODE terminator for {step_name}")

    wrapper = "\n".join(body)
    command = "python3 - <<'PYCODE'\n"
    if command not in wrapper:
        raise AssertionError(f"{path}: missing Python heredoc for {step_name}")
    return textwrap.dedent(wrapper.split(command, 1)[1])


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def commit_all(repo: Path, message: str) -> str:
    git(repo, "add", "-f", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def write_file(repo: Path, relative_path: str, content: str) -> None:
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def spec_text(description: str = "The system SHALL return a stable result.") -> str:
    return (
        "# Capability A Specification\n\n"
        "## Purpose\n\n"
        "This capability provides a stable result for its callers.\n\n"
        "## Requirements\n\n"
        "### Requirement: Stable output\n"
        f"{description}\n\n"
        "#### Scenario: Normal operation\n"
        "- **WHEN** the capability is called\n"
        "- **THEN** it returns a stable result\n"
    )


class OpenSpecWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflows = workflow_files()
        if len(cls.workflows) != 13:
            raise AssertionError(f"expected 13 enabled CI workflows, found {len(cls.workflows)}")
        cls.scripts = {
            path: tuple(extract_script(path, step) for step in STEP_NAMES)
            for path in cls.workflows
        }
        cls.reference_scripts = cls.scripts[ROOT / ".github/workflows/ci-python-unified.yml"]

    def init_git(self, repo: Path) -> None:
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "workflow-test@example.invalid")
        git(repo, "config", "user.name", "Workflow test")
        git(repo, "config", "commit.gpgsign", "false")

    def init_repo(self, repo: Path, *, active_name: str | None = None) -> str:
        self.init_git(repo)
        write_file(repo, "openspec/config.yaml", "schema: spec-driven\n")
        if active_name:
            write_file(
                repo,
                f"openspec/changes/{active_name}/tasks.md",
                "# Tasks\n\n- [ ] 1.1 Finish this change\n",
            )
        return commit_all(repo, "base")

    def event(self, temp: Path, base: str, head: str) -> Path:
        event = temp / "event.json"
        event.write_text(
            json.dumps({"pull_request": {"base": {"sha": base}, "head": {"sha": head}}}),
            encoding="utf-8",
        )
        return event

    def run_detection(self, repo: Path, temp: Path, base: str, head: str) -> str:
        event_path = self.event(temp, base, head)
        output_path = temp / "github-output"
        output_path.write_text("", encoding="utf-8")
        result = subprocess.run(
            ["python3", "-c", self.reference_scripts[0]],
            cwd=repo,
            env=os.environ | {"EVENT_PATH": str(event_path), "GITHUB_OUTPUT": str(output_path)},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return output_path.read_text(encoding="utf-8").strip().split("=", 1)[1]

    def run_validation(
        self,
        repo: Path,
        temp: Path,
        base: str,
        head: str,
        findings: list[dict[str, object]] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        event_path = self.event(temp, base, head)
        fake_bin = temp / "bin"
        fake_bin.mkdir(exist_ok=True)
        log = temp / "openspec-args.jsonl"
        report_path = temp / "archive-report.json"
        report_path.write_text(
            json.dumps(
                {
                    "report": {"kind": "validation-findings", "scope": "archived"},
                    "itemFindings": findings or [],
                }
            ),
            encoding="utf-8",
        )
        fake_cli = fake_bin / "openspec"
        fake_cli.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "with open(os.environ['FAKE_OPENSPEC_LOG'], 'a', encoding='utf-8') as log:\n"
            "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
            "if '--archived' in sys.argv:\n"
            "    print(open(os.environ['FAKE_ARCHIVE_REPORT'], encoding='utf-8').read())\n"
            "    sys.exit(int(os.environ.get('FAKE_ARCHIVE_EXIT', '0')))\n",
            encoding="utf-8",
        )
        fake_cli.chmod(0o755)
        return subprocess.run(
            ["python3", "-c", self.reference_scripts[1]],
            cwd=repo,
            env=os.environ
            | {
                "EVENT_PATH": str(event_path),
                "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
                "FAKE_OPENSPEC_LOG": str(log),
                "FAKE_ARCHIVE_REPORT": str(report_path),
                "FAKE_ARCHIVE_EXIT": "1" if findings else "0",
            },
            capture_output=True,
            text=True,
        )

    def test_gate_scripts_are_identical_in_all_enabled_ci_workflows(self) -> None:
        for path, scripts in self.scripts.items():
            with self.subTest(workflow=path.relative_to(ROOT)):
                self.assertEqual(scripts, self.reference_scripts)

    def test_non_openspec_pr_skips_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            repo.mkdir()
            base = self.init_repo(repo)
            write_file(repo, "README.md", "Documentation-only update.\n")
            head = commit_all(repo, "docs only")
            self.assertEqual(self.run_detection(repo, temp, base, head), "false")

    def test_changed_spec_requires_a_matching_archived_delta(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            repo.mkdir()
            self.init_git(repo)
            write_file(repo, "openspec/config.yaml", "schema: spec-driven\n")
            write_file(repo, "openspec/specs/capability-a/spec.md", spec_text())
            base = commit_all(repo, "base spec")
            write_file(repo, "openspec/specs/capability-a/spec.md", spec_text("The system SHALL return a changed result."))
            write_file(
                repo,
                "openspec/changes/archive/2026-10-01-unrelated/tasks.md",
                "# Tasks\n\n- [x] 1.1 Complete unrelated change\n",
            )
            head = commit_all(repo, "change spec and unrelated archive")
            self.assertEqual(self.run_detection(repo, temp, base, head), "true")
            result = self.run_validation(repo, temp, base, head)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("capability 'capability-a'", result.stderr)
            self.assertIn("matching archived delta", result.stderr)

    def test_matching_archived_delta_and_spec_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            repo.mkdir()
            base = self.init_repo(repo, active_name="demo-change")
            archive = "openspec/changes/archive/2026-10-01-demo-change"
            active_tasks = repo / "openspec/changes/demo-change/tasks.md"
            active_tasks.unlink()
            active_tasks.parent.rmdir()
            write_file(repo, f"{archive}/tasks.md", "# Tasks\n\n- [x] 1.1 Finish this change\n")
            write_file(repo, f"{archive}/specs/capability-a/spec.md", "# Spec Delta\n")
            write_file(repo, "openspec/specs/capability-a/spec.md", spec_text())
            head = commit_all(repo, "archive change with matching spec delta")
            result = self.run_validation(repo, temp, base, head)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            commands = [json.loads(line) for line in (temp / "openspec-args.jsonl").read_text().splitlines()]
            self.assertIn(["validate", "capability-a", "--type", "spec", "--no-interactive"], commands)
            self.assertIn(["validate", "--archived", "--report", "findings", "--json", "--no-interactive"], commands)

    def test_already_date_prefixed_change_name_matches_exact_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            repo.mkdir()
            name = "2026-02-03-demo-change"
            base = self.init_repo(repo, active_name=name)
            archive = repo / "openspec/changes/archive" / name
            archive.mkdir(parents=True)
            active = repo / "openspec/changes" / name
            task_text = (active / "tasks.md").read_text(encoding="utf-8")
            (active / "tasks.md").unlink()
            active.rmdir()
            write_file(repo, f"openspec/changes/archive/{name}/tasks.md", task_text.replace("[ ]", "[x]"))
            head = commit_all(repo, "archive already date-prefixed change")
            result = self.run_validation(repo, temp, base, head)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_unrelated_archive_finding_does_not_fail_pr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            repo.mkdir()
            base = self.init_repo(repo)
            write_file(
                repo,
                "openspec/changes/archive/2026-10-01-touched/tasks.md",
                "# Tasks\n\n- [x] 1.1 Complete touched change\n",
            )
            head = commit_all(repo, "touch complete archive")
            unrelated = {
                "id": "2025-01-01-old-change",
                "type": "change",
                "valid": False,
                "issues": [{"level": "ERROR", "message": "old unchecked task"}],
            }
            result = self.run_validation(repo, temp, base, head, [unrelated])
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_incomplete_touched_archive_fails_pr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            repo.mkdir()
            base = self.init_repo(repo)
            archive_id = "2026-10-01-touched"
            write_file(repo, f"openspec/changes/archive/{archive_id}/tasks.md", "# Tasks\n\n- [ ] 1.1 Unfinished\n")
            head = commit_all(repo, "touch incomplete archive")
            finding = {
                "id": archive_id,
                "type": "change",
                "valid": False,
                "issues": [{"level": "ERROR", "message": "1 incomplete task (0/1 completed)"}],
            }
            result = self.run_validation(repo, temp, base, head, [finding])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PR-touched archived OpenSpec changes are incomplete", result.stderr)

    def test_active_change_still_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            repo = temp / "repo"
            repo.mkdir()
            base = self.init_repo(repo, active_name="active-change")
            write_file(repo, "openspec/changes/active-change/tasks.md", "# Tasks\n\n- [ ] 1.1 Still active\n")
            head = commit_all(repo, "leave change active")
            result = self.run_validation(repo, temp, base, head)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("still active", result.stderr)


if __name__ == "__main__":
    unittest.main()
