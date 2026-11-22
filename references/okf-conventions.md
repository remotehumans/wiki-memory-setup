# Google Open Knowledge Format v0.1

Source: [Google Cloud Knowledge Catalog — OKF v0.1 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).

Apply OKF page, link, index, and log conventions to the maintained top-level knowledge areas and root `index.md`/`log.md`. Keep `raw/` as the separate immutable source layer from the Karpathy pattern.

## Conformance

- Represent each concept as one UTF-8 Markdown file with YAML frontmatter.
- Require only a non-empty `type` field. Recommend `title`, `description`, `resource`, `tags`, and ISO 8601 `timestamp` where useful.
- Permit domain-specific fields. Consumers must tolerate unknown types and fields.
- Reserve `index.md` and `log.md`; they are not concept documents.
- Use stable kebab-case paths and domain-appropriate directories.
- Use standard Markdown links. Prefer bundle-root links such as `[Concept](/topics/concept.md)`; relative links are also valid.
- Put external and raw-source support under a final `# Citations` heading when a concept makes sourced claims.
- Treat broken concept links as a soft lint issue, not invalid OKF.

## Progressive disclosure

An `index.md` may appear at any directory level. List each concept or subdirectory with a relative link and one-line description:

```markdown
# Topics

* [Example concept](example-concept.md) - One-line summary.
```

The bundle-root index may declare `okf_version: "0.1"` in frontmatter. Do not add other page metadata to index files.

## Log

`log.md` is optional and uses newest-first ISO date headings:

```markdown
# Wiki Update Log

## 2026-07-15
* **Creation**: Added [Example concept](/example-concept.md).
```

Example page:

```markdown
---
type: concept
title: Example concept
description: One-line navigation summary
tags: [example]
timestamp: 2026-07-15T12:00:00Z
---

# Example concept

Integrated synthesis with a link to a [related concept](/related-concept.md).

# Citations

[1] [Example source](../raw/example-source.md)
```

Use the personal/business starter areas supplied by this skill, but do not turn them into a closed ontology. The specification explicitly leaves taxonomy, storage, serving, and query infrastructure to the producer.
