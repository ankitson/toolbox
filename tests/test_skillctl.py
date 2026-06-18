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

        self.assertIn("0 external skills, 0 routers, 1 custom skills", result.stdout)

    def test_check_accepts_empty_tree(self) -> None:
        (self.root / "skills.toml").write_text("# no skills yet\n")

        result = self.run_command("check")

        self.assertIn("0 external skills, 0 routers, 0 custom skills", result.stdout)

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

    def test_add_glob_star_creates_multiple_skills(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha\n",
                "skills/beta/SKILL.md": "# Beta\n",
                "skills/alpha/extra.md": "extra\n",
            }
        )

        self.run_command("add", "glob-all", str(repo), "skills/*")

        alpha = self.root / "skills" / "alpha"
        beta = self.root / "skills" / "beta"
        self.assertTrue((alpha / "SKILL.md").exists())
        self.assertTrue((beta / "SKILL.md").exists())
        self.assertEqual((alpha / ".skillctl-source").read_text().strip(), "glob-all")
        self.assertEqual((beta / ".skillctl-source").read_text().strip(), "glob-all")

    def test_sync_glob_updates_existing_skills(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha before\n",
                "skills/beta/SKILL.md": "# Beta\n",
            }
        )
        self.run_command("add", "glob-all", str(repo), "skills/*")
        self.commit_file(repo, "skills/alpha/SKILL.md", "# Alpha after\n")

        self.run_command("sync", "glob-all")

        self.assertEqual(
            (self.root / "skills" / "alpha" / "SKILL.md").read_text(),
            "# Alpha after\n",
        )

    def test_sync_glob_removes_stale_skills(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha\n",
                "skills/beta/SKILL.md": "# Beta\n",
            }
        )
        self.run_command("add", "glob-all", str(repo), "skills/*")

        # Remove beta from the repo
        self.git(repo, "rm", "-r", "skills/beta")
        self.git(repo, "commit", "--quiet", "-m", "remove beta")

        self.run_command("sync", "glob-all")

        self.assertTrue((self.root / "skills" / "alpha").exists())
        self.assertFalse((self.root / "skills" / "beta").exists())

    def test_glob_brace_expansion_selects_subset(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha\n",
                "skills/beta/SKILL.md": "# Beta\n",
                "skills/gamma/SKILL.md": "# Gamma\n",
            }
        )

        self.run_command("add", "subset", str(repo), "skills/{alpha,gamma}")

        self.assertTrue((self.root / "skills" / "alpha" / "SKILL.md").exists())
        self.assertTrue((self.root / "skills" / "gamma" / "SKILL.md").exists())
        self.assertFalse((self.root / "skills" / "beta").exists())
        self.assertEqual(
            (self.root / "skills" / "alpha" / ".skillctl-source").read_text().strip(),
            "subset",
        )
        self.assertEqual(
            (self.root / "skills" / "gamma" / ".skillctl-source").read_text().strip(),
            "subset",
        )

    def test_list_shows_glob_source(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha\n",
                "skills/beta/SKILL.md": "# Beta\n",
            }
        )
        self.run_command("add", "glob-all", str(repo), "skills/*")

        result = self.run_command("list")

        self.assertIn("glob", result.stdout)
        self.assertIn("glob-all", result.stdout)
        # Individual skill names should NOT appear as separate "custom" rows
        lines = result.stdout.splitlines()
        custom_lines = [l for l in lines if "custom" in l]
        for line in custom_lines:
            self.assertNotIn("alpha", line)
            self.assertNotIn("beta", line)

    def test_check_glob_source_fails_before_sync(self) -> None:
        # Write a skills.toml with a glob entry manually (no sync)
        (self.root / "skills.toml").write_text(
            '[skills.glob-source]\nrepo = "owner/repo"\npath = "skills/*"\n'
        )

        result = self.run_command("check", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("run skillctl sync", result.stderr)

    def test_check_glob_source_passes_after_sync(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha\n",
                "skills/beta/SKILL.md": "# Beta\n",
            }
        )
        self.run_command("add", "glob-all", str(repo), "skills/*")

        result = self.run_command("check")

        self.assertEqual(result.returncode, 0)
        self.assertIn("glob sources", result.stdout)

    def test_router_from_source_group_copies_reference_skills(self) -> None:
        alpha = self.root / "skills" / "alpha"
        beta = self.root / "skills" / "beta"
        alpha.mkdir(parents=True)
        beta.mkdir(parents=True)
        (alpha / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: Handle alpha workflows.\n"
            "---\n"
            "\n"
            "# Alpha\n"
        )
        (alpha / "reference.md").write_text("alpha reference\n")
        (alpha / ".skillctl-source").write_text("group-one")
        (beta / "SKILL.md").write_text(
            "---\n"
            "name: beta\n"
            "description: Handle beta workflows.\n"
            "---\n"
            "\n"
            "# Beta\n"
        )
        (beta / ".skillctl-source").write_text("group-one")

        self.run_command(
            "router",
            "bundle-router",
            "--source-group",
            "group-one",
            "--description",
            "Route bundle requests.",
        )

        router = self.root / "skills" / "bundle-router"
        skill_text = (router / "SKILL.md").read_text()
        self.assertIn('name: "bundle-router"', skill_text)
        self.assertIn('description: "Route bundle requests."', skill_text)
        self.assertIn("Generated from source group `group-one`.", skill_text)
        self.assertIn("| Handle alpha workflows. | `references/alpha/instructions.md` |", skill_text)
        self.assertIn("| Handle beta workflows. | `references/beta/instructions.md` |", skill_text)
        self.assertEqual(
            (router / "references" / "alpha" / "reference.md").read_text(),
            "alpha reference\n",
        )
        self.assertTrue((router / "references" / "alpha" / "instructions.md").exists())
        self.assertFalse((router / "references" / "alpha" / "SKILL.md").exists())
        self.assertFalse((router / "references" / "alpha" / ".skillctl-source").exists())

    def test_router_from_skills_sh_group_copies_reference_skills(self) -> None:
        alpha = self.root / "skills" / "alpha"
        beta = self.root / "skills" / "beta"
        alpha.mkdir(parents=True)
        beta.mkdir(parents=True)
        (alpha / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: Handle alpha workflows.\n"
            "---\n"
            "\n"
            "# Alpha\n"
        )
        (beta / "SKILL.md").write_text(
            "---\n"
            "name: beta\n"
            "description: Handle beta workflows.\n"
            "---\n"
            "\n"
            "# Beta\n"
        )
        (self.root / "skills.sh.json").write_text(
            "{\n"
            '  "$schema": "https://skills.sh/schemas/skills.sh.schema.json",\n'
            '  "notGrouped": "bottom",\n'
            '  "groupings": [\n'
            "    {\n"
            '      "title": "Bundle Group",\n'
            '      "description": "Skills for grouped routing.",\n'
            '      "skills": ["alpha", "beta"]\n'
            "    }\n"
            "  ]\n"
            "}\n"
        )

        self.run_command("router", "bundle-router", "--group", "Bundle Group")

        router = self.root / "skills" / "bundle-router"
        skill_text = (router / "SKILL.md").read_text()
        self.assertIn('description: "Route Bundle Group requests. Skills for grouped routing."', skill_text)
        self.assertIn("Generated from skills.sh.json grouping `Bundle Group`.", skill_text)
        self.assertIn("| Handle alpha workflows. | `references/alpha/instructions.md` |", skill_text)
        self.assertIn("| Handle beta workflows. | `references/beta/instructions.md` |", skill_text)

    def test_router_absorb_removes_top_level_sources_and_preserves_glob(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha\n",
                "skills/beta/SKILL.md": "# Beta\n",
            }
        )
        self.run_command("add", "glob-all", str(repo), "skills/*")
        (self.root / "skills.sh.json").write_text(
            '{"groupings": [{"title": "Bundle Group", "skills": ["alpha", "beta"]}]}\n'
        )

        self.run_command("router", "bundle-router", "--group", "Bundle Group", "--absorb")

        router = self.root / "skills" / "bundle-router"
        self.assertTrue((router / "references" / "alpha" / "instructions.md").exists())
        self.assertFalse((self.root / "skills" / "alpha").exists())
        self.assertFalse((self.root / "skills" / "beta").exists())
        self.assertIn("[skills.glob-all]", (self.root / "skills.toml").read_text())

    def test_sync_registered_router_absorbs_by_default_and_generates_skills_sh(self) -> None:
        repo = self.make_repo(
            {
                "skills/alpha/SKILL.md": "# Alpha\n",
                "skills/beta/SKILL.md": "# Beta\n",
            }
        )
        (self.root / "skills.toml").write_text(
            '[routers.bundle-router]\n'
            'title = "Bundle Group"\n'
            'description = "Skills for grouped routing."\n'
            f'absorbs = ["{repo}:skills/alpha", "{repo}:skills/beta"]\n'
        )

        self.run_command("sync")

        router = self.root / "skills" / "bundle-router"
        self.assertTrue((router / "SKILL.md").exists())
        self.assertTrue((router / "references" / "alpha" / "instructions.md").exists())
        self.assertTrue((router / "references" / "beta" / "instructions.md").exists())
        self.assertFalse((self.root / "skills" / "alpha").exists())
        self.assertFalse((self.root / "skills" / "beta").exists())
        generated = (self.root / "skills.sh.json").read_text()
        self.assertIn('"title": "Bundle Group"', generated)
        self.assertIn('"alpha"', generated)
        self.assertIn('"beta"', generated)

    def test_router_can_regenerate_from_absorbed_references(self) -> None:
        alpha = self.root / "skills" / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: Handle alpha workflows.\n"
            "---\n"
            "\n"
            "# Alpha\n"
        )
        (self.root / "skills.sh.json").write_text(
            '{"groupings": [{"title": "Bundle Group", "skills": ["alpha"]}]}\n'
        )
        self.run_command("router", "bundle-router", "--group", "Bundle Group", "--absorb")

        self.run_command(
            "router",
            "bundle-router",
            "--group",
            "Bundle Group",
            "--overwrite",
            "--absorb",
            "--description",
            "Updated description.",
        )

        router = self.root / "skills" / "bundle-router"
        skill_text = (router / "SKILL.md").read_text()
        self.assertIn('description: "Updated description."', skill_text)
        self.assertIn("| Handle alpha workflows. | `references/alpha/instructions.md` |", skill_text)
        self.assertFalse((self.root / "skills" / "alpha").exists())

    def test_router_fails_when_skills_sh_group_is_missing(self) -> None:
        (self.root / "skills.sh.json").write_text(
            '{"groupings": [{"title": "Other", "skills": ["alpha"]}]}\n'
        )

        result = self.run_command(
            "router",
            "bundle-router",
            "--group",
            "Missing",
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("grouping not found", result.stderr)

    def test_router_accepts_explicit_skill_names(self) -> None:
        alpha = self.root / "skills" / "alpha"
        alpha.mkdir(parents=True)
        (alpha / "SKILL.md").write_text("# Alpha\n")

        self.run_command("router", "single-router", "alpha")

        router = self.root / "skills" / "single-router"
        skill_text = (router / "SKILL.md").read_text()
        self.assertIn("| Use the alpha workflow. | `references/alpha/instructions.md` |", skill_text)
        self.assertTrue((router / "references" / "alpha" / "instructions.md").exists())
        self.assertFalse((router / "references" / "alpha" / "SKILL.md").exists())

    def test_router_refuses_to_overwrite_without_flag(self) -> None:
        alpha = self.root / "skills" / "alpha"
        router = self.root / "skills" / "bundle-router"
        alpha.mkdir(parents=True)
        router.mkdir(parents=True)
        (alpha / "SKILL.md").write_text("# Alpha\n")
        (router / "SKILL.md").write_text("# Existing\n")

        result = self.run_command("router", "bundle-router", "alpha", check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual((router / "SKILL.md").read_text(), "# Existing\n")


if __name__ == "__main__":
    unittest.main()
