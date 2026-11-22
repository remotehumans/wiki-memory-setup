#!/usr/bin/env python3
"""Report validation, unresolved exceptions, recent activity, and Git state."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


RESERVED_DIRS = {"raw", "tools", "reports"}


def run(root: Path, *command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def knowledge_dirs(root: Path) -> list[Path]:
    return [
        path
        for path in sorted(root.iterdir())
        if path.is_dir() and path.name not in RESERVED_DIRS and not path.name.startswith((".", "_"))
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero for failed validation or unresolved exceptions")
    args = parser.parse_args()
    root = Path(args.repo).expanduser().resolve()

    area_counts: dict[str, int] = {}
    pages: list[str] = []
    for directory in knowledge_dirs(root):
        area_pages = [
            path.relative_to(root).as_posix()
            for path in sorted(directory.rglob("*.md"))
            if path.name not in {"index.md", "log.md"}
        ]
        area_counts[directory.name] = len(area_pages)
        pages.extend(area_pages)

    unresolved_dir = root / "_inbox" / "unresolved"
    unresolved = [
        path.relative_to(root).as_posix()
        for path in sorted(unresolved_dir.rglob("*"))
        if path.is_file() and path.name != ".gitkeep"
    ] if unresolved_dir.exists() else []

    raw_dir = root / "raw"
    raw_sources = [
        path.relative_to(root).as_posix()
        for path in sorted(raw_dir.rglob("*"))
        if path.is_file() and path.name != ".gitkeep"
    ] if raw_dir.exists() else []

    log_path = root / "log.md"
    recent_log: list[str] = []
    last_log_date = None
    last_semantic_lint: dict[str, str | None] | None = None
    if log_path.exists():
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        headings = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", log_text, re.MULTILINE)
        last_log_date = max(headings) if headings else None
        current_date = None
        dated_entries: list[tuple[str, int, str]] = []
        semantic_lints: list[tuple[str, int, str]] = []
        for sequence, line in enumerate(log_text.splitlines()):
            heading = re.fullmatch(r"##\s+(\d{4}-\d{2}-\d{2})\s*", line)
            if heading:
                current_date = heading.group(1)
            elif line.startswith("* "):
                dated_entries.append((current_date or "", sequence, line.strip()))
                if "**Lint**" in line:
                    semantic_lints.append((current_date or "", sequence, line.strip()))
        recent_log = [entry for _, _, entry in sorted(dated_entries, reverse=True)[:5]]
        if semantic_lints:
            lint_date, _, lint_entry = max(semantic_lints)
            last_semantic_lint = {"date": lint_date or None, "entry": lint_entry}

    validation = {"status": "not run", "summary": "local validator missing"}
    validator = root / "tools" / "validate_llm_wiki.py"
    if validator.exists():
        result = run(root, "python3", str(validator), str(root), "--strict")
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        validation = {
            "status": "pass" if result.returncode == 0 else "fail",
            "summary": lines[-1] if lines else result.stderr.strip() or "validator returned no output",
        }

    git_state: dict[str, object] = {"enabled": (root / ".git").exists()}
    if git_state["enabled"]:
        branch = run(root, "git", "branch", "--show-current").stdout.strip()
        changes = [line for line in run(root, "git", "status", "--porcelain").stdout.splitlines() if line]
        git_state.update({"branch": branch or "detached", "clean": not changes, "changed_files": len(changes)})

    report = {
        "repo": str(root),
        "knowledge_areas": area_counts,
        "maintained_pages": len(pages),
        "raw_sources": len(raw_sources),
        "unresolved": unresolved,
        "last_log_date": last_log_date,
        "recent_log": recent_log,
        "validation": validation,
        "git": git_state,
        "last_semantic_lint": last_semantic_lint,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Wiki: {root}")
        print(f"Maintained pages: {len(pages)} across {len(area_counts)} knowledge areas")
        print(f"Raw sources retained: {len(raw_sources)}")
        print(f"Unresolved exceptions: {len(unresolved)}")
        for path in unresolved:
            print(f"  UNRESOLVED: {path}")
        print(f"Last update: {last_log_date or 'none'}")
        for entry in recent_log:
            print(f"  {entry}")
        print(f"Validation: {validation['status']} ({validation['summary']})")
        if git_state["enabled"]:
            state = "clean" if git_state.get("clean") else f"{git_state.get('changed_files')} changed file(s)"
            print(f"Git: {git_state.get('branch')} — {state}")
        else:
            print("Git: disabled")
        if last_semantic_lint:
            print(f"Semantic lint: last recorded {last_semantic_lint['date']} — {last_semantic_lint['entry']}")
        else:
            print("Semantic lint: none recorded")

    unhealthy = bool(unresolved or validation["status"] == "fail")
    raise SystemExit(1 if args.strict and unhealthy else 0)


if __name__ == "__main__":
    main()
