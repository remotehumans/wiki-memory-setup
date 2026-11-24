#!/usr/bin/env python3
"""Create a personal and business LLM memory wiki, or upgrade an existing one."""

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


STORAGE_CHOICES = ["github", "local", "google-drive", "onedrive", "sharepoint", "dropbox", "icloud", "other"]
# Cloud sync folders keep their own version history; a .git folder inside them can be corrupted by the sync client.
SYNCED_STORAGE = {"google-drive", "onedrive", "sharepoint", "dropbox", "icloud"}

CLAUDE_STUB = """@AGENTS.md

This wiki's rules are in AGENTS.md. Read it before working in this folder, and edit rules there only.
"""

PERSON_TEMPLATE = """---
type: person
title: Full Name
description: One line on who they are and why they matter
tags: []
status: active
updated: YYYY-MM-DD
sources: []
aka: []
relationship: How you know them
company:
role:
email:
phone:
linkedin:
location:
channel: Preferred way to contact them
met_at: Event or place you met
met_on: YYYY-MM-DD
last_contact: YYYY-MM-DD
next_touch:
---

# Full Name

## Relationship

Who they are, how you met and what matters to them.

## History

Newest first. One dated line per conversation or contact.

- YYYY-MM-DD: what happened (src: where this came from)

## Open Loops

- Anything promised either way, with a date when there is one.
"""

CRM_VIEW = """---
type: view
title: Follow-ups
description: People with a next_touch date, soonest first. Works in Obsidian with the Dataview plugin.
---

# Follow-ups

Ask your AI "Who do I need to follow up with?" for the same list in any tool.

```dataview
TABLE relationship AS Relationship, company AS Company, next_touch AS "Next touch", last_contact AS "Last contact", channel AS Channel
FROM "people"
WHERE type = "person" AND next_touch
SORT next_touch ASC
```
"""

PEOPLE_SECTION = """## People and Follow-ups

- Create people pages from `_templates/person.md`. Fill only the fields you know; leave the rest blank.
- When the user meets or talks to someone, set `last_contact` to that date and add one dated line under `## History`, newest first.
- When a follow-up is agreed or suggested, set `next_touch` to its date and note what it is under `## Open Loops`.
- When a follow-up is done, clear or move `next_touch` and close the open loop.
- "Who do I need to follow up with?": list people whose `next_touch` is today or earlier, soonest first, with the open loop for each. If nobody is due, say so and name the next person coming up.
- Always write dates as YYYY-MM-DD. Turn "next Tuesday" or "in two weeks" into a real date.
"""


LEGACY_RULES = {
    "- This file defines the schema. Keep `AGENTS.md` and `CLAUDE.md` byte-identical.":
        "- This file, `AGENTS.md`, is the only rulebook. `CLAUDE.md` imports it with `@AGENTS.md`. Edit rules here only.",
    "make the same edit in both schema files, ": "",
}


def storage_section(storage: str) -> str:
    if storage in SYNCED_STORAGE:
        saving = (f"This wiki lives in a {storage} folder. The provider's version history keeps every change, so there is no Git. "
                  "Save edits in place. If a conflict copy appears (a file with a computer or user name added), merge it into the real page and delete the copy.")
    elif storage == "github":
        saving = "This wiki uses Git with a private GitHub repository for history, backup and access from other computers and agents."
    elif storage == "local":
        saving = "This wiki uses Git on this computer for history. Add a private remote later for backup."
    else:
        saving = "Save edits in place. Use Git only if this folder has a `.git` directory."
    return f"""## Storage

{saving}

- When Git is set up (a `.git` folder exists): pull before working, make one coherent commit on `main` after validation, and push when a remote exists.
- When Git is not set up: never create it inside a cloud sync folder.
"""


def area_lines() -> str:
    return "\n".join(f"- `{name}/`: {description}." for name, description in MEMORY_AREAS)


def schema(name: str, purpose: str, storage: str) -> str:
    return f"""# {name} Wiki Schema

## Purpose

{purpose}

## Architecture

- `raw/` optionally preserves original source documents when exact context or traceability has durable value. Existing files are immutable.
{area_lines()}
- Each knowledge area has its own `index.md` listing its pages with a one-line description. The root `index.md` is a short router to those area indexes.
- `log.md` is an append-only operations timeline.
- `entities.yaml` stores canonical names and aliases to prevent duplicate entities.
- `_inbox/unresolved/` is an exception queue only for ambiguity, contradiction, sensitivity, or failed validation requiring judgement.
- `tools/` contains local status and validation commands.
- `_templates/` holds page templates. `_views/` holds optional Obsidian views, such as the follow-up table.
- This file, `AGENTS.md`, is the only rulebook. `CLAUDE.md` imports it with `@AGENTS.md`. Edit rules here only.

## Client Commands

- Normal agent use: automatically file durable knowledge into the correct maintained pages when it surfaces.
- “Add this to my wiki”: explicitly ingest supplied text, a file, or an accessible document; preserve the original only when useful.
- “What does my wiki know about X?”: read `index.md`, search maintained pages, and answer with citations.
- “Check my wiki”: run `python3 tools/wiki_status.py .`, then inspect contradictions, duplicate entities, stale claims, missing links, and weak synthesis; log the semantic lint.
- “What changed recently?”: summarize `log.md`, plus recent Git changes when Git is set up.

The client should not need to manage files or run tools personally.

## Entity and Ontology Management

- Search `entities.yaml`, page titles, aliases, and existing content before creating a person, organisation, project, offering, event, or place.
- Merge new facts into the canonical page and update aliases in `entities.yaml` when needed. Never create a duplicate page merely because a name is written differently.
- Use the existing starter areas whenever they fit.
- Add a top-level category only for a durable, recurring page type that does not fit an existing area. Do not add a folder for one unusual item.
- When adding a category, describe it here, give it an `index.md`, add it to the root `index.md`, and log the change.
- Do not move or rename established pages without updating all links and explaining the migration in `log.md`.

## Multi-Agent Coordination

When several agents share this wiki, read a page again just before editing it, change only what the new knowledge needs, and never overwrite another agent's work. With Git, pull/rebase before ingest and protect unrelated changes.

{storage_section(storage)}
{PEOPLE_SECTION}
## Page Conventions

- Apply Open Knowledge Format v0.1 page and linking conventions to the maintained knowledge areas.
- Give every maintained Markdown page YAML frontmatter with a non-empty `type`. Add `title`, `description`, `tags`, `updated` (YYYY-MM-DD) and `resource` when useful. Start people pages from `_templates/person.md`.
- Keep root `index.md` and `log.md` as reserved navigation/history files, not concept pages.
- Keep one main entity, concept, source record, or synthesis per page. Use stable kebab-case filenames.
- Use standard bundle-root Markdown links such as `[Person](/people/person.md)`.
- Note where each fact came from: inline as `(src: where it came from)` next to the fact, and list links to files in `raw/` under `# Citations` at the bottom of the page.
- Keep raw originals in `raw/`. Use `source_material/` only when selected full notes, exact wording, or source context deserves a maintained page with metadata and links.
- Integrate new evidence into existing synthesis. Record contradictions, confidence changes, and unresolved questions.

## Ingest

1. Detect durable knowledge during normal agent use or read an explicit source fully; then read `index.md`, search maintained pages, and resolve named entities.
2. Ask the client only when ambiguity, contradiction, sensitivity, or failed validation prevents safe filing.
3. Create or update all affected pages across the appropriate areas; do not stop at an isolated source summary.
4. Add raw-source citations and cross-links. Update `entities.yaml` for new canonical entities or aliases.
5. Add or update the page's line in its area `index.md`; for a material change, append one concise `* **Ingest**: ...` entry under today's heading in `log.md`.
6. Run `python3 tools/validate_llm_wiki.py . --strict`.
7. When Git is set up, commit the coherent change directly on `main` and push when a remote exists.
8. Report knowledge filed, key pages changed, validation and save state, and only genuine unresolved exceptions.

## Query

Read the root `index.md`, then the relevant area `index.md` files, search relevant areas, inspect cited raw sources when needed, and answer with citations. File valuable new synthesis into the appropriate maintained page when agreed, then update the index if needed and log `* **Query**: Title`.

## Lint

Check duplicate entities, contradictions, stale claims, orphan pages, broken links, uncited claims, missing concepts, weak synthesis, index drift, entity-registry drift, schema drift, and `_inbox/unresolved/`. Fix safe issues directly and log material passes as `* **Lint**: Scope`.
"""


def area_index(name: str, description: str, pages: list[Path] | None = None) -> str:
    title = name.replace("_", " ").title()
    lines = "\n".join(f"- [{page.stem.replace('-', ' ').title()}]({page.name})" for page in pages or [])
    return f"# {title}\n\n{description}.\n\n## Pages\n\n{lines or 'No pages yet. Add one line per page: a link and a short description.'}\n"


def root_index(name: str, purpose: str) -> str:
    areas = "\n".join(f"- [{n.replace('_', ' ').title()}]({n}/index.md) — {d}." for n, d in MEMORY_AREAS)
    return f"""---
okf_version: "0.1"
---

# {name}

{purpose}

Start here, then open the area index you need. Each area index lists its pages.

## Knowledge areas

{areas}

## Views

- [Follow-ups](_views/crm.md) — people with a follow-up date, soonest first.
"""


def start_here(name: str, purpose: str, storage: str) -> str:
    saving = ("Your storage provider keeps the history of every change." if storage in SYNCED_STORAGE
              else "Git keeps the history of every change, so anything can be undone.")
    return f"""# Using {name}

Talk to an AI agent that can open this folder. You do not need to organise the files yourself.

## Useful things to say

- **Normal conversation** — the agent files decisions, people, projects and other things worth keeping as they come up.
- **“Add this to my wiki”** — paste text, attach a file or share a link. The agent updates every relevant page and tells you what changed.
- **“What does my wiki know about …?”** — ask across everything already filed.
- **“Who do I need to follow up with?”** — people whose follow-up date has arrived.
- **“Check my wiki”** — the agent checks structure, duplicates and links, and fixes what it safely can.
- **“What changed recently?”** — a plain summary of recent updates.

## How it is organised

There are folders for people, organisations, projects, offerings, events, places, decisions, preferences, observations, questions, ideas, lessons, playbooks, concepts and selected source material. Each folder has its own contents page. The agent creates and updates pages, merges duplicates and keeps the links and contents pages up to date.

{saving}

The wiki does not read your email, chats or drives unless you ask. `_inbox/unresolved/` is only for the rare item the agent cannot safely file without you.

## Purpose

{purpose}
"""


def write_if_missing(path: Path, content: str, added: list[str], root: Path) -> None:
    if not path.exists():
        write(path, content)
        added.append(path.relative_to(root).as_posix())


def copy_tools(root: Path) -> None:
    script_dir = Path(__file__).resolve().parent
    for tool_name in ("wiki_status.py", "validate_llm_wiki.py"):
        source = script_dir / tool_name
        if not source.exists():
            fail(f"missing bundled tool: {source}")
        destination = root / "tools" / tool_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        destination.chmod(0o755)


def upgrade(root: Path) -> None:
    """Add missing rulebook sections, templates, views and area indexes. Never edits existing knowledge pages."""
    agents = root / "AGENTS.md"
    if not agents.exists():
        fail(f"no AGENTS.md in {root}; this does not look like a wiki made by this skill")
    added: list[str] = []
    notes: list[str] = []

    original_rules = agents.read_text(encoding="utf-8")
    rules = original_rules
    # Rules from earlier versions of this skill that told agents to keep two identical rulebooks.
    for before, after in LEGACY_RULES.items():
        if before in rules:
            rules = rules.replace(before, after)
            notes.append("AGENTS.md: updated a rule about the two rulebook files")
    if "## People and Follow-ups" not in rules:
        rules = rules.rstrip() + "\n\n" + PEOPLE_SECTION
        notes.append("AGENTS.md: added People and Follow-ups rules")
    write(agents, rules)

    claude = root / "CLAUDE.md"
    if not claude.exists():
        write(claude, CLAUDE_STUB)
        added.append("CLAUDE.md")
    elif "@AGENTS.md" not in claude.read_text(encoding="utf-8"):
        if claude.read_text(encoding="utf-8").strip() == original_rules.strip():
            write(claude, CLAUDE_STUB)
            notes.append("CLAUDE.md: replaced the duplicate rulebook with an @AGENTS.md import")
        else:
            notes.append("CLAUDE.md differs from AGENTS.md and was left alone; merge it into AGENTS.md, then replace it with the import")

    write_if_missing(root / "_templates" / "person.md", PERSON_TEMPLATE, added, root)
    write_if_missing(root / "_views" / "crm.md", CRM_VIEW, added, root)
    for area, description in MEMORY_AREAS:
        folder = root / area
        if folder.is_dir():
            pages = sorted(page for page in folder.glob("*.md") if page.name not in {"index.md", "log.md"})
            write_if_missing(folder / "index.md", area_index(area, description, pages), added, root)
    copy_tools(root)
    notes.append("tools/: refreshed validation and status tools")

    print(f"Upgraded wiki: {root}")
    for item in added:
        print(f"  added {item}")
    for note in notes:
        print(f"  {note}")
    print("Existing knowledge pages were not changed. Run: python3 tools/validate_llm_wiki.py .")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, help="New wiki destination, or the existing wiki with --upgrade")
    parser.add_argument("--name", help="Wiki name (required for a new wiki)")
    parser.add_argument("--purpose", help="What the wiki should help the user understand (required for a new wiki)")
    parser.add_argument("--storage", choices=STORAGE_CHOICES, default="local",
                        help="Where the wiki lives. Git is set up only for github and local")
    parser.add_argument("--remote", help="Existing private Git remote URL (github storage)")
    parser.add_argument("--no-git", action="store_true", help="Do not initialise Git")
    parser.add_argument("--upgrade", action="store_true", help="Add missing templates, views, indexes and rules to an existing wiki")
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if args.upgrade:
        upgrade(root)
        return
    if not args.name or not args.purpose:
        fail("--name and --purpose are required for a new wiki")
    if root.exists() and not root.is_dir():
        fail(f"destination exists and is not a directory: {root}")
    if root.exists() and any(root.iterdir()):
        fail(f"destination is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    use_git = not args.no_git and args.storage in {"github", "local"}

    today = dt.date.today().isoformat()
    (root / "raw" / "assets").mkdir(parents=True)
    write(root / "raw" / ".gitkeep", "")
    write(root / "raw" / "assets" / ".gitkeep", "")
    for area, description in MEMORY_AREAS:
        write(root / area / "index.md", area_index(area, description))
    write(root / "_inbox" / "unresolved" / ".gitkeep", "")
    write(root / "_templates" / "person.md", PERSON_TEMPLATE)
    write(root / "_views" / "crm.md", CRM_VIEW)

    write(root / "AGENTS.md", schema(args.name, args.purpose, args.storage))
    write(root / "CLAUDE.md", CLAUDE_STUB)
    write(root / ".gitignore", ".DS_Store\n.obsidian/workspace*.json\n*.swp\n")
    write(
        root / "entities.yaml",
        """# Canonical entity registry. Example:\n# people:\n#   jane-doe:\n#     name: Jane Doe\n#     aka: [Jane]\npeople: {}\norganisations: {}\nprojects: {}\nofferings: {}\nevents: {}\nplaces: {}""",
    )
    write(root / "START_HERE.md", start_here(args.name, args.purpose, args.storage))
    write(root / "index.md", root_index(args.name, args.purpose))
    write(
        root / "log.md",
        f"""# Wiki Update Log

## {today}
* **Initialization**: Created the memory structure, area indexes, templates, log, entity registry and rulebook (storage: {args.storage}).
""",
    )
    copy_tools(root)

    if use_git:
        if not shutil.which("git"):
            fail("git not found; install Git, or rerun with --no-git")
        git(root, "init", "-b", "main")
        if args.remote:
            git(root, "remote", "add", "origin", args.remote)
        git(root, "add", ".")
        commit = git(root, "commit", "-m", "Initialize personal business memory wiki", check=False)
        if commit.returncode != 0:
            print("WARNING: Git initialized but initial commit failed; configure Git identity and commit manually.", file=sys.stderr)

    print(f"Created memory wiki: {root} (storage: {args.storage}, Git: {'on' if use_git else 'off'})")
    print('Next: add one real person or note and say "Add this to my wiki". See START_HERE.md.')
    if args.remote and use_git:
        print("Remote configured but not pushed. Check the repository is private, then push.")
    elif args.remote:
        print(f"Ignored --remote: Git is off for {args.storage} storage.")


if __name__ == "__main__":
    main()
