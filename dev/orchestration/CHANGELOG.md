# orchestration — Changelog

## v1.2.0 — 2026-08-14 (in-flight, pending merge)
- CHANGED: Extended orchestration with an owner sign-off gate before dispatch (Step 3: owner brief with positive AND negative use cases + assertable acceptance checks), a hard two-round review limit escalating to the owner (Step 11), a decomposition rule split by architectural seam not size (Step 1), assertable acceptance checks (eval-harness pattern, Step 2), a review-granularity guard, a post-merge learning loop (Step 14), and cross-references to sibling skills.
- DECISION: The owner must approve the brief before tokens are spent so we do not build the wrong thing confidently; the two-round cap prevents indefinite review/implementation spirals (the exact failure mode the fitness framework targets); assertable checks let the reviewer execute rather than eyeball; the learning loop makes process knowledge compound per the library's stated purpose.
- MODEL: validated against the orchestrator/implementer/reviewer pattern; model assignments remain swappable example configurations in SKILL.md.
- REJECTED: per-file review enumeration (spiral risk), auto-merging after round 2 (removes owner from the loop), and splitting tasks by size rather than seam (integration risk).
- REVIEW-FIXES (post independent black-box review): linked Step 10's unbounded review loop to the Step 11 two-round cap; marked `claude-code`/`codex`/`subagent-driven-development`/`eval-harness` as not-yet-in-this-repo (aspirational, not dead links); added Verify assertions for the learning loop and explicit sign-off evidence; relaxed the round-cap Verify wording so round-1 approval is not misread as requiring escalation.
- NOTE: Version stays v1.2.0 through PR iteration. Version increments ONLY after merge to main.

## v1.1.0 — 2026-08-14 (in-flight, pending merge)
- CHANGED: Added one canonical task brief shared identically with the implementer and reviewer,
  defining Goal, Constraints, Acceptance checks, and Out-of-scope as the task's single source of
  truth. Added a mandatory black-box fitness review in which the reviewer evaluates every change
  for necessity, simplicity, actual problem fit, over-engineering, and constraint breaches.
- DECISION: A shared, explicit brief prevents the implementer and reviewer from optimizing against
  different interpretations, while the five-question fitness framework makes review test whether
  the output satisfies the orchestrator's task instead of stopping at mechanical correctness or
  code cleanliness. The Constraints field was kept (not dropped) and wired into a fifth review
  question because hard limits (no new deps, personal Mac only, projects/ never exported) are
  frequently the first thing AI agents quietly violate while "solving" a task.
- MODEL: validated against the orchestrator/implementer/reviewer pattern; model assignments remain
  swappable example configurations in SKILL.md.
- REJECTED: dropping the Constraints field to satisfy "minimal brief" — rejected because
  constraint breaches are a distinct failure mode from scope creep and deserve an explicit check;
  cutting it would hide the most common AI slip. Also rejected: adding a sixth "style/format"
  question — out of scope for fitness-to-task.
- NOTE: Version stays v1.1.0 through PR iteration. Version increments ONLY after merge to main.

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
