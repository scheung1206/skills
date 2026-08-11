---
name: documentation-workflow
tier: dev
description: Use when creating or changing a skill or project that requires a versioned decision paper trail in CHANGELOG.md.
tools: [delegation, terminal, file]
status: active
env: macos>=12
---

# Documentation Workflow

## Trigger
- Load this skill whenever a skill or project is created or materially changed and its decisions must remain traceable.

## Steps
1. Keep operational instructions and current behavior in `SKILL.md`; keep reasons and history in the adjacent `CHANGELOG.md`.
2. Add a heading in the form `## vX.Y.Z — YYYY-MM-DD`, using MAJOR for structural changes, MINOR for content or step changes, and PATCH for fixes or typos.
3. Add `ADDED:` for new behavior or `CHANGED:` for revised behavior.
4. Add `DECISION:` with the constraint and reason for the chosen approach.
5. Add `MODEL:` naming the model or agent combination used to validate the entry.
6. Add `REJECTED:` with any meaningful alternative considered and why it was not selected.
7. Update the changelog whenever the skill or project changes, then run `python3 gen-index.py` after any skill metadata change.
8. Review the diff to ensure the paper trail contains no work IP, secrets, endpoints, schemas, or client data.

## Pitfalls
- DON'T log only "updated file"; record the decision and its reason.
- DON'T put historical reasons or rejected alternatives in the `SKILL.md` body.
- DON'T omit the date, semantic version, or model validation record.
- DON'T copy employer-derived details into the personal repository.

## Verify
- Run `python3 gen-index.py` and assert every changed skill or project has an adjacent `CHANGELOG.md` entry containing a versioned date plus `ADDED:` or `CHANGED:`, `DECISION:`, `MODEL:`, and any applicable `REJECTED:` line.

## Non-use / Scope
- Do not use this workflow to record a reasonless "updated file" entry, and do not place decision history in the `SKILL.md` body.
