#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-wpmgrh05}"
export WPMGR_API_URL="${WPMGR_API_URL:-http://127.0.0.1:18191}"
export WPMGR_MAILPIT_URL="${WPMGR_MAILPIT_URL:-http://127.0.0.1:18195}"
export WPMGR_BOOTSTRAP_CLAIM="${WPMGR_BOOTSTRAP_CLAIM:-wpmgr-h05-bootstrap-claim-lab-only}"
export PYTHONUNBUFFERED=1
PIN_COMMIT="e1b3a163988c9f1c31bc93922ea34322fa188792"
REPO_URL="${WPMGR_SRC_URL:-https://github.com/mosamlife/wpmgr.git}"
PIN="$(pwd)/src"
LABEL="WPMGR-H05-INVITE-2FA"
WITNESS="WPMGR-H05-SESSION-WITHOUT-2FA"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_run() {
  echo "FAIL ${LABEL} $* ${WITNESS}" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 api || true
  exit 1
}

ensure_image() {
  if docker image inspect wpmgr-lab:v0.61.199 >/dev/null 2>&1; then
    echo "IOC image-present wpmgr-lab:v0.61.199"
    return 0
  fi
  echo "== flock build wpmgr-lab:v0.61.199 =="
  flock /tmp/wpmgr-lab-image.lock docker build \
    -f "${PIN}/infra/Dockerfile.api" \
    -t wpmgr-lab:v0.61.199 \
    --build-arg VERSION=0.61.199 \
    "${PIN}"
}

trap down EXIT
chmod +x poc.py
down

ensure_pin() {
  if [[ ! -e "${PIN}/.git" ]]; then
    git clone --filter=blob:none --no-checkout "${REPO_URL}" "${PIN}" || fail_run "clone-failed"
    git -C "${PIN}" fetch --depth 1 origin "${PIN_COMMIT}" || fail_run "fetch-failed"
    git -C "${PIN}" checkout --detach FETCH_HEAD || fail_run "checkout-failed"
  fi
  local got
  got="$(git -C "${PIN}" rev-parse HEAD)"
  if [[ "${got}" != "${PIN_COMMIT}" ]]; then
    fail_run "pin-mismatch"
  fi
}

ensure_pin
ensure_image || fail_run "image-build-failed"

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 12); do
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=${attempt}"
  sleep 30
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_run "compose-up-failed"
fi

echo "== wait ${WPMGR_API_URL}/readyz =="
ready=0
for i in $(seq 1 90); do
  code="$(curl -sS -o /tmp/wpmgr-h05-readyz.txt -w '%{http_code}' --max-time 8 \
    "${WPMGR_API_URL}/readyz" || true)"
  if [[ "${code}" == "200" ]]; then
    ready=1
    echo "IOC api-ready attempt=${i} readyz=${code}"
    break
  fi
  echo "IOC api-wait attempt=${i} readyz=${code}"
  sleep 3
done
if [[ "${ready}" != 1 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=120 api || true
  fail_run "api-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e
if [[ "${rc}" != 0 ]]; then
  if ! tail -n1 poc-last-run.txt 2>/dev/null | grep -qE '^(SUCCESS|FAIL) '; then
    echo "FAIL ${LABEL} poc-exit=${rc} ${WITNESS}" >> poc-last-run.txt
  fi
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 api || true
fi

exit "${rc}"
