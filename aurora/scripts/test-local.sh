#!/usr/bin/env bash
# aurora/scripts/test-local.sh
#
# Test local plugin changes without pushing to GitHub.
# Reads the real installPath from installed_plugins.json so files land
# in the cache directory Claude Code actually loads — not marketplaces/.
#
# Usage:
#   ./aurora/scripts/test-local.sh start    — backup installed, inject dev version
#   ./aurora/scripts/test-local.sh restore  — restore backup

set -euo pipefail

INSTALLED_PLUGINS_JSON="$HOME/.claude/plugins/installed_plugins.json"
BACKUP_POINTER="$HOME/.claude/aurora-test-backup-path"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Read aurora installPath from JSON and convert Windows path to bash path
# Convert bash-style path (/c/Users/...) to Windows-style (C:/Users/...) for Python
WIN_JSON=$(cygpath -m "$INSTALLED_PLUGINS_JSON" 2>/dev/null || echo "$INSTALLED_PLUGINS_JSON" | sed 's|^/c/|C:/|')
INSTALL_PATH=$(python3 -c "
import json
with open(r'$WIN_JSON') as f:
    data = json.load(f)
entries = data.get('plugins', {}).get('aurora@aurora-smart-home', [])
if not entries:
    raise SystemExit('aurora@aurora-smart-home not found in installed_plugins.json')
path = entries[0].get('installPath', '')
path = path.replace('\\\\', '/').replace('C:', '/c').replace('c:', '/c')
print(path)
")

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

    if [ ! -d "$INSTALL_PATH" ]; then
      echo "ERROR: install path not found: $INSTALL_PATH"
      exit 1
    fi

    BACKUP_DIR="${INSTALL_PATH}-backup-$(date +%Y%m%d-%H%M%S)"
    cp -r "$INSTALL_PATH" "$BACKUP_DIR"
    echo "$BACKUP_DIR" > "$BACKUP_POINTER"
    echo "Install path : $INSTALL_PATH"
    echo "Backup saved : $BACKUP_DIR"

    cp -r "$REPO_ROOT/aurora/." "$INSTALL_PATH/"
    echo "Dev version injected from: $REPO_ROOT/aurora/"
    echo ""
    echo "Next steps:"
    echo "  1. Run /reload-plugins in Claude Code"
    echo "  2. Test — banner should show v1.8.0"
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
      exit 1
    fi

    rm -rf "$INSTALL_PATH"
    cp -r "$BACKUP_DIR" "$INSTALL_PATH"
    rm -f "$BACKUP_POINTER"

    echo "Restored: $INSTALL_PATH"
    echo "Backup kept at: $BACKUP_DIR (delete manually when satisfied)"
    echo ""
    echo "Next steps:"
    echo "  1. Run /reload-plugins in Claude Code"
    echo "  2. Push + release v1.8.0 on GitHub"
    echo "  3. claude plugin update aurora@aurora-smart-home"
    echo "  4. Verify update notice fires"
    ;;

  *)
    echo "Usage: $0 start | restore"
    echo ""
    echo "  start   — backup installed cache entry, inject dev version"
    echo "  restore — restore backup (run before pushing to GitHub)"
    exit 1
    ;;

esac
