---
name: orchestration
tier: dev
description: Use when a non-trivial development task should be decomposed across orchestrator, implementer, and independent reviewer roles behind a pull-request review gate.
tools: [delegation, terminal, file]
status: active
env: macos>=12
---

# Orchestration

## Trigger
- Load this skill when a non-trivial development task benefits from separate orchestration, implementation, and review roles.

## Steps
1. Decompose the request into bounded tasks, acceptance checks, and ownership for an orchestrator, implementer, and different reviewer.
2. Scan `INDEX.md` descriptions for relevant skills, load each matched `SKILL.md` and any sanitized `references/`, and inject that content into each sub-agent brief because sub-agents do not self-discover skills.
3. Brief the implementer with the task, acceptance checks, matched skill content, branch name, and requirement to write code and open a PR without merging.
4. Brief the reviewer with the matched skill content, TDD or tests, acceptance checks, and implementer output; require the reviewer to be a different agent from the implementer.
5. Assign models deliberately: use an expensive, slow model for review because calls are few and correctness value is high; use cheap, fast models for high-volume orchestration and implementation where marginal value is lower.
6. Use this model configuration as a starting point, swapping agents freely while preserving the role pattern:
   ```text
   Personal: orchestrator=Hermes (free), implementer=Codex (gpt-5.6-sol), reviewer=Claude (Opus/Max)
   Work:     orchestrator=Sonnet,        implementer=Sonnet,               reviewer=Opus
   ```
7. Require the implementer to work on a branch, commit the output, and open a PR; never enable auto-merge or merge the PR.
8. Require the independent reviewer to inspect the branch and tests, then post its findings **as comments in the MR** for the owner's review.
9. **MR comment discipline (mandatory):** all agent review activity happens *in the MR*, not in
   private/side channels, and agents must **actively participate in the MR comment threads** —
   not just post once and leave:
   - Each agent posts its review comments **as comments on the MR** (or inline on the diff).
   - **The implementer MUST actively respond to every reviewer comment:** reply in the same thread,
     address the concern (fix committed + linked, or justify why not), and resolve the thread.
     Silence on a reviewer comment is not allowed — every thread reaches a resolved state.
   - **The reviewer MUST actively re-review after the implementer's fix** and reply in-thread
     confirming the concern is resolved (or re-raising it). The review loop continues until the
     reviewer signals done — in the MR, not elsewhere.
   - **Every comment is labeled with the commenting role + model**, format:
     `(Implementer: <model>)` e.g. `(Implementer: Codex)`, and `(Reviewer: <model>)` e.g.
     `(Reviewer: Claude)`. This makes the audit trail unambiguous about who said what.
   - The orchestrator may also post a coordinating comment labeled `(Orchestrator: <model>)`
     and is responsible for keeping the MR thread moving toward resolution.
10. Have the orchestrator rerun relevant checks and inspect the actual diff before trusting either sub-agent's report.
11. Stop at the review gate and leave the merge decision to the owner.

## Pitfalls
- DON'T assume sub-agents discover or load repository skills without explicit injection.
- DON'T let the implementer review its own work or reuse the same agent as reviewer.
- DON'T spend the highest-cost model on every high-volume dispatch by default.
- DON'T trust completion claims without inspecting the diff and rerunning checks.
- DON'T push directly to `main`, enable auto-merge, or merge before the owner approves the PR.
- DON'T let agents report review findings anywhere but the MR (no side docs/chat). Every MR
  comment MUST carry its role+model label `(Implementer: <model>)` / `(Reviewer: <model>)`. Agents
  MUST actively participate in MR threads — implementer addresses every reviewer comment, reviewer
  re-reviews after fixes; silence on a thread is not allowed.

## Verify
- Assert that the branch has a PR against `main`, auto-merge is disabled, the implementer and reviewer are different agents, both briefs include the matched skill content, and the orchestrator's recorded checks pass.
- Assert MR comment discipline: all agent findings are posted as MR comments (not side channels),
  agents actively participate in MR threads (implementer addresses every reviewer comment and
  resolves it; reviewer re-reviews after fixes and confirms), and every comment is labeled with
  its role+model e.g. `(Implementer: Codex)`, `(Reviewer: Claude)`.

## Non-use / Scope
- Do not spin agents for tiny edits, deterministic scripts, or security-critical paths; handle those directly or use a dedicated security-controlled workflow.
