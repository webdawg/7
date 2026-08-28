# creation.md — Spec-Driven Project Bootstrap

Copy this file into a new project repo and follow it to set up the same
structure used in `7` (The City of Light).

## 1. Root spec

Write a `SPEC.md` describing the concept at whatever level of abstraction
fits the project — mythic, technical, or both. This is the project's north
star document.

## 2. specs/ directory

Create a `specs/` folder. Each subsystem/component gets its own folder:
`specs/<slug>/SPEC.md`, plus any supporting files needed. Track a status
(`proposed` / `in-progress` / `implemented`) per spec. Create
`specs/INDEX.md` listing every registered spec and restating the folder
convention.

## 3. LLM index files

At repo root, create:

- `llms.txt` — concise index per the [llms.txt standard](https://llmstxt.org/):
  an H1 title, a one-line blockquote summary, then a `## Docs` section
  linking every doc in the repo with a one-line description.
- `llms-full.txt` — full concatenation of every doc's content, for feeding
  an LLM complete context in one file. Regenerate whenever docs change.

## 4. Prompt-logging hook

Configure a project-scoped Claude Code `UserPromptSubmit` hook (via the
`update-config` skill, or directly in `.claude/settings.json`) that appends
every prompt submitted while working in this repo to a log file (e.g.
`PROMPTS.md`), so the design conversation that produced the specs is
preserved alongside them.

## 5. This file

Keep a copy of this `creation.md` at the repo root so the pattern is
self-documenting and can be copied forward into the next project.
