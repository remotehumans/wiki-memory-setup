#!/usr/bin/env python3
"""Create a personal and business LLM memory wiki."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path


MEMORY_AREAS = [
    ("people", "People and durable relationship context"),
    ("organisations", "Companies, clients, partners, suppliers, venues, and communities"),
    ("projects", "Durable project state, milestones, and open questions"),
    ("offerings", "Products, services, programmes, pricing, and positioning"),
    ("events", "Notable meetings, sessions, and events"),
    ("places", "Locations, venues, and local knowledge"),
    ("decisions", "Durable decisions and their rationale"),
    ("preferences", "Stable working, communication, and personal preferences"),
    ("observations", "Durable signals and things noticed before conclusions harden"),
    ("questions", "Durable open questions worth revisiting"),
    ("ideas", "Possibilities and testable hypotheses not yet committed"),
    ("lessons", "Reusable learning grounded in experience and outcomes"),
    ("playbooks", "Reusable processes, templates, and ways of working"),
    ("concepts", "Ideas, frameworks, themes, and cross-source synthesis"),
    ("source_material", "Selected full notes or wording preserved as maintained source records"),
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def area_lines() -> str:
    return "\n".join(f"- `{name}/`: {description}." for name, description in MEMORY_AREAS)


def schema(name: str, purpose: str) -> str:
    return f"""# {name} Wiki Schema

## Purpose

{purpose}

## Architecture

- `raw/` optionally preserves original source documents when exact context or traceability has durable value. Existing files are immutable.
{area_lines()}
- `index.md` catalogs every maintained page by area.
- `log.md` is an append-only operations timeline.
- `entities.yaml` stores canonical names and aliases to prevent duplicate entities.
- `_inbox/unresolved/` is an exception queue only for ambiguity, contradiction, sensitivity, or failed validation requiring judgement.
- `tools/` contains local status and validation commands.
- This file defines the schema. Keep `AGENTS.md` and `CLAUDE.md` byte-identical.

## Client Commands

- Normal agent use: automatically file durable knowledge into the correct maintained pages when it surfaces.
- “Add this to my wiki”: explicitly ingest supplied text, a file, or an accessible document; preserve the original only when useful.
- “What does my wiki know about X?”: read `index.md`, search maintained pages, and answer with citations.
- “Check my wiki”: run `python3 tools/wiki_status.py .`, then inspect contradictions, duplicate entities, stale claims, missing links, and weak synthesis; log the semantic lint.
- “What changed recently?”: summarize `log.md` and recent Git changes.

The client should not need to manage files or run tools personally.

## Entity and Ontology Management

- Search `entities.yaml`, page titles, aliases, and existing content before creating a person, organisation, project, offering, event, or place.
- Merge new facts into the canonical page and update aliases in `entities.yaml` when needed. Never create a duplicate page merely because a name is written differently.
- Use the existing starter areas whenever they fit.
- Add a top-level category only for a durable, recurring page type that does not fit an existing area. Do not add a folder for one unusual item.
- When adding a category, describe it here, make the same edit in both schema files, add it to `index.md`, and log the change.
- Do not move or rename established pages without updating all links and explaining the migration in `log.md`.

## Multi-Agent Coordination

When several agents share this wiki through Git, pull/rebase before ingest, protect unrelated changes, make one coherent direct-to-`main` commit, and push after validation. Never overwrite another agent's work.

## Page Conventions

- Apply Open Knowledge Format v0.1 page and linking conventions to the maintained knowledge areas.
- Give every maintained Markdown page YAML frontmatter with a non-empty `type`. Add `title`, `description`, `resource`, `tags`, and `timestamp` when useful.
- Keep root `index.md` and `log.md` as reserved navigation/history files, not concept pages.
- Keep one main entity, concept, source record, or synthesis per page. Use stable kebab-case filenames.
- Use standard bundle-root Markdown links such as `[Person](/people/person.md)`.
- Put supporting links to immutable files under `# Citations` at the bottom of maintained pages.
- Keep raw originals in `raw/`. Use `source_material/` only when selected full notes, exact wording, or source context deserves a maintained page with metadata and links.
- Integrate new evidence into existing synthesis. Record contradictions, confidence changes, and unresolved questions.

## Ingest

1. Detect durable knowledge during normal agent use or read an explicit source fully; then read `index.md`, search maintained pages, and resolve named entities.
2. Ask the client only when ambiguity, contradiction, sensitivity, or failed validation prevents safe filing.
3. Create or update all affected pages across the appropriate areas; do not stop at an isolated source summary.
4. Add raw-source citations and cross-links. Update `entities.yaml` for new canonical entities or aliases.
5. Update `index.md`; for a material change, append one concise `* **Ingest**: ...` entry under today's heading in `log.md`.
6. Run `python3 tools/validate_llm_wiki.py . --strict`.
7. Commit the coherent change directly on `main` and push when Git is enabled.
8. Report knowledge filed, key pages changed, validation/commit state, and only genuine unresolved exceptions.

## Query

Read `index.md`, search relevant areas, inspect cited raw sources when needed, and answer with citations. File valuable new synthesis into the appropriate maintained page when agreed, then update the index if needed and log `* **Query**: Title`.

## Lint

Check duplicate entities, contradictions, stale claims, orphan pages, broken links, uncited claims, missing concepts, weak synthesis, index drift, entity-registry drift, schema drift, and `_inbox/unresolved/`. Fix safe issues directly and log material passes as `* **Lint**: Scope`.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, help="New wiki destination")
    parser.add_argument("--name", required=True, help="Wiki name")
    parser.add_argument("--purpose", required=True, help="What the wiki should help the client understand")
    parser.add_argument("--remote", help="Existing private Git remote URL")
    parser.add_argument("--no-git", action="store_true", help="Do not initialize Git")
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if root.exists() and not root.is_dir():
        fail(f"destination exists and is not a directory: {root}")
    if root.exists() and any(root.iterdir()):
        fail(f"destination is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)

    today = dt.date.today().isoformat()
    (root / "raw" / "assets").mkdir(parents=True)
    write(root / "raw" / ".gitkeep", "")
    write(root / "raw" / "assets" / ".gitkeep", "")
    for area, _ in MEMORY_AREAS:
        write(root / area / ".gitkeep", "")
    write(root / "_inbox" / "unresolved" / ".gitkeep", "")

    router = schema(args.name, args.purpose)
    write(root / "AGENTS.md", router)
    write(root / "CLAUDE.md", router)
    write(root / ".gitignore", ".DS_Store\n.obsidian/workspace*.json\n*.swp\n")
    write(
        root / "entities.yaml",
        """# Canonical entity registry. Example:\n# people:\n#   jane-doe:\n#     name: Jane Doe\n#     aka: [Jane]\npeople: {}\norganisations: {}\nprojects: {}\nofferings: {}\nevents: {}\nplaces: {}""",
    )
    write(
        root / "START_HERE.md",
        f"""# Using {args.name}

Talk to an AI agent that has access to this folder. You do not need to organise the files yourself.

## Four useful commands

- **Normal conversation** — the agent automatically files durable decisions, observations, lessons, preferences, relationships, and project changes into the right pages.
- **“Add this to my wiki”** — paste text, attach a file, or provide an accessible link. The agent updates every relevant page, cross-links the knowledge, checks the result, and tells you what changed.
- **“What does my wiki know about …?”** — ask across everything already integrated.
- **“Check my wiki”** — validate the structure and have the agent inspect meaning and connections for problems.
- **“What changed recently?”** — get a plain-language summary of recent updates.

## How the wiki organises itself

It starts with visible areas for people, organisations, projects, offerings, events, places, decisions, preferences, observations, questions, ideas, lessons, playbooks, concepts, and selected source material. The agent creates and updates pages inside them, merges duplicate knowledge, and maintains links and indexes. If a genuinely new recurring type of knowledge emerges, the agent may add a category and document the change.

The wiki does not trawl email, chats, drives, or other accounts without permission. But knowledge shared with an authorised agent is filed automatically when durable. `_inbox/unresolved/` is only for the rare item the agent cannot safely classify or reconcile.

The AI agent performs the ingest itself; there is no separate ingest application for you to operate.

## Purpose

{args.purpose}
""",
    )

    area_index = "\n".join(f"- [{name.replace('_', ' ').title()}]({name}/) — {description}." for name, description in MEMORY_AREAS)
    write(
        root / "index.md",
        f"""---
okf_version: "0.1"
---

# {args.name}

{args.purpose}

## Knowledge areas

{area_index}

## Pages

No maintained pages yet. Add every created page here under its knowledge area.
""",
    )
    write(
        root / "log.md",
        f"""# Wiki Update Log

## {today}
* **Initialization**: Created the personal and business memory structure, index, log, entity registry, and agent schema.
""",
    )

    script_dir = Path(__file__).resolve().parent
    for tool_name in ("wiki_status.py", "validate_llm_wiki.py"):
        source = script_dir / tool_name
        if not source.exists():
            fail(f"missing bundled tool: {source}")
        destination = root / "tools" / tool_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        destination.chmod(0o755)

    if not args.no_git:
        if not shutil.which("git"):
            fail("git not found; rerun with --no-git or install Git")
        git(root, "init", "-b", "main")
        if args.remote:
            git(root, "remote", "add", "origin", args.remote)
        git(root, "add", ".")
        commit = git(root, "commit", "-m", "Initialize personal business memory wiki", check=False)
        if commit.returncode != 0:
            print("WARNING: Git initialized but initial commit failed; configure Git identity and commit manually.", file=sys.stderr)

    print(f"Created personal and business memory wiki: {root}")
    print('Next: give an agent a source and say "Add this to my wiki". See START_HERE.md.')
    if args.remote:
        print("Remote configured but not pushed. Verify privacy, then push explicitly.")


if __name__ == "__main__":
    main()
