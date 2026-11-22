#!/usr/bin/env python3
"""Validate a personal and business Markdown memory wiki."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


MEMORY_AREAS = [
    "people",
    "organisations",
    "projects",
    "offerings",
    "events",
    "places",
    "decisions",
    "preferences",
    "observations",
    "questions",
    "ideas",
    "lessons",
    "playbooks",
    "concepts",
    "source_material",
]
RESERVED_DIRS = {"raw", "tools"}
REQUIRED = [
    "raw",
    "index.md",
    "log.md",
    "entities.yaml",
    "AGENTS.md",
    "CLAUDE.md",
    "START_HERE.md",
    "_inbox/unresolved",
    "tools/wiki_status.py",
    "tools/validate_llm_wiki.py",
    *MEMORY_AREAS,
]


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def knowledge_dirs(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.iterdir())
        if path.is_dir() and path.name not in RESERVED_DIRS and not path.name.startswith((".", "_"))
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()
    root = Path(args.repo).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for required in REQUIRED:
        if not (root / required).exists():
            errors.append(f"missing {required}")
    if (root / "AGENTS.md").exists() and (root / "CLAUDE.md").exists():
        if (root / "AGENTS.md").read_bytes() != (root / "CLAUDE.md").read_bytes():
            errors.append("AGENTS.md and CLAUDE.md differ")

    index_path = root / "index.md"
    log_path = root / "log.md"
    index_text = index_path.read_text(encoding="utf-8", errors="replace") if index_path.exists() else ""
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    if index_text.startswith("---\n"):
        index_meta = frontmatter(index_text)
        if index_meta is None:
            errors.append("index.md: invalid frontmatter")
        elif set(index_meta) != {"okf_version"}:
            errors.append("index.md: frontmatter may contain only okf_version")
        elif index_meta.get("okf_version", "").strip("\"'") != "0.1":
            warnings.append("index.md: unexpected OKF version")
    else:
        errors.append("index.md: missing OKF frontmatter")
    if log_text.startswith("---\n"):
        errors.append("log.md: reserved log must not have frontmatter")
    for heading in re.findall(r"^##\s+(.+)$", log_text, re.MULTILINE):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", heading.strip()):
            errors.append(f"log.md: date heading must be YYYY-MM-DD: {heading}")

    for directory in knowledge_dirs(root):
        for path in sorted(directory.rglob("*.md")):
            rel = path.relative_to(root)
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.name in {"index.md", "log.md"}:
                continue
            meta = frontmatter(text)
            if meta is None:
                errors.append(f"{rel}: missing or invalid frontmatter")
                continue
            if not meta.get("type"):
                errors.append(f"{rel}: missing non-empty type")
            if meta.get("timestamp") and not re.match(r"^\d{4}-\d{2}-\d{2}T", meta["timestamp"]):
                warnings.append(f"{rel}: timestamp should be ISO 8601")
            if rel.as_posix() not in index_text and path.stem not in index_text:
                warnings.append(f"{rel}: not listed in index.md")

            for target in re.findall(r"\[[^]]+\]\(((?:\.\./)+raw/[^)]+)\)", text):
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    warnings.append(f"{rel}: broken raw citation {target}")

    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=MDR", "HEAD", "--", "raw/"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        for changed in result.stdout.splitlines():
            errors.append(f"existing raw source modified, deleted, or renamed: {changed}")

    status = "PASS" if not errors and (not args.strict or not warnings) else "FAIL"
    print(f"{status}: {root}")
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    raise SystemExit(1 if errors or (args.strict and warnings) else 0)


if __name__ == "__main__":
    main()
