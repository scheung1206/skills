# orchestration — Changelog

## v1.0.0 — 2026-08-06
- ADDED: Role-separated orchestration (orchestrator / implementer / independent reviewer), explicit
  skill injection into sub-agent briefs, model-assignment guidance (strong model on sparse
  high-value review; cheap model on high-volume orchestration/implementation), and a
  branch-to-PR review gate (never auto-merge; merge decision is Stephen's).
- ADDED (during PR #1 iteration, pre-merge): mandatory MR comment discipline — agents post
  findings as MR comments (not side channels), reply to each other in MR comment threads, and
  label every comment with role+model, e.g. `(Implementer: Codex)`, `(Reviewer: Claude)`,
  `(Orchestrator: Hermes)`. Comments must communicate the CODE DECISION (what was decided and
  why) so the review trail is auditable.
- DECISION: Separate implementation from review and reserve the strongest model for sparse,
  high-value review calls to improve correctness at controlled cost. Per Stephen's PR review,
  agent review activity must be auditable inside the MR with an unambiguous who-said-what trail,
  so the PR is the single source of review truth.
- MODEL: validated against Hermes+Codex+Claude.
- REJECTED: Automatic skill discovery by sub-agents, auto-merging after automated review, and
  reporting findings in chat/side docs or with unlabeled comments (no audit trail / ambiguous
  authorship).
- NOTE: Version stays v1.0.0 through PR iteration. Version increments ONLY after merge to main.
