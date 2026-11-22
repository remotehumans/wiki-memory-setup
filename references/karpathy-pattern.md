# Karpathy LLM Wiki Pattern

Source: [Andrej Karpathy, “LLM Wiki”](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Core distinction

Document RAG repeatedly retrieves fragments and reconstructs understanding at query time. An LLM wiki compiles understanding once, keeps it current, and makes later questions build on maintained synthesis.

## Roles

- Human: curate sources, guide emphasis, explore, question, and review.
- LLM: summarize, integrate, cross-reference, revise, flag contradictions, maintain the index, and maintain the log.
- Obsidian or another Markdown editor: optional browsing and graph interface, never the storage contract.

## Three layers

- Raw sources are immutable source truth.
- Wiki pages are generated and maintained by the LLM.
- The schema file tells the active agent how this particular wiki works and evolves as the domain becomes clearer.

## Compounding operations

- Ingest sources into the existing body of knowledge, not isolated summaries.
- Answer from maintained pages and file valuable outputs back into the wiki.
- Lint for inconsistency, staleness, missing pages, missing links, and useful next investigations.

## Scale

Start with `index.md`, ordinary file search, and direct reads. Hundreds of pages can remain workable without embeddings. Add local search such as qmd only when measured retrieval failures justify it.

The source intentionally leaves exact directories, schemas, tooling, and output formats open. This skill instantiates that open pattern for personal and business memory with a small entity-oriented starter structure. Let the structure grow when repeated use earns a new category; do not add unrelated assistant workflows.
