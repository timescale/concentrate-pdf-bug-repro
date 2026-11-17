#!/usr/bin/env bash
# Sends identical Messages API bodies to Anthropic and Concentrate and prints the results.
# Requires: ANTHROPIC_API_KEY and CONCENTRATE_API_KEY in the environment.
set -uo pipefail
cd "$(dirname "$0")"
: "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY}" "${CONCENTRATE_API_KEY:?set CONCENTRATE_API_KEY}"

call() { # name url auth-header body
  printf '%-34s ' "$1"
  curl -s -o /tmp/repro_resp.json -w '%{http_code}  ' "$2" -H "$3" \
    -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d @"$4"
  head -c 220 /tmp/repro_resp.json; echo
}
A="https://api.anthropic.com/v1/messages";  AH="x-api-key: $ANTHROPIC_API_KEY"
C="https://api.concentrate.ai/v1/messages"; CH="Authorization: Bearer $CONCENTRATE_API_KEY"

call "Anthropic   + encrypted PDF" "$A" "$AH" payload-encrypted.json
call "Concentrate + encrypted PDF" "$C" "$CH" payload-encrypted.json
call "Concentrate + plain PDF"     "$C" "$CH" payload-plain.json
