# Wiki Workflows

## Ingest check

- Durable material identified during normal agent use or from an explicit source.
- Existing wiki and entity aliases searched before page creation.
- Knowledge integrated into the correct typed pages, not left as a capture summary.
- Stale statements superseded and duplicates removed by meaning.
- Dates, citations, canonical entities, cross-links, index, and material log entry updated.
- Exact source preserved only when useful.
- Structural validation passes.
- Coherent change saved: committed and pushed on `main` when Git is set up.
- Only genuine ambiguity, contradiction, sensitivity, or failed validation enters `_inbox/unresolved/`.

## Query check

- Search index, entities, titles, frontmatter, body text, and links.
- Read source material when synthesis is insufficient or exact wording matters.
- Cite maintained pages near supported claims.
- Identify uncertainty or disagreement explicitly.
- File durable new synthesis through the normal ingest operation.

## Lint check

- Contradictory, stale, or duplicate claims.
- Orphans, broken links, missing citations, and index/entity/schema drift.
- Pages stacking source summaries instead of synthesis.
- Missing durable connections or promoted concepts.
- Unresolved exceptions that can now be closed.
- Safe fixes committed directly; judgement calls reported concisely.

Add a top-level category only for a durable recurring type that does not fit the starter taxonomy. Update `AGENTS.md`, give the area an `index.md`, add it to the root index, and log it.
