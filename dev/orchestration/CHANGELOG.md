# orchestration — Changelog

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
