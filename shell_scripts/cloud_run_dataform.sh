#!/bin/bash
set -euo pipefail

: "${TAGS:=bm1,bm2,bm3,prod}"
: "${ACTIONS:=}"
: "${EXTRA_ARGS:=}"

echo "tags=${TAGS}, actions=${ACTIONS}, extra_args=${EXTRA_ARGS}"

DATAFORM_BIN="$(command -v dataform || true)"
if [[ -z $DATAFORM_BIN ]]; then
  DATAFORM_BIN="npx --yes @dataform/cli@3"
fi

echo "PWD=$(pwd)"
ls -la . || true
ls -la ./dataform || true
cp -f /run/secrets/.df-credentials.json ./dataform/.df-credentials.json
cd dataform
IFS="," read -r -a TAG_LIST <<< "${TAGS}"
for tag in "${TAG_LIST[@]}"; do
  echo -e "=== running: ${tag} ==="
  ${DATAFORM_BIN} run \
    --dry-run=false \
    ${ACTIONS:+--actions ${ACTIONS}} \
    --tags "${tag}" \
    ${EXTRA_ARGS}
  echo "=== ${tag} done ==="
done