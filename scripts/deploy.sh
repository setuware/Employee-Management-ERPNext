#!/usr/bin/env bash
# Auto-deploy for the LMS app (Frappe/ERPNext).
# Works in two setups:
#   1. bench directly accessible on this host
#   2. bench inside a Docker container (bench path not on host) -> runs inside the container
# Usage: deploy.sh [bench_path] [site_name] [container_pattern]
set -euo pipefail

BENCH_PATH="${1:-/workspace/frappe15-bench}"
SITE_NAME="${2:-}"
CONTAINER_PATTERN="${3:-}"

log() { echo "==> $*"; }

deploy_inside() {
	if [ ! -d "$BENCH_PATH/apps/lms/.git" ]; then
		echo "ERROR: $BENCH_PATH/apps/lms is not a git checkout. Clone it first:" >&2
		echo "  cd $BENCH_PATH/apps && git clone git@github.com:setuware/Employee-Management-ERPNext.git lms" >&2
		exit 1
	fi

	log "Pulling latest code"
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
	log "Code updated to commit $DEPLOYED_SHA"

	cd "$BENCH_PATH"
	SITE_ARGS=()
	if [ -n "$SITE_NAME" ]; then
		SITE_ARGS=(--site "$SITE_NAME")
	fi

	log "Running bench migrate"
	bench "${SITE_ARGS[@]}" migrate
	bench build --app lms
	bench "${SITE_ARGS[@]}" clear-cache || true
	bench "${SITE_ARGS[@]}" clear-website-cache || true
	log "Done. Deployed commit $DEPLOYED_SHA"
}

# Case 1: bench is directly accessible from this shell
if [ -d "$BENCH_PATH/apps" ]; then
	deploy_inside
	exit 0
fi

# Case 2: bench lives inside a Docker container (bench path not on host)
if [ -n "$CONTAINER_PATTERN" ]; then
	CONTAINER="$(docker ps -qf "name=$CONTAINER_PATTERN" | head -1)"
else
	CONTAINER=""
	for pat in bench frappe backend web worker; do
		CONTAINER="$(docker ps -qf "name=$pat" | head -1)"
		[ -n "$CONTAINER" ] && break
	done
fi

if [ -z "$CONTAINER" ]; then
	echo "ERROR: bench path '$BENCH_PATH' not found on this host and no bench container found." >&2
	echo "Run 'docker ps' on the server and pass the container name as the 3rd argument." >&2
	exit 1
fi

log "Running deployment inside container $CONTAINER"
SCRIPT="$(readlink -f "$0")"
docker cp "$SCRIPT" "$CONTAINER":/tmp/lms_deploy.sh >/dev/null
docker exec -w "$BENCH_PATH" "$CONTAINER" bash /tmp/lms_deploy.sh "$BENCH_PATH" "$SITE_NAME"
