# Contributing

## Add a skill

1. Choose exactly one tier and create one kebab-case skill folder whose name matches the `name` frontmatter field.
2. Copy `SKILL-TEMPLATE.md` when available, then include the required frontmatter and the ordered `Trigger`, `Steps`, `Pitfalls`, `Verify`, and `Non-use / Scope` sections.
3. Add an adjacent `CHANGELOG.md` with a semantic version, date, `ADDED:` or `CHANGED:`, `DECISION:`, `MODEL:`, and any meaningful `REJECTED:` alternative.
4. Keep skills as Markdown plus optional sanitized `references/`; the agent is the runtime.
5. Run `python3 refresh-skills-index.py` from the repository root and commit the generated `INDEX.md` with the skill.
6. Verify commands are assertable, inspect the diff for secrets or work IP, and open a PR for Stephen's review.

## Tiers and naming

- `generic/<skill>/`: tool-agnostic procedures with no personal-project or employer IP; safe to fork to work.
- `dev/<skill>/`: development workflow and process skills with sanitized examples; safe to fork to work.
- `projects/<project>/<skill>/`: project-specific personal IP; personal-only and never copied to work.
- Use lowercase kebab-case for project and skill folders. Project folders must be `projects/<project>/`, not dot-prefixed names.
- Keep one responsibility per skill and make its frontmatter `description` state when to load it.

## Hard rules

- Never push directly to `main`. Work on a branch, open a PR, and wait for Stephen's explicit approval before merge.
- Never auto-merge, and never let an orchestrator, implementer, or reviewer merge its own work.
- Commit to `scheung1206/skills` only from Stephen's personal Mac.
- Never add employer source, endpoints, schemas, client data, secrets, or other work IP.
- Allow only one-way flow from the personal library to sanitized work forks; never copy work-derived improvements back.
- For implementation work, commit a runnable test or explicit assertion list first and wait for Stephen's approval before writing implementation.
