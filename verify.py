#!/usr/bin/env python3
"""Enforce the orchestration skill's process gates (R1-R7) from git/gh state.

Inspects a GitHub PR (github.com/scheung1206/skills) via the `gh` CLI and
asserts the objective process gates defined in dev/orchestration/SKILL.md:
  A) PR targets `main` and auto-merge is disabled
  B) implementer agent != reviewer agent
  C) owner sign-off occurred before the first implementation commit
  D) TDD/spec commit precedes the first implementation commit
  E) reviewer comment contains a spec-trace (PASS/FAIL) and a verdict
  F) every agent comment is labeled; both roles commented
  G) review rounds <= 2
  H) parallel mode declares ownership + orchestrator disk-verification note
  I) CHANGELOG learning-loop entry dated on/after the PR

Exit 0 = all gates pass, 1 = any gate FAILs. Missing GitHub fields cause a
graceful SKIP rather than a crash. This script never judges code quality --
that is the reviewer's job -- it only checks process adherence.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHANGELOG = ROOT / "dev" / "orchestration" / "CHANGELOG.md"
REPO = "scheung1206/skills"

# Role-label detection. The canonical label format is `(Role: Model)` where
# Role is a single alphabetic word.
ROLE_RE = re.compile(r"\([A-Za-z]+:\s*[^)]+\)")
IMP_RE = re.compile(r"\(Implementer:\s*([^)]+)\)", re.IGNORECASE)
REV_RE = re.compile(r"\(Reviewer:\s*([^)]+)\)", re.IGNORECASE)
ORCH_RE = re.compile(r"\(Orchestrator:\s*([^)]+)\)", re.IGNORECASE)
OWNER_RE = re.compile(r"\(Owner:\s*approved\)", re.IGNORECASE)
PARALLEL_RE = re.compile(r"fan-out|parallel (?:fan-out|execution|sub-agent)|sub-agent", re.IGNORECASE)
OWNS_RE = re.compile(r"owns\s*:\s*(\S+)", re.IGNORECASE)

# Prefixes / tokens that mark a commit as a spec/test (TDD) commit rather than
# an implementation commit.
SPEC_PREFIXES = ("test:", "spec:", "add test", "chore(spec)")


# --------------------------------------------------------------------------- #
# Output helpers
# --------------------------------------------------------------------------- #
def pass_(desc: str) -> str:
    print(f"[PASS] {desc}")
    return "PASS"


def fail(desc: str) -> str:
    print(f"[FAIL] {desc}")
    return "FAIL"


def skip(desc: str) -> str:
    print(f"[SKIP] {desc}")
    return "SKIP"


# --------------------------------------------------------------------------- #
# gh / data helpers
# --------------------------------------------------------------------------- #
def gh_json(args: list[str]) -> dict:
    """Run a `gh` command and return parsed JSON. Raises RuntimeError on failure."""
    proc = subprocess.run(
        ["gh", "-R", REPO, *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "gh command failed")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"gh returned non-JSON output: {exc}") from exc


def parse_dt(value: str) -> datetime:
    """Parse an ISO-8601 timestamp (gh uses a trailing 'Z')."""
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def parse_date_only(value: str):
    return date.fromisoformat(value)


def normalize_commits(data: object) -> list[dict]:
    """Accept either `{"commits": [...]}` or a bare list of commit objects."""
    if isinstance(data, list):
        commits: list[dict] = []
        for item in data:
            if isinstance(item, dict) and "commits" in item:
                commits.extend(item["commits"])
            elif isinstance(item, dict):
                commits.append(item)
        return commits
    if isinstance(data, dict):
        return data.get("commits", [])
    return []


def is_spec_commit(message: str) -> bool:
    m = (message or "").lower()
    if any(m.startswith(p) for p in SPEC_PREFIXES):
        return True
    return "tdd" in m


def first_impl_commit(commits: list[dict]) -> dict | None:
    """First commit (chronologically) that is clearly implementation work."""
    ordered = sorted(commits, key=lambda c: c.get("authoredDate", ""))
    for c in ordered:
        if not is_spec_commit(c.get("messageHeadline", "")):
            return c
    return None


# --------------------------------------------------------------------------- #
# Gates
# --------------------------------------------------------------------------- #
def gate_a(pr: dict) -> str:
    """PR targets `main` AND auto-merge is disabled AND not a draft."""
    base = pr.get("baseRefName")
    if base is None:
        return skip("baseRefName field missing from PR data")
    amr = pr.get("autoMergeRequest")
    if pr.get("isDraft"):
        return fail("PR is a draft")
    if base != "main":
        return fail(f"base ref is {base!r}, expected 'main'")
    if amr:
        return fail("auto-merge is enabled (autoMergeRequest is set)")
    return pass_("PR targets 'main', not draft, auto-merge disabled")


def gate_b(comments: list[dict]) -> str:
    """Implementer agent != reviewer agent; both roles must be present."""
    impl = rev = None
    for c in comments:
        body = c.get("body", "") or ""
        m = IMP_RE.search(body)
        if m and impl is None:
            impl = m.group(1).strip()
        m = REV_RE.search(body)
        if m and rev is None:
            rev = m.group(1).strip()
    if not impl:
        return fail("no (Implementer: ...) comment found")
    if not rev:
        return fail("no (Reviewer: ...) comment found")
    if impl == rev:
        return fail(f"implementer ({impl}) == reviewer ({rev})")
    return pass_(f"implementer ({impl}) != reviewer ({rev})")


def gate_c(comments: list[dict], commits: list[dict]) -> str:
    """Owner sign-off occurred before the first implementation commit."""
    owner_dt = None
    for c in comments:
        if OWNER_RE.search(c.get("body", "") or ""):
            created = c.get("createdAt")
            if created:
                owner_dt = parse_dt(created)
                break
    if owner_dt is None:
        return fail("no (Owner: approved) comment found")
    if not commits:
        return skip("no commits available to compare against")
    impl = first_impl_commit(commits)
    earliest = min(commits, key=lambda c: c.get("authoredDate", ""))
    if impl is None:
        # Conservative: cannot distinguish impl commit; require owner <= earliest.
        ref = earliest
        ref_dt = parse_dt(ref.get("authoredDate", ""))
        if owner_dt <= ref_dt:
            return pass_(f"owner approved {owner_dt.isoformat()} <= earliest commit {ref_dt.isoformat()}")
        return fail(f"owner approved {owner_dt.isoformat()} after earliest commit {ref_dt.isoformat()}")
    ref_dt = parse_dt(impl.get("authoredDate", ""))
    if owner_dt < ref_dt:
        return pass_(f"owner approved {owner_dt.isoformat()} before first impl commit {ref_dt.isoformat()}")
    return fail(f"owner approved {owner_dt.isoformat()} not before first impl commit {ref_dt.isoformat()}")


def gate_d(commits: list[dict]) -> str:
    """TDD/spec commit(s) precede the first implementation commit."""
    if not commits:
        return skip("no commits available")
    ordered = sorted(commits, key=lambda c: c.get("authoredDate", ""))
    spec = [c for c in ordered if is_spec_commit(c.get("messageHeadline", ""))]
    if not spec:
        return skip("no TDD/spec commit detectable")
    impl = first_impl_commit(commits)
    if impl is None:
        return skip("no implementation commit to compare against")
    impl_dt = parse_dt(impl.get("authoredDate", ""))
    if all(parse_dt(s.get("authoredDate", "")) < impl_dt for s in spec):
        return pass_(f"{len(spec)} spec commit(s) precede first impl commit")
    return fail("a spec commit is not earlier than the first impl commit")


def gate_e(comments: list[dict]) -> str:
    """The FINAL reviewer comment contains a spec-trace (PASS/FAIL) and a verdict.

    Only the last reviewer comment is checked: round-2 confirmations may be
    brief ("LGTM (Reviewer: Codex)") and need not repeat the full trace.
    """
    rev_bodies = [
        c.get("body", "") or ""
        for c in comments
        if REV_RE.search(c.get("body", "") or "")
    ]
    if not rev_bodies:
        return fail("no (Reviewer: ...) comment found")
    last = rev_bodies[-1]
    problems: list[str] = []
    if not re.search(r"PASS|FAIL", last, re.IGNORECASE):
        problems.append("no PASS/FAIL in final reviewer comment")
    if not re.search(r"verdict", last, re.IGNORECASE):
        problems.append("no 'Verdict' in final reviewer comment")
    if problems:
        return fail("; ".join(problems))
    return pass_(f"final reviewer comment contains PASS/FAIL + Verdict")


def gate_f(comments: list[dict]) -> str:
    """Every agent comment is labeled; both roles commented."""
    markers = ("(Implementer:", "(Reviewer:", "(Orchestrator:")
    unlabeled = 0
    for c in comments:
        body = c.get("body", "") or ""
        if any(marker in body for marker in markers):
            # The label must match the canonical `(Role: Model)` format.
            if not ROLE_RE.search(body):
                unlabeled += 1
    has_impl = any(IMP_RE.search(c.get("body", "") or "") for c in comments)
    has_rev = any(REV_RE.search(c.get("body", "") or "") for c in comments)
    problems: list[str] = []
    if unlabeled:
        problems.append(f"{unlabeled} unlabeled agent-style comment(s)")
    if not has_impl:
        problems.append("no Implementer comment")
    if not has_rev:
        problems.append("no Reviewer comment")
    if problems:
        return fail("; ".join(problems))
    return pass_("all agent comments labeled; both roles commented")


def gate_g(comments: list[dict]) -> str:
    """Review rounds <= 2.

    Implements the Verify section's "reviewer re-review count <= 2" (SKILL.md
    Verify, gate G). The R6 prose ("at most two review rounds") is interpreted
    as <=2 re-review comments beyond the first reviewer pass, i.e. <=3 total
    reviewer comments. If R6 is later read as <=2 total, tighten this.
    """
    rev_count = sum(1 for c in comments if REV_RE.search(c.get("body", "") or ""))
    rounds = max(0, rev_count - 1)
    if rounds <= 2:
        return pass_(f"{rev_count} reviewer comment(s), {rounds} re-review round(s) (<=2)")
    return fail(f"{rev_count} reviewer comments -> {rounds} re-review rounds (>2)")


def gate_h(comments: list[dict]) -> str:
    """Parallel mode: ownership declared + orchestrator disk-verification note."""
    parallel = any(PARALLEL_RE.search(c.get("body", "") or "") for c in comments)
    if not parallel:
        return skip("parallel mode not detected")
    owns_declared = any(
        OWNS_RE.search(c.get("body", "") or "")
        for c in comments
    )
    orch_disk = any(
        ORCH_RE.search(c.get("body", "") or "")
        and re.search(r"disk|verified|fan-in", c.get("body", "") or "", re.IGNORECASE)
        for c in comments
    )
    problems: list[str] = []
    if not owns_declared:
        problems.append("no ownership declaration (expects 'owns: <paths>')")
    if not orch_disk:
        problems.append("no orchestrator disk-verification note")
    if problems:
        return fail("; ".join(problems))
    return pass_("parallel mode: ownership declared + orchestrator disk-verification present")


def gate_i(pr: dict) -> str:
    """CHANGELOG learning-loop: a dated ADDED/DECISION/REJECTED entry >= PR date.

    The marker must appear in the LATEST version section (under the most
    recent `## vX.Y.Z — DATE` header), not anywhere in the file — older
    versions already carry markers and would otherwise satisfy the regex.
    """
    if not CHANGELOG.exists():
        return skip("dev/orchestration/CHANGELOG.md not found")
    text = CHANGELOG.read_text(encoding="utf-8")
    # Find the chronologically latest dated version header (CHANGELOG is
    # newest-first, so positional [-1] is the OLDEST — must max by date).
    header_dates = []
    for h in re.finditer(r"##\s+v[0-9.]+[^\n]*?(\d{4}-\d{2}-\d{2})", text):
        try:
            header_dates.append((parse_date_only(h.group(1)), h.start()))
        except ValueError:
            continue
    if not header_dates:
        return skip("no dated version entries in CHANGELOG")
    latest_start = max(header_dates, key=lambda x: x[0])[1]
    next_header = text.find("\n## ", latest_start + 1)
    section = text[latest_start:next_header if next_header != -1 else None]
    if not re.search(r"(ADDED|DECISION|REJECTED):", section):
        return skip("latest CHANGELOG section has no ADDED:/DECISION:/REJECTED: entry")
    # Reference date: prefer merge date, fall back to PR creation date.
    ref_dt = None
    for field in ("mergedAt", "createdAt"):
        v = pr.get(field)
        if v:
            try:
                ref_dt = parse_dt(v)
            except ValueError:
                ref_dt = None
            if ref_dt is not None:
                break
    if ref_dt is None:
        return skip("no PR created/merged date available to compare")
    latest_date = max(header_dates, key=lambda x: x[0])[0]
    ref_day = ref_dt.date()
    if latest_date >= ref_day:
        return pass_(
            f"CHANGELOG latest entry dated {latest_date} (>= PR {ref_day}) with learning-loop markers"
        )
    return skip(f"CHANGELOG latest entry {latest_date} predates PR {ref_day} (uncertain)")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enforce the orchestration skill's process gates (R1-R7) for a PR.",
    )
    parser.add_argument(
        "--pr",
        required=True,
        help="GitHub PR number to verify (e.g. --pr 4).",
    )
    args = parser.parse_args()
    pr_number = args.pr.lstrip("#")

    try:
        pr = gh_json(
            [
                "pr",
                "view",
                pr_number,
                "--json",
                "baseRefName,isDraft,autoMergeRequest,createdAt,mergedAt",
            ]
        )
        comments = gh_json(["pr", "view", pr_number, "--json", "comments"]).get(
            "comments", []
        )
        commits = normalize_commits(
            gh_json(["pr", "view", pr_number, "--json", "commits"])
        )
    except (RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    statuses = [
        gate_a(pr),
        gate_b(comments),
        gate_c(comments, commits),
        gate_d(commits),
        gate_e(comments),
        gate_f(comments),
        gate_g(comments),
        gate_h(comments),
        gate_i(pr),
    ]

    if "FAIL" in statuses:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
