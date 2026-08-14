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

## Related skills
- `tdd-gate` — orchestration invokes this as the SPEC GATE: the executable spec (runnable test) is committed and owner-approved BEFORE implementation, defining "correct" (lives in this repo).
- `claude-code` — dispatch implementer/reviewer as Claude Code sub-agents (Hermes skill; not yet in this repo).
- `codex` — dispatch as OpenAI Codex CLI agents (Hermes skill; not yet in this repo).
- `subagent-driven-development` — context-budget and parallel-worktree mechanics (Hermes skill; not yet in this repo).
- eval-harness pattern — acceptance checks must be runnable assertions (see `generic/eval-harness`, planned; until then: a check is assertable if a command/assertion passes or fails).

## Steps
1. Decompose the request by **architectural seam, not size**. Parallelize only independent pieces that cannot conflict (separate worktrees/files); serialize dependent tasks. If a task comfortably fits one agent's context, keep it as one agent — splitting a small task is itself over-engineering. Produce bounded tasks, acceptance checks, and role ownership.
2. Author **one canonical task brief** (Goal / Constraints / Out-of-scope) plus an **executable spec (TDD artifact)** as the single source of truth. The executable spec is a committed, runnable test or assertion list — produced via the `tdd-gate` skill — that fails before implementation and passes only when the task is correctly built. This artifact, not the prose brief, is the definition of "correct." The brief's positive and negative use cases become the spec's test cases (see the eval-harness pattern for the generic runner).
3. **Owner brief & sign-off (gate before dispatch).** Produce a concise owner-facing brief: the Goal, the exact use cases being tackled (including **positive AND negative cases**), and the executable spec. Obtain owner sign-off on BOTH the brief and the executable spec **before** dispatching the implementer — the owner is approving the *definition of done* (the runnable test), not merely a description. Do not spend implementation tokens until the owner approves.
4. Scan `INDEX.md` descriptions for relevant skills, load each matched `SKILL.md` and any sanitized `references/`, and inject that content into each sub-agent brief because sub-agents do not self-discover skills. Because the orchestrator already produced and obtained owner sign-off on the executable spec in Step 3 (which IS tdd-gate's green-light, not a separate approval), the implementer does NOT re-run tdd-gate's gate — it executes only tdd-gate Steps 7-8: implement just enough to satisfy the approved artifact, then open the PR.
5. Brief the implementer with the canonical task brief, matched skill content, branch name, and requirement to write code and open a PR without merging. The implementer builds **only** to the approved executable spec and does not expand scope beyond the brief and its approved spec.
6. Brief the reviewer with the **same canonical task brief, identical to what the implementer received**, plus the matched skill content, TDD or tests, and implementer output. Require the reviewer to be a different agent from the implementer and to judge the output against the orchestrator's stated task. The reviewer MUST run the exact TDD command the owner approved and confirm it passes, and that the brief's positive and negative use cases are represented as cases in the artifact — judgment of fitness is against the approved spec, not the implementer's retrofit.
7. Assign models deliberately: use an expensive, slow model for review because calls are few and correctness value is high; use cheap, fast models for high-volume orchestration and implementation where marginal value is lower.
8. Require the implementer to work on a branch, commit the output, and open a PR; never enable auto-merge or merge the PR.
9. Require the independent reviewer to inspect the branch and tests, then post its findings **as comments in the MR** for the owner's review.
10. **MR comment discipline (mandatory):** all agent review activity happens *in the MR*, not in private/side channels, and agents must **actively participate in the MR comment threads** — not just post once and leave:
   - Each agent posts its review comments **as comments on the MR** (or inline on the diff).
   - **The implementer MUST actively respond to every reviewer comment:** reply in the same thread, address the concern (fix committed + linked, or justify why not), and resolve the thread. Silence on a reviewer comment is not allowed — every thread reaches a resolved state.
   - **The reviewer MUST actively re-review after the implementer's fix** and reply in-thread confirming the concern is resolved (or re-raising it). The review loop continues until the reviewer signals done — subject to the **two-round limit in Step 11** — in the MR, not elsewhere.
   - **Every comment is labeled with the commenting role + model**, format: `(Implementer: <model>)` e.g. `(Implementer: Codex)`, and `(Reviewer: <model>)` e.g. `(Reviewer: Claude)`. This makes the audit trail unambiguous about who said what.
   - The orchestrator may also post a coordinating comment labeled `(Orchestrator: <model>)` and is responsible for keeping the MR thread moving toward resolution.
11. **Review round limit (anti-spiral).** Allow at most **two review rounds**: Implementer → Reviewer → Implementer → Reviewer. After round 2, **stop further implementation and escalate to the owner**; the implementer does not proceed without an explicit owner decision. This caps review/implementation loops that would otherwise run indefinitely.
12. Have the orchestrator rerun relevant checks and inspect the actual diff before trusting either sub-agent's report.
13. Stop at the review gate and leave the merge decision to the owner.
14. **Learning loop.** After merge, capture what worked and what failed back into the skill (a CHANGELOG entry or a revision) so the library's process knowledge compounds. Do not treat a merged task as fire-and-forget.

## Black-box fitness review (reviewer mandate)
- The reviewer's job is **not** to confirm only that the code compiles, runs, or lints, or that it
  "looks reasonable." The reviewer must confirm that the output is **fit for the orchestrator's
  task** through a black-box check against the canonical brief.
- For every change the implementer made, the reviewer MUST explicitly answer:
  - **"Why do we need this?"** Is the change necessary; does it earn its place, or is it
    speculative?
  - **"Is there a better / simpler way?"** Were simpler alternatives considered, and did the
    implementation choose the minimal approach?
  - **"Does this actually solve the problem?"** Does it satisfy the orchestrator's Goal + the approved executable spec (its positive and negative cases), or does it merely resemble a solution?
  - **"Are we overthinking / over-engineering it?"** AI agents tend to spiral by adding
    abstractions, edge-case handling, and speculative features beyond the brief. Flag and cut
    anything that does not map to an acceptance check.
  - **"Does this violate a stated Constraint?"** The brief lists hard Constraints the work must
    respect; the reviewer confirms nothing breaks them (e.g. "no new dependencies," "personal Mac
    only," "projects/ never exported"). A constraint breach is a fail regardless of how clean the code.
- The reviewer challenges necessity and scope and may request removal of code that does not trace
  to an acceptance check.
- **Granularity guard:** answer the five questions in a **PR-level summary** plus detail only for *notable* changes (new behavior, removed code, architectural shifts) — not a per-file enumeration. Per-file review is itself a spiral risk this framework exists to prevent.

## Pitfalls
- DON'T assume sub-agents discover or load repository skills without explicit injection.
- DON'T let the implementer review its own work or reuse the same agent as reviewer.
- DON'T let the reviewer only verify that the code runs or is clean; it must judge fitness to the
  orchestrator's task through the five questions above.
- DON'T let the implementer add features or abstractions beyond the brief; the reviewer must flag
  scope creep and gold-plating.
- DON'T let the orchestrator's brief be vague; vague briefs cause both under- and over-building,
  so the brief must state Goal + Constraints + Out-of-scope, and the executable spec (TDD artifact) carries the acceptance cases.
- DON'T spend the highest-cost model on every high-volume dispatch by default.
- DON'T trust completion claims without inspecting the diff and rerunning checks.
- DON'T push directly to `main`, enable auto-merge, or merge before the owner approves the PR.
- DON'T let agents report review findings anywhere but the MR (no side docs/chat). Every MR
  comment MUST carry its role+model label `(Implementer: <model>)` / `(Reviewer: <model>)`. Agents
  MUST actively participate in MR threads — implementer addresses every reviewer comment, reviewer
  re-reviews after fixes; silence on a thread is not allowed.
- DON'T write acceptance checks as prose; they must be runnable assertions the reviewer executes (eval-harness pattern).
- DON'T split a task that fits one agent; splitting by size instead of architectural seam adds coordination cost and integration risk.
- DON'T run more than two review rounds without owner escalation; silence past round 2 is not allowed.
- DON'T dispatch the implementer before the owner has signed off the brief (Step 3).

## Verify
- Assert that the branch has a PR against `main`, auto-merge is disabled, the implementer and reviewer are different agents, both briefs include the matched skill content, and the orchestrator's recorded checks pass.
- Assert that the reviewer brief contains the **identical canonical task brief** the implementer
  received, and that the reviewer's posted findings explicitly address all five fitness questions
  for every change (or state why a question is N/A for a given change).
- Assert MR comment discipline: all agent findings are posted as MR comments (not side channels),
  agents actively participate in MR threads (implementer addresses every reviewer comment and
  resolves it; reviewer re-reviews after fixes and confirms), and every comment is labeled with
  its role+model e.g. `(Implementer: Codex)`, `(Reviewer: Claude)`.
- Assert the owner signed off the brief (Step 3) before the implementer was dispatched — evidence is the owner's explicit approval message (or a posted `(Owner: approved)` comment on the brief), not merely the brief's existence.
- Assert the review loop escalated to the owner once it reached round 2 (no round 3 without an explicit owner decision) — if the reviewer approved at round 1, this asserts only that the cap was not exceeded.
- Assert acceptance checks are assertable (runnable) and the reviewer executed them rather than only reading.
- Assert review findings include a PR-level summary (granularity guard).
- Assert a post-merge learning-loop entry was captured (a CHANGELOG update or skill revision noting what worked/failed).
- Assert the TDD artifact commit precedes the implementation commit (tdd-gate rule) and the owner approved the artifact before implementation began — proving the agent built to an owner-approved definition of "correct," not a self-defined one.

## Non-use / Scope
- Do not spin agents for tiny edits, deterministic scripts, or security-critical paths; handle those directly or use a dedicated security-controlled workflow.
