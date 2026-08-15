---
name: orchestration
tier: dev
description: Use when a non-trivial development task should be decomposed across orchestrator, implementer, and independent reviewer roles behind a pull-request review gate. Reviewer criteria follow Google's eng-practices standard (CC BY 3.0) adapted for AI agents.
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

## Design decisions (why this skill is structured this way)
- **One coordinating skill, not three.** Implementer and reviewer are ROLES (prompts + swappable model assignments in Step 7), not separate skills. The coordination value — the shared canonical brief, the 2-round cap, the owner sign-off gate, the MR-thread discipline — is cross-cutting state that must NOT be passed across files where it can drift. Splitting into implementer/reviewer/coordinator skills would add integration risk for no new capability. Extract a standalone `dev/code-review` skill ONLY if reviewing non-orchestrated PRs becomes a real need.
- **Principle-led review, not a checklist.** A mandated question-list produces ritual compliance (boilerplate hitting each box) rather than judgment — the exact AI-spiral failure this skill targets. We adopt Google's eng-practices standard (CC BY 3.0) and let the reviewer write one honest verdict, anchored to the runnable spec.
- **Spec is the definition of "correct."** The owner-approved TDD artifact (via tdd-gate) is what "done" means, reviewed before any code — so agents build/validate the correct thing instead of reinterpreting a prose brief.
- **Code delegates to the implementer model; skills are authored by the orchestrator.** Application *code logic* always goes to the configured implementer model (e.g. Codex) with independent review — never authored by the orchestrator. *Skill/prose documentation* that the owner is directing line-by-line is authored directly by the orchestrator as the typing surface (disclosed, not silently delegated). This split keeps code under the review gate while avoiding needless delegation overhead on prose the owner is shaping in real time.
- **Parallelism is for the conflict-free implementation leg, not review.** Fan-out N seam-independent implementers (background, depth-1, pre-declared file ownership); keep review centralized and sequential post-fan-in. Parallel review is wrong because it needs the whole picture and is cheap in calls. The concurrency cap (illustrated as 3) is a coordination budget, not a hard law — raise only with real independent seams.

## Steps
1. Decompose the request by **architectural seam, not size**. Parallelize only independent pieces that cannot conflict (separate worktrees/files); serialize dependent tasks. If a task comfortably fits one agent's context, keep it as one agent — splitting a small task is itself over-engineering. Produce bounded tasks, acceptance checks, and role ownership.

### Parallel execution (autonomous fan-out)
*Executes after the Step 3 owner sign-off — placed here because it operationalizes Step 1's decomposition.* When Step 1 yields **seam-independent** pieces (each owns distinct files / a distinct worktree / a distinct interface with no read-write overlap), execute them as a **parallel fan-out** rather than serially:
- **Fan-out (background, concurrent).** Dispatch the pieces as background leaf sub-agents via your delegation tool's concurrent-dispatch mechanism. They run concurrently in isolated sessions; results consolidate on completion. The orchestrator stays alive to do fan-in. Concurrency is capped by the tool's max-concurrent-children setting (illustrated here as **3**) — raise it only when you genuinely have more independent seams; forcing N agents on fewer seams just makes them wait or collide.
- **Pre-declare file ownership (mandatory).** Each sub-agent is told the exact paths it owns and forbidden from touching any other. This is the contract that prevents silent overwrites — the #1 failure of autonomous agent teams. Without it, do not parallelize.
- **Depth = 1.** Sub-agents are leaves (no further delegation); they cannot spawn agents of their own. One orchestrator → N implementers is the correct ceiling; deeper nesting is where coordination rots.
- **Owner sign-off (Step 3) and the TDD spec (Step 2) happen BEFORE fan-out**, and the spec must be unambiguous enough that N agents cannot interpret it differently. This is why the correctness gate is the prerequisite, not optional.
- **Fan-in → centralized review (sequential).** Once all implementers report, the orchestrator verifies actual output on disk (trust-but-verify, Step 12) — not just self-reports. Review stays **one agent, sequential, after fan-in** (Steps 6/9/10): review needs the whole picture and is cheap in model calls, so it does NOT parallelize. The 2-round cap (Step 11) applies at this review tier.
- **When NOT to parallelize:** dependent tasks (shared mutable state, one agent's output is another's input), tasks that fit one agent's context, or when you cannot pre-declare non-overlapping ownership. Serialize those.
2. Author **one canonical task brief** (Goal / Constraints / Out-of-scope) plus an **executable spec (TDD artifact)** as the single source of truth. The executable spec is a committed, runnable test or assertion list — produced via the `tdd-gate` skill — that fails before implementation and passes only when the task is correctly built. This artifact, not the prose brief, is the definition of "correct." The brief's positive and negative use cases become the spec's test cases.
3. **Owner brief & sign-off (gate before dispatch).** Produce a concise owner-facing brief: the Goal, the exact use cases being tackled (including **positive AND negative cases**), and the executable spec. Obtain owner sign-off on BOTH the brief and the executable spec **before** dispatching the implementer — the owner is approving the *definition of done* (the runnable test), not merely a description. Do not spend implementation tokens until the owner approves.
4. Scan `INDEX.md` descriptions for relevant skills, load each matched `SKILL.md` and any sanitized `references/`, and inject that content into each sub-agent brief because sub-agents do not self-discover skills. Because the orchestrator already produced and obtained owner sign-off on the executable spec in Step 3 (which IS tdd-gate's gate, not a separate approval), the implementer does NOT re-run tdd-gate's gate — it executes only tdd-gate Steps 7-8: implement just enough to satisfy the approved artifact, then open the PR.
5. Brief the implementer with the canonical task brief, matched skill content, branch name, and requirement to write code and open a PR without merging. The implementer builds **only** to the approved executable spec and does not expand scope beyond the brief and its approved spec.
6. Brief the reviewer with the **same canonical task brief, identical to what the implementer received**, plus the matched skill content, the approved TDD command, and implementer output. Require the reviewer to be a different agent from the implementer and to judge the output against the orchestrator's stated task. The reviewer MUST run the exact TDD command the owner approved and confirm it passes, and that the brief's positive and negative use cases are represented as cases in the artifact — judgment of fitness is against the approved spec, not the implementer's retrofit.
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

## Reviewer standard (adapted from Google eng-practices, CC BY 3.0)
The reviewer's primary purpose is to ensure the change **improves the task's outcome** without degrading the system. In general, **favor approving a change once it is in a state where it clearly improves what we set out to build, even if it isn't perfect.** Seek continuous improvement, not perfection. There is no "perfect" change — only better.

### What the reviewer looks for (in priority order)
1. **Design** — Do the pieces fit? Does the change belong here, or in a library / different layer? Does it integrate well with the rest of the system? Is now the right time?
2. **Functionality** — Does it do what we intended (per the approved spec)? Is what we intended actually good for the user/owner? Think about edge cases; the reviewer should reason about bugs by reading, not assume the implementer tested them. **The reviewer verifies functionality by running the approved TDD command** (orchestrator-authored, owner-approved — not the implementer's retrofit), not by trusting the implementer's claim.
3. **Complexity / over-engineering** — Is the change more complex than it needs to be? A particular failure mode: **over-engineering** — making the code more generic than needed, or adding functionality not presently required. **Reviewers must be especially vigilant about this.** Solve the problem we know needs solving *now*; do not build for a future we haven't reached. This is the primary anti-spiral safeguard.
4. **Tests** — Are the acceptance checks correct, sensible, and useful? Do they actually fail when the code is broken? (For AI-generated changes, the reviewer runs them — see Step 6.)
5. **Naming / comments / style** — Clear names; comments explain *why*, not *what*; follow existing style. Non-critical polish gets a `Nit:` prefix and is not blocking.
6. **Context** — Look at the whole file/system, not just the diff. Don't accept changes that degrade overall system health through small added complexity.

### How to deliver the review (flows, not a checklist)
- **Trace the spec first.** For each approved acceptance check, state `pass/fail + how verified` (the command run). This is the objective core and is machine-checkable.
- **Then one verdict paragraph.** In plain prose: *Does this do what we set out to build? What would I cut or change, and why?* The "what I'd cut" naturally covers necessity, simplicity, and over-engineering — the reviewer need not hit separate boxes.
- **Block only on real degradation:** spec failure, constraint breach, or genuine over-engineering. Everything else is a `Nit:` or an optional suggestion.
- **Technical facts/data overrule opinions.** Design is weighed on principles, not personal preference.
- **Granularity (deliberate deviation from Google's "Every Line"):** Google expects human reviewers to read every line. For AI-agent review at volume, we instead review at the MR change-set level — each *notable* change (new behavior, removed code, architectural shifts, new deps), not every line or file. Trivial lines are covered by the overall verdict. This is a conscious tradeoff: line-by-line enumeration is exactly the review-spiral risk this skill exists to prevent, and the objective spec-trace (above) already covers correctness. If a diff is small and high-risk, the reviewer may still go line-by-line.

## Pitfalls
- DON'T assume sub-agents discover or load repository skills without explicit injection.
- DON'T let the implementer review its own work or reuse the same agent as reviewer.
- DON'T let the reviewer only verify that the code runs or is clean; it must judge fitness to the orchestrator's task by tracing the approved spec and writing an honest verdict.
- DON'T let the implementer add features or abstractions beyond the brief; the reviewer must flag scope creep and gold-plating (especially over-engineering — see Reviewer standard §3).
- DON'T let the orchestrator's brief be vague; vague briefs cause both under- and over-building, so the brief must state Goal + Constraints + Out-of-scope, and the executable spec (TDD artifact) carries the acceptance cases.
- DON'T write acceptance checks as prose; they must be runnable assertions the reviewer executes (eval-harness pattern).
- DON'T split a task that fits one agent; splitting by size instead of architectural seam adds coordination cost and integration risk.
- DON'T run more than two review rounds without owner escalation; silence past round 2 is not allowed.
- DON'T dispatch the implementer before the owner has signed off the brief (Step 3).
- DON'T spend the highest-cost model on every high-volume dispatch by default.
- DON'T trust completion claims without inspecting the diff and rerunning checks.
- DON'T push directly to `main`, enable auto-merge, or merge before the owner approves the PR.
- DON'T parallelize without pre-declared, non-overlapping file ownership per sub-agent — silent overwrites are the #1 failure of autonomous agent teams. If you can't declare it, serialize.
- DON'T parallelize review or run more than one reviewer concurrently; review needs the whole picture and is cheap in model calls. Fan-out implementation, centralize review.
- DON'T raise the concurrency cap beyond the number of genuinely independent seams you have; forcing N agents on fewer seams just makes them wait or collide.
- DON'T let agents report review findings anywhere but the MR (no side docs/chat). Every MR comment MUST carry its role+model label. Agents MUST actively participate in MR threads — implementer addresses every reviewer comment, reviewer re-reviews after fixes; silence on a thread is not allowed.

## Verify
- Assert that the branch has a PR against `main`, auto-merge is disabled, the implementer and reviewer are different agents, both briefs include the matched skill content, and the orchestrator's recorded checks pass.
- Assert that the reviewer brief contains the **identical canonical task brief** the implementer received, and that the reviewer's posted findings (a) trace each approved acceptance check pass/fail with evidence (the command run), and (b) include a verdict paragraph — not a per-question checklist.
- Assert MR comment discipline: all agent findings are posted as MR comments (not side channels), agents actively participate in MR threads (implementer addresses every reviewer comment and resolves it; reviewer re-reviews after fixes and confirms), and every comment is labeled with its role+model e.g. `(Implementer: Codex)`, `(Reviewer: Claude)`.
- Assert the owner signed off the brief (Step 3) before the implementer was dispatched — evidence is the owner's explicit approval message (or a posted `(Owner: approved)` comment on the brief), not merely the brief's existence.
- Assert the review loop escalated to the owner once it reached round 2 (no round 3 without an explicit owner decision) — if the reviewer approved at round 1, this asserts only that the cap was not exceeded.
- Assert acceptance checks are assertable (runnable) and the reviewer executed them rather than only reading.
- Assert a post-merge learning-loop entry was captured (a CHANGELOG update or skill revision noting what worked/failed).
- Assert the TDD artifact commit precedes the implementation commit (tdd-gate rule) and the owner approved the artifact before implementation began — proving the agent built to an owner-approved definition of "correct," not a self-defined one.
- If parallel fan-out was used: assert each sub-agent was given pre-declared, non-overlapping file ownership; that owner sign-off (Step 3) and the TDD spec (Step 2) preceded the fan-out; and that fan-in verification inspected actual output on disk (not just self-reports) before the centralized sequential review (Steps 6/9/10).

## Non-use / Scope
- Do not spin agents for tiny edits, deterministic scripts, or security-critical paths; handle those directly or use a dedicated security-controlled workflow.
