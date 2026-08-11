# orchestration — Changelog

## v1.0.0 — 2026-08-06
- ADDED: Role-separated orchestration, explicit skill injection, model assignment guidance, and a branch-to-PR review gate.
- DECISION: Separate implementation from review and reserve the strongest model for sparse, high-value review calls to improve correctness at controlled cost.
- MODEL: validated against Hermes+Codex+Claude.
- REJECTED: Automatic skill discovery by sub-agents and auto-merging after automated review because neither preserves the required control boundary.
