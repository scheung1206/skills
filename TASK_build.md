# Task: Build the skills library (initial `dev/` pass) per PLAN.md

You are the IMPLEMENTER. Build the initial skills library at `/Users/stephencheung/skills/`
exactly to the locked spec in `PLAN.md` (read it first — it is the authority). Do NOT deviate.
After building, open a PR for Stephen's review; do NOT merge (Hard Rule: MR review gate).

## What to build (ONLY these — `generic/` and `projects/` are NOT built yet)

1. `refresh-skills-index.py` at repo root — walks `generic/`, `dev/`, `projects/*/`, parses each SKILL.md
   YAML frontmatter (`name`, `tier`, `description`), emits `INDEX.md` (flat table:
   `| skill | tier | trigger |`). WARN if any SKILL.md is newer (mtime) than its CHANGELOG.md.
   Run it at the end and commit the generated INDEX.md.

2. Three `dev/` skills, each as a folder with `SKILL.md` + `CHANGELOG.md`:
   - `dev/orchestration/`
   - `dev/tdd-gate/`
   - `dev/documentation-workflow/`

3. `CONTRIBUTING.md` at repo root — how to add a skill, run gen-index, tier meanings, naming
   (`projects/<project>/` not dot-prefixed), Hard Rules summary.

## Per-skill SKILL.md format (STRICT)
Frontmatter (YAML, first lines):
```
---
name: <kebab-case, matches folder>
tier: dev
description: <WHEN to use — trigger phrasing, not a noun summary>
tools: [delegation, terminal, file]
status: active
env: macos>=12
---
```
Body sections IN ORDER:
```
# <Title>
## Trigger
<one line: exact condition to load this skill>
## Steps
<numbered, executable; inline commands/scripts>
## Pitfalls
<DON'T-style prohibitions>
## Verify
<assertable check proving success>
## Non-use / Scope
<when NOT to use this skill / not to spin an agent>
```
Every skill also gets `CHANGELOG.md`:
```
# <skill> — Changelog
## v1.0.0 — 2026-08-06
- ADDED: <feature>
- DECISION: <why>
- MODEL: validated against <model/agent, e.g. Hermes+Codex>
- REJECTED: <alt considered, if any>
```

## Content of each skill (from PLAN.md §8.5 — implement faithfully)

### dev/orchestration
- Pattern: orchestrator decomposes + dispatches; implementer writes code/PR; a DIFFERENT agent
  reviews; branch→PR→review gate; never auto-merge; orchestrator verifies before trusting.
- Model-config block (model assignment is a deliberate cost/quality decision). Rule: expensive/slow
  model on REVIEW (few calls, high correctness value); cheap/fast on orchestration+implementation
  (high volume, low marginal value). Example configs:
  - Personal: orchestrator=Hermes (free), implementer=Codex (gpt-5.6-sol), reviewer=Claude (Opus/Max)
  - Work:     orchestrator=Sonnet,        implementer=Sonnet,           reviewer=Opus
  Swap assignments freely; pattern holds.
- SKILL-INJECTION STEP (critical): sub-agents do NOT self-discover skills. Orchestrator matches
  the relevant skill via INDEX.md/description, then INJECTS the matched SKILL.md (+ references/)
  into each sub-agent's brief — implementer gets skill+task; reviewer gets skill+TDD/tests+output.
- Non-use: don't spin agents for tiny edits, deterministic scripts, or security-critical paths.

### dev/tdd-gate
- Discipline: BEFORE implementer writes any implementation, they MUST produce a runnable TDD (test
  file or explicit assertions) committed to the branch, for Stephen's review. Implementation starts
  ONLY after green-light. TDD artifact = runnable test / explicit assertion list in the branch.
- Non-use: trivial one-liners where a test is heavier than the code (note: still prefer TDD).

### dev/documentation-workflow
- The paper-trail practice: every skill/project has CHANGELOG.md with versioned entries
  (ADDED/CHANGED + DECISION + MODEL + REJECTED + date). Mirrors this very build.
- Non-use: don't log "updated file" without a DECISION; don't put reasons in SKILL.md body.

## Hard Rules (do not violate — Stephen reviews before merge)
- NO direct push to main. Branch `build/dev-skills`, commit there, open PR, request Stephen review.
- No work IP, no secrets. Personal Mac only (you are on it).
- Skills are markdown + references/; agent is the runtime.

## Verify before opening PR
- Run `python3 refresh-skills-index.py` — INDEX.md generated, no SKILL.md newer than its CHANGELOG.
- Each SKILL.md has valid frontmatter + all 5 body sections + Non-use note.
- Each has CHANGELOG.md with v1.0.0 + DECISION + MODEL.
- `git status` clean of secrets.

## Deliver
- Branch `build/dev-skills` with all files committed.
- PR opened against `main` (or default) on `scheung1206/skills`, titled "Initial dev/ skills:
  orchestration, tdd-gate, documentation-workflow + gen-index + CONTRIBUTING".
- Assign/request review from Stephen (scheung1206). Do NOT merge.
- Print the PR URL and a 1-paragraph summary.
