#!/usr/bin/env bash
# sync-to-profile.sh — push the CURATED skills from this repo into the Hermes profile.
#
# Source of truth: this repo's dev/ skills (orchestration, tdd-gate, documentation-workflow).
# Target: ~/.hermes/profiles/shinsu/skills  (override with HERMES_PROFILE_SKILLS=...).
#
# Collision policy: REPO WINS. If a curated skill already exists in the profile, the
# profile copy is backed up to /tmp (never silently destroyed) and then replaced by the
# repo version. The other ~128 local profile skills are NEVER touched.
#
# Cross-device sync: on any machine, `git pull` this repo, then run this script.
# The profile stays the live skills dir; the repo stays canonical for curated skills.
#
# Usage:
#   ./sync-to-profile.sh            # sync (repo wins on collision, backups to /tmp)
#   ./sync-to-profile.sh --pull     # git pull the repo first, then sync
#
# Portable: uses only POSIX/bash-3.2 features (no associative arrays).
set -eu

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO_DEV="$REPO_ROOT/dev"
PROFILE_SKILLS="${HERMES_PROFILE_SKILLS:-$HOME/.hermes/profiles/shinsu/skills}"

if [ "${1:-}" = "--pull" ]; then
  echo ">> git pull in $REPO_ROOT"
  git -C "$REPO_ROOT" pull --ff-only
fi

# repo dev/ subdir | profile relative target path
# (orchestration lives at dev/orchestration but the profile keeps the older
#  orchestration/orchestrator layout — mapped explicitly; the rest are 1:1)
MAP="orchestration|orchestration/orchestrator
tdd-gate|tdd-gate
documentation-workflow|documentation-workflow"

echo ">> syncing curated skills -> $PROFILE_SKILLS"
collisions=0
printf '%s\n' "$MAP" | while IFS='|' read -r src target; do
  [ -z "$src" ] && continue
  if [ ! -d "$REPO_DEV/$src" ]; then
    echo "  SKIP   $src (not present in repo dev/)"
    continue
  fi
  dest="$PROFILE_SKILLS/$target"
  if [ -e "$dest" ]; then
    # Only treat as a real collision if content actually differs.
    if diff -rq "$REPO_DEV/$src" "$dest" >/dev/null 2>&1; then
      echo "  SAME   $src -> $dest  (already in sync, skipped)"
      continue
    fi
    ts="$(date +%Y%m%d-%H%M%S)"
    backup="/tmp/skill-backup-${src}-${ts}"
    cp -R "$dest" "$backup"
    echo "  UPDATE $src -> $dest  (collision: backed up to $backup, repo wins)"
  else
    echo "  NEW    $src -> $dest"
  fi
  rm -rf "$dest"
  mkdir -p "$(dirname "$dest")"
  cp -R "$REPO_DEV/$src" "$dest"
done
echo ">> done. Curated skills synced (repo wins on collision). Other profile skills untouched."
