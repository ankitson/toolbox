#!/usr/bin/env python3
"""Black-box tests for bin/skillctl."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLCTL = PROJECT_ROOT / "bin" / "skillctl"


class SkillctlTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self.temp = Path(self._tempdir.name)
        self.root = self.temp / "toolbox"
        self.root.mkdir()

    def run_command(
        self,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(SKILLCTL), "--root", str(self.root), *args],
            cwd=PROJECT_ROOT,
            env=self._git_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check and result.returncode:
            self.fail(
                f"skillctl {' '.join(args)} failed with {result.returncode}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        return result

    def git(self, repo: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            env=self._git_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode:
            self.fail(
                f"git {' '.join(args)} failed with {result.returncode}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        return result.stdout.strip()

    def make_repo(self, files: dict[str, str]) -> Path:
        repo = self.temp / f"source-{len(list(self.temp.glob('source-*')))}"
        repo.mkdir()
        self.git(repo, "init", "--quiet", "--initial-branch=main")
        self.git(repo, "config", "user.email", "skillctl-tests@example.invalid")
        self.git(repo, "config", "user.name", "skillctl tests")
        for relative_path, content in files.items():
            target = repo / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        self.git(repo, "add", ".")
        self.git(repo, "commit", "--quiet", "-m", "fixture")
        return repo

    def commit_file(self, repo: Path, relative_path: str, content: str) -> None:
        target = repo / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        self.git(repo, "add", relative_path)
        self.git(repo, "commit", "--quiet", "-m", f"update {relative_path}")

    @staticmethod
    def _git_env() -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_CONFIG_NOSYSTEM": "1",
            }
        )
        return env

    def test_add_copies_subdirectory_and_writes_toml_registry(self) -> None:
        repo = self.make_repo(
            {
                "catalog/example/SKILL.md": "# Example\n",
                "catalog/example/reference.md": "reference material\n",
                "outside.txt": "must not be copied\n",
            }
        )

        self.run_command("add", "example", str(repo), "catalog/example")

        installed = self.root / "skills" / "example"
        self.assertEqual((installed / "SKILL.md").read_text(), "# Example\n")
        self.assertEqual((installed / "reference.md").read_text(), "reference material\n")
        self.assertFalse((installed / "outside.txt").exists())
        registry = (self.root / "skills.toml").read_text()
        self.assertIn("[skills.example]", registry)
        self.assertIn(f'repo = "{repo}"', registry)
        self.assertIn('path = "catalog/example"', registry)

    def test_add_with_repo_only_infers_name_and_standard_skills_path(self) -> None:
        repo = self.make_repo({"skills/agent-browser/SKILL.md": "# Browser\n"})

        self.run_command("add", str(repo))

        installed = self.root / "skills" / repo.name / "SKILL.md"
        self.assertEqual(installed.read_text(), "# Browser\n")
        registry = (self.root / "skills.toml").read_text()
        self.assertIn(f"[skills.{repo.name}]", registry)
        self.assertIn(f'repo = "{repo}"', registry)
        self.assertNotIn("path =", registry)

    def test_add_with_repo_only_uses_single_obvious_skill_folder(self) -> None:
        repo = self.make_repo({"skills/only-skill/SKILL.md": "# Only\n"})

        self.run_command("add", str(repo))

        installed = self.root / "skills" / repo.name / "SKILL.md"
        self.assertEqual(installed.read_text(), "# Only\n")

    def test_add_with_repo_only_fails_when_multiple_skill_folders_are_ambiguous(self) -> None:
        repo = self.make_repo(
            {
                "skills/one/SKILL.md": "# One\n",
                "skills/two/SKILL.md": "# Two\n",
            }
        )

        result = self.run_command("add", str(repo), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("multiple skill folders", result.stderr)

    def test_add_can_select_repeated_files(self) -> None:
        repo = self.make_repo(
            {
                "SKILL.md": "# Selected\n",
                "SCHEMA.md": "schema\n",
                "ignored.md": "ignored\n",
            }
        )

        self.run_command(
            "add", "selected", str(repo), "--file", "SKILL.md", "--file", "SCHEMA.md"
        )

        installed = self.root / "skills" / "selected"
        self.assertEqual((installed / "SKILL.md").read_text(), "# Selected\n")
        self.assertEqual((installed / "SCHEMA.md").read_text(), "schema\n")
        self.assertFalse((installed / "ignored.md").exists())
        registry = (self.root / "skills.toml").read_text()
        self.assertIn('files = ["SKILL.md", "SCHEMA.md"]', registry)

    def test_sync_refreshes_snapshot(self) -> None:
        repo = self.make_repo({"SKILL.md": "# Before\n"})
        self.run_command("add", "refreshable", str(repo))
        self.commit_file(repo, "SKILL.md", "# After\n")

        self.run_command("sync", "refreshable")

        installed = self.root / "skills" / "refreshable" / "SKILL.md"
        self.assertEqual(installed.read_text(), "# After\n")

    def test_list_infers_unregistered_directory_is_custom(self) -> None:
        custom = self.root / "skills" / "authored"
        custom.mkdir(parents=True)
        (custom / "SKILL.md").write_text("# Authored\n")

        result = self.run_command("list")

        self.assertIn("authored", result.stdout)
        self.assertIn("custom", result.stdout)

    def test_check_accepts_unregistered_custom_directory(self) -> None:
        custom = self.root / "skills" / "authored"
        custom.mkdir(parents=True)
        (custom / "SKILL.md").write_text("# Authored\n")
        (self.root / "skills.toml").write_text("# no external sources\n")

        result = self.run_command("check")

        self.assertIn("0 external skills, 1 custom skills", result.stdout)

    def test_check_accepts_empty_tree(self) -> None:
        (self.root / "skills.toml").write_text("# no skills yet\n")

        result = self.run_command("check")

        self.assertIn("0 external skills, 0 custom skills", result.stdout)

    def test_add_refuses_to_overwrite_existing_custom_skill(self) -> None:
        repo = self.make_repo({"SKILL.md": "# Upstream\n"})
        custom = self.root / "skills" / "occupied"
        custom.mkdir(parents=True)
        (custom / "SKILL.md").write_text("# Keep me\n")

        result = self.run_command("add", "occupied", str(repo), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual((custom / "SKILL.md").read_text(), "# Keep me\n")

    def test_add_rejects_source_paths_outside_checkout(self) -> None:
        repo = self.make_repo({"SKILL.md": "# Safe\n"})

        result = self.run_command("add", "escape", str(repo), "..", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escapes", result.stderr)
        self.assertFalse((self.root / "skills" / "escape").exists())

    def test_check_fails_when_registered_snapshot_is_missing(self) -> None:
        (self.root / "skills.toml").write_text(
            '[skills.missing]\nrepo = "owner/repo"\npath = "skills/missing"\n'
        )

        result = self.run_command("check", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run skillctl sync missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
