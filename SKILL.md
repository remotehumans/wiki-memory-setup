---
name: wiki-memory-setup
description: Create and operate a simple personal/business memory wiki based on Andrej Karpathy's ingest-query-lint pattern and minimal Open Knowledge Format conventions. Agents automatically file durable knowledge into visible people, organisations, projects, offerings, events, places, decisions, preferences, observations, questions, ideas, lessons, playbooks, concepts, and source-material areas; query the maintained wiki; and lint it periodically. Includes guided onboarding when a user hands an agent the skill link, a personal CRM with follow-up dates, a choice of storage (GitHub, Google Drive, OneDrive, SharePoint, Dropbox or local) and optional follow-up reminders. Use for personal wikis, business wikis, second brains, personal CRMs, client memory systems, Obsidian memory vaults, persistent memory, or source-to-wiki ingestion.
---

# Wiki Memory Setup

Create or operate a memory wiki with three operations only:

1. **Ingest** — an agent classifies, merges, cross-links, sources, validates and saves durable knowledge when it surfaces.
2. **Query** — an agent searches maintained pages and follows links/citations to answer from the wiki.
3. **Lint** — an agent periodically checks structure and meaning, then fixes safe issues directly.

The taxonomy helps retrieval; it is not extra workflow. The client does not sort notes or maintain a normal inbox.

## Guided Onboarding

Use this when a user gives you this skill's link or asks you to set up their memory wiki. The user should only need to answer questions. Ask one question at a time, in plain words, and do the work yourself.

1. **Check what you can do.** You need to read and write files on the user's computer and run commands.
   - If you can, continue.
   - If you cannot (for example a web chat), say so in one plain sentence and suggest an agent that can, such as Claude desktop with Cowork, Claude Code, Codex or Cursor. Offer to explain how to start there. Stop.
2. **Install the skill** into your own skills folder if it is not there already (for Claude: `~/.claude/skills/wiki-memory-setup`; for Codex: `~/.codex/skills/wiki-memory-setup`). Clone it from the link, or download the files if Git is not available. A newly installed skill may only load in a new session; if so, carry on from this guide in the current session.
3. **Check the basics.** Python 3 must run. If it does not, help install it, or create the same folders and files by hand from `scripts/init_llm_wiki.py`.
4. **Ask about the wiki:**
   - What should it be called, and what should it help them with? (For example: "my clients, contacts and projects".)
   - Where should it live? Offer the storage options in `references/storage-and-connectors.md`. Recommend GitHub for history and agent access, but accept any choice, including "IT hasn't approved GitHub".
   - Which folder? Find their real synced folder (see `references/storage-and-connectors.md` for typical locations) and suggest a subfolder such as `My Brain`. For a cloud folder, check it is set to stay available offline.
5. **Create it** with `scripts/init_llm_wiki.py --path ... --name ... --purpose ... --storage ...`. For GitHub, follow the walkthrough in `references/storage-and-connectors.md`.
6. **First test.** Read the new wiki's `AGENTS.md`. Ask for one real person they spoke to recently. File them from `_templates/person.md`, turning dates like "next Tuesday" into YYYY-MM-DD (check with the user if it is ambiguous), and set `next_touch` if a follow-up was mentioned. Run the validator. Then answer "What does my wiki know about <name>?" and show it. This proves it works.
7. **Follow-up reminders (optional).** Ask whether they want reminders about follow-ups. If yes, follow `references/follow-ups.md`, including whether they want a notification only or draft messages.
8. **Connect it (optional).** Offer to connect the wiki to their other AI apps as context, using `references/storage-and-connectors.md`.
9. **Hand over.** Point them to `START_HERE.md`, give three things they can say, and stop. Keep the summary short.

Never put the wiki in a public place. Never connect email, chats or drives as sources unless the user asks.

## Upgrading an Existing Wiki

When a wiki made by an earlier version of this skill lacks `_templates/person.md`, area `index.md` files or the `@AGENTS.md` import, run:

```bash
python3 scripts/init_llm_wiki.py --path /path/to/wiki --upgrade
```

It adds what is missing, updates outdated rules in `AGENTS.md`, refreshes the tools and never edits existing knowledge pages.

## Setup Details

Read `references/karpathy-pattern.md` and `references/okf-conventions.md`, then run:

```bash
python3 scripts/init_llm_wiki.py \
  --path /path/to/wiki \
  --name "Client Memory" \
  --purpose "Durable personal and business context" \
  --storage local
```

`--storage` is one of `github`, `local`, `google-drive`, `onedrive`, `sharepoint`, `dropbox`, `icloud` or `other`. Git is set up only for `github` and `local`. Use `--remote PRIVATE_GIT_URL` only when the user has supplied or authorised a private remote. Do not enable scheduled capture by default.

The scaffold includes:

- Maintained typed areas: `people/`, `organisations/`, `projects/`, `offerings/`, `events/`, `places/`, `decisions/`, `preferences/`, `observations/`, `questions/`, `ideas/`, `lessons/`, `playbooks/`, `concepts/`, and `source_material/`, each with its own `index.md`.
- A short root `index.md` that routes to the area indexes.
- `_templates/person.md` with contact and follow-up fields (`last_contact`, `next_touch`), and `_views/crm.md`, a follow-up table for Obsidian.
- Optional `raw/` preservation when exact original material or provenance is useful.
- `entities.yaml`, `log.md`, `AGENTS.md` as the only rulebook, `CLAUDE.md` importing it with `@AGENTS.md`, structural validation, and status tools.
- `_inbox/unresolved/` only for genuine ambiguity, contradiction, sensitivity, or failed validation requiring judgement.

## Automatic Ingest

During ordinary agent use, detect durable knowledge without needing a separate “remember this” command. Decisions, observations, lessons, preferences, people, relationships, project changes, commitments, and stable context usually qualify. Apply the wiki's durability threshold; do not capture transient chatter or process narration.

For every ingestion:

1. If Git is set up, pull/rebase `main`; protect unrelated changes with an isolated worktree.
2. Read the source fully, then search `entities.yaml`, the root and area `index.md` files, and relevant pages.
3. Classify each durable fact into the correct maintained areas. One source may update several pages.
4. Merge and supersede by meaning. Do not create a source-shaped summary pile.
5. Add canonical entities/aliases, cross-links, dates, and citations.
6. Preserve the original under `raw/` or as `source_material/` only when exact context has continuing value.
7. Update the area `index.md`; for people, keep `last_contact`, `next_touch` and History current; add one concise `log.md` entry for a material change.
8. Run `python3 tools/validate_llm_wiki.py . --strict`.
9. If Git is set up, commit the coherent change on `main` and push when a remote exists. Otherwise the storage provider keeps the history.

Ask the user only when a judgement cannot be safely inferred. Put that exception in `_inbox/unresolved/` with the source, uncertainty, and exact decision required. Everything else is filed automatically.

## Query

Read `index.md`, search titles/frontmatter/body text and aliases, follow relevant links, and inspect citations or raw/source material when precision requires it. Cite the maintained pages supporting the answer. If querying produces durable new synthesis, file it through the same ingest operation.

GBrain, embeddings, or graph tooling may accelerate query later, but the Markdown wiki and its saved history remain the source of truth; setup does not depend on them.

## Lint

Run structural validation and an LLM semantic pass for:

- Duplicate entities and facts
- Contradictions or stale claims
- Broken or missing links/citations
- Orphan pages and index/schema drift
- Pages stacking summaries instead of maintained synthesis
- Missing connections or useful promoted concepts
- Items lingering in `_inbox/unresolved/`

Fix unambiguous issues directly on `main`. Surface only judgement calls. One weekly lint is normally enough; do not create a daily compile/review job.

## Conversational Interface

- **Normal agent conversation** — file durable knowledge automatically.
- **“Add this to my wiki”** — explicitly ingest supplied text, file, or accessible source.
- **“What does my wiki know about X?”** — query and cite maintained knowledge.
- **“Check my wiki”** — validate, lint, fix safe issues, and report exceptions.
- **“Who do I need to follow up with?”** — list people whose `next_touch` is due, soonest first.
- **“What changed recently?”** — summarise recent `log.md` and Git changes.

## Completion Contract

Report only what helps the user:

- Durable knowledge filed and key pages changed
- Validation and save state (commit/push when Git is set up)
- Genuine unresolved exceptions, if any

Never report a normal item as “waiting for review” merely because an agent captured it.
