#!/usr/bin/env bash
# Auto-deploy script for the LMS app (Frappe/ERPNext in Docker).
# Usage: deploy.sh [bench_path] [site_name]
set -euo pipefail

BENCH_PATH="${1:-/workspace/frappe15-bench}"
SITE_NAME="${2:-}"

log() { echo "==> $*"; }

if [ ! -d "$BENCH_PATH/apps/lms/.git" ]; then
	echo "ERROR: $BENCH_PATH/apps/lms is not a git checkout. Clone the repo there first:" >&2
	echo "  git clone https://github.com/setuware/Employee-Management-ERPNext.git $BENCH_PATH/apps/lms" >&2
	exit 1
fi

log "Pulling latest code in $BENCH_PATH/apps/lms"
cd "$BENCH_PATH/apps/lms"
git fetch --all --prune
REMOTE="$(git remote | head -1)"
if [ -z "$REMOTE" ]; then
	echo "ERROR: no git remote configured in apps/lms" >&2
	exit 1
fi
git reset --hard "$REMOTE/main"
git checkout main 2>/dev/null || true
DEPLOYED_SHA="$(git rev-parse --short HEAD)"
log "Deploying commit $DEPLOYED_SHA"

cd "$BENCH_PATH"

build_site_args() {
	if [ -n "$SITE_NAME" ]; then
		echo "--site $SITE_NAME"
	fi
}

restart_containers() {
	for name in frontend backend worker scheduler; do
		CID="$(docker ps -qf "name=$name" | head -1)"
		if [ -n "$CID" ]; then
			log "Restarting $name container ($CID)"
			docker restart "$CID" >/dev/null
		fi
	done
}

if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
	BACKEND="$(docker ps -qf "name=backend" | head -1)"
	if [ -n "$BACKEND" ]; then
		log "Running migrate inside backend container ($BACKEND)"
		docker exec -w "$BENCH_PATH" "$BACKEND" bench $(build_site_args) migrate
		docker exec -w "$BENCH_PATH" "$BACKEND" bench $(build_site_args) clear-cache || true

		# Prefer docker compose restart if a compose file is present, else restart containers
		if [ -f "$BENCH_PATH/../frappe_docker/pwd.yml" ]; then
			log "Restarting via docker compose (pwd.yml)"
			(cd "$BENCH_PATH/../frappe_docker" && docker compose -f pwd.yml restart backend worker scheduler frontend) || restart_containers
		elif [ -f "$BENCH_PATH/pwd.yml" ] || [ -f "$BENCH_PATH/docker-compose.yml" ]; then
			log "Restarting via docker compose"
			docker compose -f pwd.yml restart 2>/dev/null || docker compose restart 2>/dev/null || restart_containers
		else
			restart_containers
		fi

		log "Done. Deployed commit $DEPLOYED_SHA"
		exit 0
	fi
fi

log "No Docker backend found — falling back to running bench directly on the host"
bench $(build_site_args) migrate
bench $(build_site_args) clear-cache
bench restart
log "Done. Deployed commit $DEPLOYED_SHA"
