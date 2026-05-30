# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
#     "requests",
# ]
# ///
"""Sync Claude Code skills from GitHub repos into the local skills directory."""

import io
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

import requests
import yaml


def load_manifest(path: str = "skills.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def download_repo_tarball(repo: str, ref: str = "main") -> bytes:
    """Download a GitHub repo as a tarball."""
    url = f"https://github.com/{repo}/archive/refs/heads/{ref}.tar.gz"
    print(f"  Downloading {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def extract_skills_from_tarball(
    tarball: bytes, skill_names: list[str] | None
) -> dict[str, Path]:
    """Extract skill directories from a tarball. Returns {skill_name: temp_path}."""
    tmpdir = Path(tempfile.mkdtemp())
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tar:
        tar.extractall(tmpdir, filter="data")

    # Find the extracted root (usually repo-name-ref/)
    roots = list(tmpdir.iterdir())
    if len(roots) == 1 and roots[0].is_dir():
        repo_root = roots[0]
    else:
        repo_root = tmpdir

    # Look for skills in common locations
    skills_dir = None
    for candidate in ["skills", "."]:
        p = repo_root / candidate
        if p.is_dir():
            skills_dir = p
            break

    if skills_dir is None:
        print("  Warning: no skills directory found in repo")
        return {}

    results = {}
    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue
        # Check if it looks like a skill (has SKILL.md)
        if not (item / "SKILL.md").exists():
            continue
        if skill_names is None or item.name in skill_names:
            results[item.name] = item

    return results


def sync_skill(skill_name: str, source_path: Path, target_dir: Path) -> None:
    """Copy a skill directory to the target, replacing if it exists."""
    target = target_dir / skill_name
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source_path, target)
    print(f"  Synced: {skill_name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync Claude Code skills from GitHub")
    parser.add_argument(
        "--manifest", default="skills.yaml", help="Path to skills manifest"
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    skills_dir = Path(manifest["skills_dir"]).expanduser()
    skills_dir.mkdir(parents=True, exist_ok=True)

    for source in manifest["sources"]:
        repo = source["repo"]
        ref = source.get("ref", "main")
        wanted = source.get("skills")  # None means all

        print(f"\nSource: {repo} ({ref})")
        if wanted:
            print(f"  Wanted: {', '.join(wanted)}")

        tarball = download_repo_tarball(repo, ref)
        # Extract all skills to check for missing ones, then filter
        all_extracted = extract_skills_from_tarball(tarball, None)
        extracted = (
            {k: v for k, v in all_extracted.items() if k in wanted}
            if wanted
            else all_extracted
        )

        if wanted:
            missing = set(wanted) - set(all_extracted.keys())
            if missing:
                print(f"  Warning: skills not found: {missing}")

        if not extracted:
            print("  No matching skills found")
            continue

        for name, path in extracted.items():
            if args.dry_run:
                print(f"  Would sync: {name}")
            else:
                sync_skill(name, path, skills_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
