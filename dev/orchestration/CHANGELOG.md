# orchestration — Changelog

## v1.1.0 — 2026-08-14 (MERGED via #3)
- CHANGED: Replaced the mandated 5-question reviewer checklist with Google's eng-practices reviewer standard (CC BY 3.0), adapted for AI agents. The reviewer judges "does this improve the task's outcome without degrading the system," in priority order: design → functionality → complexity/over-engineering → tests → naming/comments/style → context. Over-engineering is called out as the primary anti-spiral safeguard ("solve the problem we know needs solving now").
- CHANGED: Reviewer delivers via spec-trace (each approved acceptance check: pass/fail + command run) + one honest verdict paragraph — not a per-question checklist. Granularity is MR change-set level, not per line. Blocking reserved for spec failure, constraint breach, or genuine over-engineering; everything else is a `Nit:`.
- CHANGED: Added owner sign-off gate before dispatch (Step 3, with positive+negative use cases + executable spec), TDD correctness spec as the definition of "correct" (Steps 2/4/6, via tdd-gate), hard two-round review cap escalating to owner (Step 11), seam-not-size decomposition (Step 1), and post-merge learning loop (Step 14).
- DECISION: A mandated checklist produced ritual compliance (boilerplate hitting each box) rather than judgment — the exact AI-spiral failure the skill targets. Google's principle-led standard flows better and already names over-engineering as the key reviewer vigilance. The executable spec (tdd-gate) gives the reviewer an objective, runnable anchor so "verdict" can't degrade into vague prose.
- DEVIATION (disclosed): Google's "Every Line" review principle is intentionally NOT adopted — AI-agent review at volume uses MR change-set granularity instead, because line-by-line enumeration is itself the spiral risk this skill prevents, and the spec-trace covers correctness objectively. Small high-risk diffs may still go line-by-line. This is documented in the skill, not hidden.
- MODEL: validated against the orchestrator/implementer/reviewer pattern; model assignments remain swappable example configurations in SKILL.md.
- REJECTED: per-file/per-line review enumeration (spiral risk), auto-merging after round 2 (removes owner from the loop), splitting tasks by size rather than seam (integration risk), the 5-box mandated checklist (ritual compliance), and **splitting orchestration into 3 separate skills (implementer / reviewer / coordinator)**.
- DECISION (skill structure): Keep orchestration as ONE coordinating skill. Implementer and reviewer are ROLES (prompts + swappable model assignments), not separate skills. The cross-cutting state — shared canonical brief, 2-round cap, owner sign-off gate, MR-thread discipline — is the coordination value and must not be passed across files where it can drift. Extract a standalone `dev/code-review` skill ONLY if/when reviewing non-orchestrsated PRs becomes a real need; do not preemptively split.
- NOTE: Version incremented to v1.1.0 upon merge to main (PR #3).

## v1.0.0 — 2026-08-06
- ADDED: Role-separated orchestration (orchestrator / implementer / independent reviewer), explicit
  skill injection into sub-agent briefs, model-assignment guidance (strong model on sparse
  high-value review; cheap model on high-volume orchestration/implementation), and a
  branch-to-PR review gate (never auto-merge; merge decision reserved for the human owner).
- ADDED (during PR iteration, pre-merge): mandatory MR comment discipline — agents post findings
  as MR comments (not side channels) and MUST actively participate in MR threads: the implementer
  addresses every reviewer comment and resolves the thread (fix committed + linked, or justified),
  the reviewer re-reviews after fixes and confirms in-thread; silence on a thread is not allowed.
  Every comment labeled with role+model, e.g. `(Implementer: <model>)`, `(Reviewer: <model>)`,
  `(Orchestrator: <model>)`. Comments communicate the CODE DECISION (what was decided and why) so
  the review trail is auditable. Model assignments live in the SKILL.md model-config block.
- DECISION: Separate implementation from review and reserve the strongest model for sparse,
  high-value review calls to improve correctness at controlled cost. Agent review activity must be
  auditable inside the MR with an unambiguous who-said-what trail, so the PR is the single source
  of review truth. The DECISION lines describe rationale only — no personal names — so the skill
  stays reusable and forkable; specific model/agent assignments belong in the model-config block.
- MODEL: validated against the orchestrator/implementer/reviewer pattern (model assignments are
  example configs in SKILL.md, swapped per environment).
- REJECTED: Automatic skill discovery by sub-agents, auto-merging after automated review, and
  reporting findings in chat/side docs or with unlabeled comments (no audit trail / ambiguous
  authorship).
- NOTE: Version stays v1.0.0 through PR iteration. Version increments ONLY after merge to main.
