# Client Operations

## Default mode: automatic filing

When an authorised agent conversation surfaces durable knowledge, the agent files it into the correct maintained pages immediately. The client should not sort captures, process an inbox, or approve routine classification.

The system has only three operations: ingest, query, and lint.

- **Ingest** — classify, merge, link, source, validate, commit, push.
- **Query** — search maintained knowledge and cite the supporting pages.
- **Lint** — check structure and meaning, fix safe issues, surface judgement calls.

Explicit commands such as “Add this to my wiki” remain useful, but are not required for durable facts to be remembered.

## Multi-agent coordination

Every agent follows byte-identical `AGENTS.md` and `CLAUDE.md`. Git is the audit and coordination layer: pull/rebase before work, preserve unrelated changes, make one coherent direct-to-`main` commit, and push after validation.

## Exceptions

`_inbox/unresolved/` is the only inbox. Use it solely when ambiguity, contradiction, sensitivity, or failed validation prevents safe filing. Each note states the source, what is unclear, and the exact decision required. Resolve and remove or archive it as soon as judgement is available.

## Post-ingest response

Return a concise receipt: knowledge filed, key pages changed, validation, commit/push state, and genuine exceptions. Do not create a client review task for ordinary memory.

## Scheduling

One weekly lint is a sensible default when scheduling is authorised. Do not schedule daily compilation or broad external-account capture. Source monitoring requires separate explicit permission and uses the same direct-ingest path.
