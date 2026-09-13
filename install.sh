#!/usr/bin/env bash
# Install the cat-visual-aptitude skill for Antigravity CLI (agy) and/or Claude Code.
#
#   ./install.sh                # register this repo with agy globally (recommended)
#   ./install.sh copy           # copy into the global skills root instead
#   ./install.sh workspace      # register for the current repo only
#   ./install.sh claude         # copy into ~/.claude/skills for Claude Code
#
# "register" means a later `git pull` updates the skill with no reinstall.
set -euo pipefail

MODE="${1:-register}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$REPO/skills"
SKILL_NAME="cat-visual-aptitude"

[ -f "$SKILLS_DIR/$SKILL_NAME/SKILL.md" ] || {
  echo "skills/$SKILL_NAME/SKILL.md not found under $REPO" >&2
  exit 1
}

PY_BIN=""
for c in python3 python py; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys" >/dev/null 2>&1; then
    PY_BIN="$c"; break
  fi
done
[ -n "$PY_BIN" ] || { echo "no working python found on PATH (need python3, python or py)" >&2; exit 1; }

add_entry() {                       # add_entry <config.json> <path>
  local cfg="$1" entry="$2"
  mkdir -p "$(dirname "$cfg")"
  "$PY_BIN" - "$cfg" "$entry" <<'PY'
import json, os, sys
cfg_path, entry = sys.argv[1], sys.argv[2]
cfg = {}
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        try:
            cfg = json.load(f)
        except json.JSONDecodeError:
            sys.exit(f"{cfg_path} is not valid JSON; fix or remove it first")
entries = cfg.setdefault("entries", [])
if any(e.get("path") == entry for e in entries):
    print(f"already registered: {entry}")
else:
    entries.append({"path": entry})
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"registered {entry} in {cfg_path}")
PY
}

copy_to() {                         # copy_to <dest>
  local dest="$1"
  rm -rf "$dest"
  mkdir -p "$dest"
  cp -R "$SKILLS_DIR/$SKILL_NAME/." "$dest/"
  echo "copied to $dest"
}

case "$MODE" in
  register)
    add_entry "$HOME/.gemini/config/skills.json" "$SKILLS_DIR"
    echo
    echo "Installed globally for agy. Start a new session and paste a question;"
    echo "the skill activates on its own. Confirm with:"
    echo "  agy --print='Which skills are available to you? Names only.'"
    echo "Update later with: git -C \"$REPO\" pull  (no reinstall needed)"
    ;;
  copy)
    copy_to "$HOME/.gemini/config/skills/$SKILL_NAME"
    echo "Note: a copy does not track this repo. Re-run after a git pull."
    ;;
  workspace)
    add_entry "$PWD/.agents/skills.json" "$SKILLS_DIR"
    echo
    echo "Registered for this workspace only ($PWD)."
    echo "Commit .agents/skills.json to share it with the team."
    ;;
  claude)
    copy_to "$HOME/.claude/skills/$SKILL_NAME"
    echo "Restart Claude Code to pick it up."
    ;;
  *)
    echo "usage: $0 [register|copy|workspace|claude]" >&2
    exit 2
    ;;
esac

echo
echo "Optional: pip install pillow    (needed only for the image scripts)"
