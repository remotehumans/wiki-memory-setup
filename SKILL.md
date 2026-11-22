---
name: wiki-memory-setup
description: Create and operate a simple personal/business memory wiki based on Andrej Karpathy's ingest-query-lint pattern and minimal Open Knowledge Format conventions. Agents automatically file durable knowledge into visible people, organisations, projects, offerings, events, places, decisions, preferences, observations, questions, ideas, lessons, playbooks, concepts, and source-material areas; query the maintained wiki; and lint it periodically. Use for personal wikis, business wikis, second brains, client memory systems, Obsidian memory vaults, persistent memory, or source-to-wiki ingestion.
---

# Wiki Memory Setup

Create or operate a memory wiki with three operations only:

1. **Ingest** — an agent classifies, merges, cross-links, sources, validates, commits, and pushes durable knowledge when it surfaces.
2. **Query** — an agent searches maintained pages and follows links/citations to answer from the wiki.
3. **Lint** — an agent periodically checks structure and meaning, then fixes safe issues directly.

The taxonomy helps retrieval; it is not extra workflow. The client does not sort notes or maintain a normal inbox.

## Setup

Read `references/karpathy-pattern.md` and `references/okf-conventions.md`, then run:

```bash
python3 scripts/init_llm_wiki.py \
  --path /path/to/wiki \
  --name "Client Memory" \
  --purpose "Durable personal and business context"
```

Use `--remote PRIVATE_GIT_URL` only when the user has supplied or authorised a private remote. Do not enable scheduled capture by default.

The scaffold includes:

- Maintained typed areas: `people/`, `organisations/`, `projects/`, `offerings/`, `events/`, `places/`, `decisions/`, `preferences/`, `observations/`, `questions/`, `ideas/`, `lessons/`, `playbooks/`, `concepts/`, and `source_material/`.
- Optional `raw/` preservation when exact original material or provenance is useful.
- `entities.yaml`, `index.md`, `log.md`, byte-identical `AGENTS.md`/`CLAUDE.md`, structural validation, and status tools.
- `_inbox/unresolved/` only for genuine ambiguity, contradiction, sensitivity, or failed validation requiring judgement.

## Automatic Ingest

During ordinary agent use, detect durable knowledge without needing a separate “remember this” command. Decisions, observations, lessons, preferences, people, relationships, project changes, commitments, and stable context usually qualify. Apply the wiki's durability threshold; do not capture transient chatter or process narration.

For every ingestion:

1. Pull/rebase `main` if Git is configured; protect unrelated changes with an isolated worktree.
2. Read the source fully, then search `entities.yaml`, `index.md`, and relevant pages.
3. Classify each durable fact into the correct maintained areas. One source may update several pages.
4. Merge and supersede by meaning. Do not create a source-shaped summary pile.
5. Add canonical entities/aliases, cross-links, dates, and citations.
6. Preserve the original under `raw/` or as `source_material/` only when exact context has continuing value.
7. Update `index.md`; add one concise `log.md` entry for a material change.
8. Run `python3 tools/validate_llm_wiki.py . --strict`.
9. Commit the coherent change on `main` and push immediately.

Ask the user only when a judgement cannot be safely inferred. Put that exception in `_inbox/unresolved/` with the source, uncertainty, and exact decision required. Everything else is filed automatically.

## Query

Read `index.md`, search titles/frontmatter/body text and aliases, follow relevant links, and inspect citations or raw/source material when precision requires it. Cite the maintained pages supporting the answer. If querying produces durable new synthesis, file it through the same ingest operation.

GBrain, embeddings, or graph tooling may accelerate query later, but the Markdown wiki and Git history remain the source of truth; setup does not depend on them.

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
- **“What changed recently?”** — summarise recent `log.md` and Git changes.

## Completion Contract

Report only what helps the user:

- Durable knowledge filed and key pages changed
- Validation and commit/push state
- Genuine unresolved exceptions, if any

Never report a normal item as “waiting for review” merely because an agent captured it.
