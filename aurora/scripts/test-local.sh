#!/usr/bin/env bash
# aurora/scripts/test-local.sh
#
# Test local plugin changes without pushing to GitHub.
# After testing, restore the previous installed version so the GitHub
# update-detection flow still works when you push and release.
#
# Usage:
#   ./aurora/scripts/test-local.sh start    — backup installed, inject dev version
#   ./aurora/scripts/test-local.sh restore  — restore backup

set -euo pipefail

INSTALLED_DIR="$HOME/.claude/plugins/marketplaces/aurora-smart-home"
BACKUP_POINTER="$HOME/.claude/aurora-test-backup-path"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cmd="${1:-}"

case "$cmd" in

  start)
    if [ -f "$BACKUP_POINTER" ]; then
      EXISTING=$(cat "$BACKUP_POINTER")
      echo "ERROR: a test session is already active."
      echo "Backup is at: $EXISTING"
      echo "Run '$0 restore' first."
      exit 1
    fi

    if [ ! -d "$INSTALLED_DIR" ]; then
      echo "ERROR: installed plugin directory not found: $INSTALLED_DIR"
      exit 1
    fi

    BACKUP_DIR="${INSTALLED_DIR}-backup-$(date +%Y%m%d-%H%M%S)"
    cp -r "$INSTALLED_DIR" "$BACKUP_DIR"
    echo "$BACKUP_DIR" > "$BACKUP_POINTER"
    echo "Backup saved: $BACKUP_DIR"

    # Inject dev version — only the aurora/ subtree changes in v1.8.0+
    # Copy the full aurora/ directory from the repo into the installed plugin
    cp -r "$REPO_ROOT/aurora/." "$INSTALLED_DIR/aurora/"
    echo "Dev version injected from: $REPO_ROOT"
    echo ""
    echo "Next steps:"
    echo "  1. Run /reload-plugins in Claude Code"
    echo "  2. Test whatever you need to test"
    echo "  3. Run '$0 restore' when done"
    ;;

  restore)
    if [ ! -f "$BACKUP_POINTER" ]; then
      echo "ERROR: no active test session found."
      echo "Run '$0 start' first."
      exit 1
    fi

    BACKUP_DIR=$(cat "$BACKUP_POINTER")

    if [ ! -d "$BACKUP_DIR" ]; then
      echo "ERROR: backup directory missing: $BACKUP_DIR"
      echo "Cannot restore. Check manually."
      exit 1
    fi

    rm -rf "$INSTALLED_DIR"
    cp -r "$BACKUP_DIR" "$INSTALLED_DIR"
    rm -f "$BACKUP_POINTER"

    echo "Restored from: $BACKUP_DIR"
    echo "Backup directory kept at that path (delete manually when satisfied)."
    echo ""
    echo "Next steps:"
    echo "  1. Run /reload-plugins in Claude Code"
    echo "  2. Push to GitHub and create release v1.8.0"
    echo "  3. Run 'claude plugin update aurora@aurora-smart-home'"
    echo "  4. Verify update notice fires and version bumps correctly"
    ;;

  *)
    echo "Usage: $0 start | restore"
    echo ""
    echo "  start   — backup the installed plugin and inject your dev version"
    echo "  restore — restore the backup (do this before pushing to GitHub)"
    exit 1
    ;;

esac
