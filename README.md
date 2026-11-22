# Wiki Memory Setup

An agent skill that sets up a personal or business memory wiki (a "second brain") in plain Markdown and Git. Your AI agent files what's worth remembering, answers questions from it and keeps it tidy. It's based on Andrej Karpathy's ingest, query and lint pattern.

## Install

Claude Code:

```bash
git clone https://github.com/remotehumans/wiki-memory-setup.git ~/.claude/skills/wiki-memory-setup
```

Codex:

```bash
git clone https://github.com/remotehumans/wiki-memory-setup.git ~/.codex/skills/wiki-memory-setup
```

Restart your agent, then ask: "Set up my memory wiki."

## What you get

- Folders for people, organisations, projects, decisions, lessons, playbooks and more
- An agent that files durable knowledge automatically as you work
- Answers to "What does my wiki know about X?", with links to the pages it used
- A weekly "Check my wiki" pass that fixes duplicates, broken links and stale pages

Needs Python 3 and Git. See `SKILL.md` for full details.

Made by [Remote Humans](https://remotehumans.ai).
