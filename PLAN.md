# Skills Library — Master Plan

**Status:** PLAN ONLY. No skills implemented yet. This document is the authoritative spec for
the library's purpose, organization, and documentation/implementation rules. Implementation
begins only after this plan is approved and any adjustments made.

---

## 1. Purpose

A personal, portable, versioned library of **engineering playbooks** ("skills") that capture
how Stephen (Shinsu) builds, operates, and reasons about software — so that:

1. **AI agents can load and execute them reliably** (Hermes, Claude Code, Cursor, or any
   tool-agnostic agent) via a fixed, machine-readable format.
2. **Knowledge compounds** instead of living in chat history or one person's memory.
3. **Provenance is explicit and safe**: personal IP stays personal; only generic procedures
   are ever forked to work, in one direction.

The library is the *source of truth* for "how we do X." It is NOT a notes dump — every entry
is an executable, maintained procedure with a decision record.

---

## 2. Organization Structure (strict)

```
~/skills/
├── PLAN.md              <- this file (the contract)
├── INDEX.md             <- SCRIPT-GENERATED: flat table of all skills + triggers (agent discovers here)
├── SKILL-TEMPLATE.md    <- copy to create a new skill (enforces the doc structure)
├── generic/             <- TIER 1: tool-agnostic procedures, NO personal/work IP. FORKABLE to work.
├── dev/                 <- TIER 2: DEVELOPMENT-WORKFLOW & RULE skills (process/meta). FORKABLE.
└── projects/            <- TIER 3: skills tied to a SPECIFIC project. PERSONAL-ONLY, never fork.
    ├── _.gm/            <-   one subfolder per project
    └── resume/
```

### Tier rules (enforced)
- **generic/**: procedures with zero personal-project or employer IP. Safe to fork into a work
  GitHub org. Example candidates: docx-cleanup, eval-harness, cloudflare-deploy.
- **dev/**: DEVELOPMENT-WORKFLOW and RULE skills — how Stephen runs AI-dev processes. Pure
  process/meta, no project code. Examples: orchestration (implementer+reviewer workflow),
  documentation-workflow (feature/decision paper-trail). Technique is generic and forkable;
  keep any project examples sanitized.
- **projects/**: skills tied to a SPECIFIC project, organized in a subfolder per project
  (`projects/_.gm/`, `projects/resume/`). Contains personal IP. NEVER copied to work laptops
  or work GitHub. The `projects/` tree is a namespace; skills live one level deeper.

### Folder naming
- One skill = one folder, named in `kebab-case`, matching the `name` in its frontmatter.
- Atomic: one responsibility per skill. If it does two things, split it.

---

## 3. Documentation Structure (strict — every SKILL.md)

### 3.1 Frontmatter (mandatory, first 5 lines, YAML)
```yaml
---
name: <kebab-case, must match folder>
tier: generic | dev | projects
description: <WHEN to use — trigger phrasing, not a noun summary>
tools: [terminal, file, delegation, web]
---
```
- `description` is the **trigger**, not a summary. Agents match user intent against it.
  - GOOD: "Use when the user wants to extract text from a .docx"
  - BAD:  "A docx text extractor"
- `tier` enforces the provenance rule (generic/dev = forkable, projects = personal-only).

### 3.2 Body (fixed sections, in order)
```
# <Title>

## Trigger
<one line: exact condition that means "load this skill">

## Steps
<numbered, executable; inline commands/scripts where possible>

## Pitfalls
<DON'T-style prohibitions; what broke before and how to avoid>

## Verify
<assertable CLI/code check proving success — never "make sure it works">
```

### 3.3 AI-processing requirements
- Frontmatter drives the **load decision** (agent parses YAML, skips body until needed).
- Body is **lists, not prose** — agents extract actions from lists reliably.
- Commands are **inline and copy-pasteable** — avoid "see other file" hops.
- Pitfalls are **negatives** ("DON'T regex-surgery document.xml") — agents follow prohibitions.
- Verify is **assertable code**, not vague checking.

---

## 4. Paper-Trail / Decision Log (strict — every skill)

Each skill folder ALSO contains a `CHANGELOG.md` recording the project-style paper trail:

```markdown
# <skill name> — Changelog

## v1.0.0 — YYYY-MM-DD
- ADDED: <feature / initial skill>
- DECISION: <why this approach; constraints chosen; what was rejected>
- CONTEXT: <project/TASK link if derived from one>

## v1.1.0 — YYYY-MM-DD
- CHANGED: <what changed>
- DECISION: <why — user's correction/constraint>
- REJECTED: <alternative considered and why not>
```

### Rules
- Versioning: SEMANTIC primary `vX.Y.Z` (MAJOR = structural change, MINOR = content/step
  change, PATCH = fix/typo) PLUS a `YYYY-MM-DD` last-updated date on every entry.
  Format: `## v1.2.0 — 2026-08-06`.
- **Version increments ONLY after merge to `main`.** Iterations within a PR (review comments,
  fixes before merge) do NOT bump the version — keep the same version and record changes as part
  of that version's entry (or an in-flight note). A version number implies "merged and settled."
- Every entry has a **DECISION** line (the "why"). No entry without a reason. MR comment
  discipline: review comments must communicate the CODE DECISION (what was decided and why) with
  role+model labels, so the audit trail is unambiguous.
- `REJECTED` is encouraged — captures paths tried and dropped (mirrors resume v1-v10).
- CHANGELOG stays SEPARATE from SKILL.md (SKILL.md = "what/how"; CHANGELOG = "why/when").

---

## 5. Discovery & Indexing

- `INDEX.md` is the agent's entry point: a flat table of every skill with `tier` + short
  `trigger`. An agent scans INDEX.md to decide relevance, then loads the specific SKILL.md.
- **INDEX.md is SCRIPT-GENERATED**, not hand-maintained. A generator script (in repo root,
  e.g. `gen-index.py`) walks `generic/`, `dev/`, `projects/*/` , reads each SKILL.md frontmatter,
  and emits INDEX.md. Run it on every skill add/edit/remove so the index never drifts.
- Rationale: a hand-maintained index goes stale; generation keeps discovery accurate at scale
  without manual toil. (Alternative considered: no index, agent reads all frontmatter on demand
  — rejected as O(N) and token-heavy past ~10 skills.)

---

## 6. Provenance & Legal-Safety Rules (strict, non-negotiable)

1. **ONE-WAY flow**: `~/skills` (personal) -> work fork. NEVER work -> personal.
2. Work may fork `generic/` and sanitized `dev/` only. `projects/` stays personal.
3. Personal repo is the **immutable source of truth**; work forks are derived copies.
4. No work IP (source, endpoints, schemas, client data, secrets) ever enters `~/skills`.
5. Library lives on Stephen's **personal Mac + personal GitHub** only.
6. At work, fork into the work org's repo; any work-specific playbooks are created AT work
   (company context), not mirrored from personal.

---

## 7. Implementation Rules (how skills get built)

1. New skill starts from `SKILL-TEMPLATE.md`.
2. Before saving, append a `CHANGELOG.md` v1.0.0 entry (ADDED + DECISION + date).
3. **Run `gen-index.py`** to regenerate INDEX.md (never hand-edit INDEX.md).
4. Verify the skill is processable: frontmatter valid, sections present, Verify is assertable.
5. Git-commit on personal GitHub (`scheung1206/skills`); commit history proves provenance.

---

## 7b. Hard Rules (non-negotiable — remembered)

These are Stephen's standing rules. They override any convenience and are never waived:

1. **MR/PR review gate:** NO code enters `main` without Stephen's explicit review and approval
   of the merge request / pull request FIRST. Branch → PR → Stephen reviews → only then merge.
   Never auto-merge. Never push directly to `main`.
2. **Orchestrator never merges its own work:** the orchestrator (Hermes / Sonnet / whoever) may
   open the PR and verify, but the MERGE decision is Stephen's alone. Sub-agents (implementer,
   reviewer) do not merge.
3. **No work IP in personal repo:** only generic/dev procedures and Stephen's own project
   playbooks. Never employer source, endpoints, schemas, secrets, or client data.
4. **Personal repo commits only from personal Mac:** never `git commit` to `scheung1206/skills`
   from a work device (keeps provenance chain clean).
5. **Skills are markdown + references; the agent is the runtime:** never embed secrets in
   `references/`; use sanitized templates.

Rule #1 is the load-bearing one: **every change to this library (or any project built with it)
flows through a reviewable MR that Stephen approves before merge.** The TDD-gate (§8.5) extends
this to implementation: review the test before the code.

---

## 8. Open Decisions — RESOLVED

1. **Tier boundaries**: `generic` = tool-agnostic no-IP procedures; `dev` = development-workflow
   & rule skills (process/meta, forkable); `projects` = per-project subfolders, personal-only.
2. **Versioning**: semantic primary `vX.Y.Z` + `YYYY-MM-DD` last-updated date. RESOLVED.
3. **INDEX.md**: SCRIPT-GENERATED via `gen-index.py`. RESOLVED (alternative: hand-maintained
   rejected as drift-prone; no-index rejected as O(N)).
4. **GitHub repo**: `scheung1206/skills` on personal GitHub. RESOLVED.
5. **Initial implementation scope (after approval) — `dev/` ONLY, three skills:**
   - `dev/orchestration` — orchestrator / implementer / reviewer workflow. Documents the
     **pattern** (orchestrator decomposes + dispatches; implementer writes code/PR; a DIFFERENT
     agent reviews; branch→PR→review gate; never auto-merge; orchestrator verifies before
     trusting) as tool-agnostic, PLUS a **model-config block** (model assignment is a deliberate
     cost/quality decision). Captured rule: spend the expensive/slow model on REVIEW (few calls,
     high correctness value); cheap/fast model on orchestration + implementation (high volume,
     low marginal value). Example configs:
       - Personal: orchestrator=Hermes (free), implementer=Codex (gpt-5.6-sol), reviewer=Claude (Opus/Max).
       - Work:     orchestrator=Sonnet,        implementer=Sonnet,           reviewer=Opus.
     Swap the three assignments for any agent/model that fills the role; the pattern holds.
     **Skill-injection step (critical):** sub-agents do NOT self-discover skills. The orchestrator
     matches the relevant skill via INDEX.md / description, then INJECTS the matched SKILL.md (and
     its `references/`) into each sub-agent's brief/context — implementer gets the skill + task;
     reviewer gets the skill + TDD/tests + output to verify against. Discovery (§5) is the
     orchestrator's mechanism; passing the skill down is the orchestrator's responsibility.
   - `dev/tdd-gate` — the test-first discipline: BEFORE the implementer writes any implementation,
     they MUST produce a runnable TDD (test file or explicit assertions) committed to the branch,
     for YOUR review. Implementation starts ONLY after you green-light the TDD. This catches
     misunderstanding at the cheapest point (review intent, not just output). The TDD artifact
     format is locked: a runnable test / explicit assertion list in the branch, reviewed pre-impl.
   - `dev/documentation-workflow` — the feature/decision paper-trail practice (CHANGELOG per
     skill/project, DECISION lines, REJECTED tracking, model-version recorded). This very process.
   - NOTE: `generic/` and `projects/` skills are NOT built initially. Only these three `dev/`
     skills are implemented in the first pass. Other tiers added later as needed.

---

## 8b. Adopted Spec Additions (from review — cheap + essential)

- **Frontmatter fields:** add `status: active|deprecated` and `env:` (min environment, e.g.
  `macos>=13`) to every SKILL.md. Prevents trusting stale/broken skills.
- **`references/` subfolder:** allowed per skill for scripts/templates/examples (sanitized, no
  secrets). Required only for skills with artifacts; optional for pure-procedure skills.
- **CHANGELOG `model:` field:** each entry records the model version that validated it
  (e.g. "validated against Codex gpt-5.6-sol, 2026-08") so model drift is distinguishable from
  step errors.
- **Non-use / Scope note:** every skill includes a line on when NOT to use it / not to spin an
  agent (tiny edits, deterministic scripts, security-critical paths).
- **Runnable tests/eval (REQUIRED):** a skill that produces an artifact MUST ship a runnable test
  or eval asserting correctness (docx-cleanup → assert 0 leaked XML; eval-harness → run
  examples.json). Applies only to artifact-producing skills, not pure-procedure skills.
- **Provenance hardening:** all `scheung1206/skills` commits ONLY from personal Mac; work-derived
  improvements to a forked generic skill stay work IP (never pasted back to personal).

## 8c. Deferred (avoid overengineering at current scale — revisit later)

- **#6 Publish-converter** (auto-convert `generic/` to target-tool format). Defer: only 2 tools
  (Hermes + Claude); manual adapt is ~30s. Build when skill count >10.
- **#8 Observability traces** (log prompt/model/tokens/result per run). Defer: covered 80% by
  CHANGELOG `model:` field; add real traces at agent volume.
- **Mandatory skill-self-test harness** beyond artifact skills. Defer: #5 covers artifact skills;
  expand only if library scales to team/40+ skills.

---

## 9. Pending (resolve at/after approval)

- [ ] Author `gen-index.py` (walks tiers, parses frontmatter, emits INDEX.md; warn if SKILL.md
      newer than its CHANGELOG).
- [ ] Implement the THREE `dev/` skills: orchestration (w/ injection step), tdd-gate,
      documentation-workflow — each with frontmatter (status/env), references/ as needed, CHANGELOG
      with model: field, Non-use note, runnable test where artifact-producing.
- [ ] Author `CONTRIBUTING.md` (how to add a skill, run gen-index, tier meanings, naming
      `projects/<project>/` not dot-prefixed).
- [ ] Git-init `scheung1206/skills` and push (provenance proof; commit only from personal Mac).


- Work-employer-specific code, architecture, or internal systems.
- Binary assets, secrets, credentials, client data.
- The actual implementation of Stephen's projects (only their *playbooks* live here).
