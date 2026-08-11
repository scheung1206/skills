# orchestration — Changelog

## v1.1.0 — 2026-08-11
- CHANGED: Added mandatory MR comment discipline — agents post findings as MR comments (not side channels), reply in MR comment threads, and label every comment with role+model, e.g. `(Implementer: Codex)`, `(Reviewer: Claude)`, `(Orchestrator: Hermes)`.
- DECISION: Per Stephen's PR review — agent review activity must be auditable inside the MR with an unambiguous who-said-what trail, so the PR is the single source of review truth.
- MODEL: validated against Hermes+Codex+Claude.
- REJECTED: reporting findings in chat/side docs (no audit trail) and unlabeled comments (ambiguous authorship).


- ADDED: Role-separated orchestration, explicit skill injection, model assignment guidance, and a branch-to-PR review gate.
- DECISION: Separate implementation from review and reserve the strongest model for sparse, high-value review calls to improve correctness at controlled cost.
- MODEL: validated against Hermes+Codex+Claude.
- REJECTED: Automatic skill discovery by sub-agents and auto-merging after automated review because neither preserves the required control boundary.
