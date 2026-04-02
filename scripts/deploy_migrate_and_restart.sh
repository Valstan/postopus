#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Single-shot deployment helper:
# - backs up .env and site_config collection
# - prepares venv and installs dependencies (optional)
# - runs migration script (dry-run by default, use --apply to apply)
# - performs optional smoke test
# - restarts systemd service and shows status/logs
#
# Usage:
#   ./scripts/deploy_migrate_and_restart.sh [--apply] [--service SERVICE] [--repo-path PATH]
# Options:
#   --apply           Actually apply migration (without this flag script runs dry-run)
#   --service NAME    systemd service name to restart (default: postopus)
#   --repo-path PATH  Path to repository (default: current dir)
#   --venv PATH       Virtualenv path (default: .venv)
#   --backup-dir DIR  Directory for backups/logs (default: /tmp)
#   --skip-install    Do not run pip install
#   --smoke-cmd CMD   Command to run as smoke test (quoted)
#   --help            Show this help

APPLY=0
SERVICE="postopus"
REPO_PATH="$(pwd)"
VENV_PATH=".venv"
BACKUP_DIR="/tmp"
SKIP_INSTALL=0
SMOKE_CMD=""

function usage() {
  sed -n '1,200p' "$0" | sed -n '1,120p'
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --service) SERVICE="$2"; shift 2 ;;
    --repo-path) REPO_PATH="$2"; shift 2 ;;
    --venv) VENV_PATH="$2"; shift 2 ;;
    --backup-dir) BACKUP_DIR="$2"; shift 2 ;;
    --skip-install) SKIP_INSTALL=1; shift ;;
    --smoke-cmd) SMOKE_CMD="$2"; shift 2 ;;
    --help) usage ;;
    *) echo "Unknown arg: $1" >&2; usage ;;
  esac
done

TS=$(date -u +%Y%m%dT%H%M%SZ)
LOG_DIR="$BACKUP_DIR/postopus_logs"
LOGFILE="$LOG_DIR/migrate_${TS}.log"
BACKUP_SUBDIR="$BACKUP_DIR/postopus_backup_${TS}"

echo "[info] repo: $REPO_PATH"
echo "[info] service: $SERVICE"
echo "[info] venv: $VENV_PATH"
echo "[info] backup dir: $BACKUP_DIR"
echo "[info] mode: $( [ $APPLY -eq 1 ] && echo APPLY || echo DRY-RUN )"

mkdir -p "$BACKUP_DIR" "$LOG_DIR"

cd "$REPO_PATH"

# Backup .env if present
if [ -f ".env" ]; then
  cp .env ".env.bak_${TS}"
  echo "[info] .env backed up to .env.bak_${TS}"
else
  echo "[warn] .env not found in repo root (proceeding)"
fi

# load env into session (export) if .env exists
if [ -f ".env" ]; then
  # shellcheck disable=SC1091
  set -a
  # shellcheck source=/dev/null
  source .env || true
  set +a
fi

if [ -z "${MONGO_CLIENT:-}" ]; then
  echo "[error] MONGO_CLIENT is not set in environment. Aborting." >&2
  exit 2
fi

echo "[info] creating mongo backup (site_config)"
if command -v mongodump >/dev/null 2>&1; then
  mkdir -p "$BACKUP_SUBDIR"
  mongodump --uri="$MONGO_CLIENT" --collection=site_config --out="$BACKUP_SUBDIR" || echo "[warn] mongodump failed"
  echo "[info] mongodump saved to $BACKUP_SUBDIR"
elif command -v mongoexport >/dev/null 2>&1; then
  mongoexport --uri="$MONGO_CLIENT" --collection=site_config --out="$BACKUP_DIR/site_config_backup_${TS}.json" || echo "[warn] mongoexport failed"
  echo "[info] mongoexport saved to $BACKUP_DIR/site_config_backup_${TS}.json"
else
  echo "[warn] neither mongodump nor mongoexport found — no mongo backup performed" >&2
fi

# Prepare venv
if [ ! -d "$VENV_PATH" ]; then
  echo "[info] creating venv at $VENV_PATH"
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv "$VENV_PATH"
  elif command -v python >/dev/null 2>&1; then
    python -m venv "$VENV_PATH"
  else
    echo "[error] python not found to create venv" >&2
    exit 3
  fi
fi

# shellcheck source=/dev/null
source "$VENV_PATH/bin/activate"

if [ $SKIP_INSTALL -eq 0 ]; then
  if [ -f "requirements.txt" ]; then
    echo "[info] installing dependencies into venv"
    pip install -r requirements.txt
  else
    echo "[warn] requirements.txt not found — skipping pip install"
  fi
else
  echo "[info] skipping pip install as requested"
fi

echo "[info] running migration script"
if [ $APPLY -eq 1 ]; then
  echo "[info] applying migration (this will modify DB)"
  python scripts/migrate_config_to_db.py --apply 2>&1 | tee "$LOGFILE"
else
  echo "[info] dry-run: running migration without --apply"
  python scripts/migrate_config_to_db.py 2>&1 | tee "$LOGFILE"
fi

echo "[info] migration log: $LOGFILE"

if [ -n "$SMOKE_CMD" ]; then
  echo "[info] running smoke test: $SMOKE_CMD"
  # run smoke test in subshell so its env doesn't leak
  ( $SMOKE_CMD ) 2>&1 | tee -a "$LOGFILE" || echo "[warn] smoke test failed" | tee -a "$LOGFILE"
fi

if [ $APPLY -eq 1 ]; then
  echo "[info] restarting systemd service: $SERVICE"
  sudo systemctl restart "$SERVICE"
  sudo systemctl status "$SERVICE" --no-pager -l
  echo "[info] recent journal entries for $SERVICE:"
  sudo journalctl -u "$SERVICE" -n 200 --no-pager
else
  echo "[info] dry-run: not restarting systemd service (use --apply to restart)"
fi

echo "[done] script finished"
