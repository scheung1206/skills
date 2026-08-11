---
name: tdd-gate
tier: dev
description: Use when implementation must wait for Stephen to review and approve a runnable test or explicit assertion list committed to the branch.
tools: [delegation, terminal, file]
status: active
env: macos>=12
---

# TDD Gate

## Trigger
- Load this skill before an implementer writes code for work whose expected behavior must be reviewed first.

## Steps
1. Translate the request into observable behavior, edge cases, and failure conditions before writing implementation code.
2. Create a runnable test file or an explicit assertion list that can be executed against the planned implementation.
3. Run the TDD artifact and record its expected pre-implementation failure or unmet assertions.
4. Commit the TDD artifact to the feature branch without implementation code.
5. Present the branch and runnable command to Stephen for review.
6. Wait for Stephen's explicit green-light; do not begin implementation while the TDD is unapproved.
7. After approval, implement only enough behavior to satisfy the reviewed artifact, rerun it, and commit the implementation separately.
8. Open or update the PR and preserve the branch-to-PR-to-review gate; never merge it.

## Pitfalls
- DON'T write production implementation before the TDD artifact is committed and approved.
- DON'T substitute prose such as "test manually" for a runnable test or explicit executable assertions.
- DON'T change reviewed assertions during implementation without returning to Stephen for review.
- DON'T treat a passing test that never failed for the missing behavior as proof of coverage.

## Verify
- Assert from branch history that the TDD commit precedes the implementation commit, Stephen approved the TDD before implementation began, and the documented test command exits zero after implementation.

## Non-use / Scope
- Do not require this gate for a trivial one-line change when the test would be heavier than the code, although TDD remains preferred whenever practical.
