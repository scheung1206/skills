---
name: orchestration
tier: dev
description: Use when a non-trivial development task should be decomposed across orchestrator, implementer, and independent reviewer roles behind a pull-request review gate. Reviewer criteria follow Google's eng-practices standard (CC BY 3.0) adapted for AI agents. Process adherence is enforced by verify.py.
tools: [delegation, terminal, file]
status: active
env: macos>=12
---

# Orchestration

## Trigger
Load this skill when a non-trivial development task benefits from separate orchestration, implementation, and review roles behind a PR gate.

## Core rules (canonical — referenced everywhere, stated once)
These are the only hard rules. Everything else elaborates them.
- **R1 — Owner sign-off before dispatch.** The owner approves the canonical brief + executable spec (the TDD artifact) *before* any implementation tokens are spent.
- **R2 — Spec is the definition of "correct."** The owner-approved TDD artifact (via `tdd-gate`) is what "done" means; it is committed *before* implementation and the agent builds only to it.
- **R3 — Separate roles.** Orchestrator, implementer, and reviewer are distinct; implementer ≠ reviewer (different agent/model).
- **R4 — Review gate, owner decides merge.** Independent reviewer judges fitness; the owner merges. Never auto-merge.
- **R5 — MR is the single source of truth.** All agent activity lives as labeled MR comments; no side channels.
- **R6 — Cap the loop.** At most two review rounds; after round 2, escalate to owner. No round 3 without explicit owner decision.
- **R7 — Verify, don't trust.** The orchestrator runs `verify.py` against the MR and inspects the actual diff; completion claims are not accepted on faith.
- **R8 — Authoring split.** Code logic → implementer model (e.g. Codex) + independent review. Skill/prose the owner directs line-by-line → orchestrator authors directly (disclosed).
- **R9 — Enterprises/parallelism:** for parallel fan-out, pre-declare non-overlapping file ownership per sub-agent; review stays centralized/sequential (see Modes).

## Steps (core flow)
1. **Decompose by architectural seam, not size.** Produce bounded tasks, acceptance checks, and role ownership. If it fits one agent's context, keep it one agent — splitting by size is over-engineering. *(See Modes → Parallel for fan-out.)*
2. **Author the canonical brief + executable spec.** Goal / Constraints / Out-of-scope brief, plus a runnable TDD artifact (via `tdd-gate`) as the single source of truth. Brief's positive/negative use cases become the spec's test cases.
3. **Owner sign-off (R1/R2 gate).** Present the brief + spec; obtain owner approval of *both* before dispatch. Do not spend implementation tokens until approved.
4. **Inject skills + brief agents.** Scan `INDEX.md`, load matched `SKILL.md`/`references/`, inject into each sub-agent brief (sub-agents do not self-discover). Brief implementer and reviewer with the *identical* canonical brief + matched skill content + approved TDD command.
5. **Implement (R3/R2).** Implementer works on a branch, builds only to the approved spec, opens a PR, never merges.
6. **Review (R3/R4).** Independent reviewer (different agent) runs the approved TDD command, traces each acceptance check (pass/fail + how verified), and writes one honest verdict paragraph (see Reviewer standard). Posts findings as MR comments.
7. **MR discipline (R5/R6).** Every comment labeled `(Role: <model>)`. Implementer addresses every reviewer comment and resolves it; reviewer re-reviews after fixes. Loop until reviewer signals done, capped at two rounds (R6).
8. **Verify + gate (R7/R4).** Orchestrator runs `python3 verify.py --pr <n>`; all gates must pass. Stop at the gate; owner merges.
9. **Learning loop.** After merge, capture what worked/failed into CHANGELOG (a DECISION/REJECTED line). Not fire-and-forget.

## Reviewer standard (adapted from Google eng-practices, CC BY 3.0)
**Purpose:** ensure the change improves the task's outcome without degrading the system; favor approving once it clearly improves what we set out to build, even if imperfect. Seek continuous improvement, not perfection.

**What the reviewer looks for (priority order):** (1) Design — pieces fit, belongs here, integrates well; (2) Functionality — does it do what the approved spec says; verify by *running* the approved TDD command, not trusting claims; (3) Complexity/over-engineering — the primary anti-spiral safeguard: solve the problem we know needs *now*, not a speculative future; (4) Tests — acceptance checks correct and runnable; (5) Naming/comments/style — clear, explain *why*; `Nit:` for non-blocking polish; (6) Context — whole file/system, not just the diff.

**How to deliver (flows, not a checklist):** trace the spec first (each check: pass/fail + command run — machine-checkable), then one verdict paragraph. Block only on real degradation (spec failure, constraint breach, genuine over-engineering). Technical facts/data overrule opinions.

**Granularity (deliberate deviation from Google's "Every Line"):** review at MR change-set level (notable changes only), not every line — line-by-line enumeration is itself the spiral risk, and the spec-trace covers correctness. Small high-risk diffs may still go line-by-line.

## Modes (optional elaborations)
- **Parallel fan-out.** When Step 1 yields seam-independent pieces, fan out as background leaf sub-agents (depth=1) with **pre-declared non-overlapping file ownership** (mandatory — prevents silent overwrites). Concurrency capped by the tool's max-concurrent-children (illustrated as 3); raise only with real independent seams. Owner sign-off (Step 3) + spec (Step 2) precede fan-out; fan-in verifies actual disk output (R7), then centralized sequential review (Step 6). Review does NOT parallelize. Don't parallelize dependent tasks, or when you can't declare ownership.
- **Lightweight (future).** Collapse the separate reviewer agent into a runnable eval harness the owner executes directly, keeping the spec-trace. Not yet built.

## Failure off-ramp
If the reviewer and implementer are stuck (same concern reopened, or spec is ambiguous mid-flight): the orchestrator posts a `(Orchestrator: <model>)`comment stating the blocker, and **escalates to the owner immediately** — do not burn round 2 on a loop. If the spec itself is ambiguous, return to Step 2/3 (re-author + re-sign-off), don't patch around it.

## Pitfalls
- DON'T let implementer == reviewer, or auto-merge, or merge before owner approval (R3/R4).
- DON'T dispatch before owner sign-off (R1) or without a runnable spec (R2).
- DON'T trust completion claims — run `verify.py` and inspect the diff (R7).
- DON'T parallelize without pre-declared non-overlapping file ownership, or parallelize review.
- DON'T write acceptance checks as prose — they must be runnable (eval-harness pattern).
- DON'T split a task that fits one agent; splitting by size adds coordination cost.
- DON'T let agents report anywhere but the MR; every comment carries its `(Role: <model>)` label and threads resolve.

## Verify
Run `python3 verify.py --pr <n>`. The script asserts the objective gates (R1–R7) from git/MR state and exits non-zero on any failure. It does **not** judge code quality (that is the reviewer's job). Gates checked:
- PR targets `main`; auto-merge disabled.
- Implementer ≠ reviewer (parsed from MR labels).
- Owner `(Owner: approved)` comment exists *before* the first implementation commit (R1).
- TDD/spec commit precedes the first implementation commit (R2).
- Reviewer comment contains a spec-trace (PASS/FAIL table) + verdict (R3/R4).
- Every agent comment matches `(Role: <model>)`; both roles commented (R5).
- Reviewer re-review count ≤ 2 before merge (R6).
- If parallel mode used: each sub-agent declared owned paths; orchestrator posted fan-in disk verification.
- CHANGELOG has a post-merge learning-loop entry.

## Non-use / Scope
Do not spin agents for tiny edits, deterministic scripts, or security-critical paths; handle those directly or via a dedicated security-controlled workflow.
