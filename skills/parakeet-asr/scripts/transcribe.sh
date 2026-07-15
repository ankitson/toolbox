#!/usr/bin/env bash
set -euo pipefail

readonly DEFAULT_MODEL="parakeet-asr/nemo-parakeet-tdt-0.6b-v2"

usage() {
  cat >&2 <<'EOF'
Usage:
  transcribe.sh <audio-file> [--model MODEL] [--out PATH] [--language CODE] [--prompt TEXT] [--json]

Environment:
  OPENAI_BASE_URL     API base immediately above /audio/transcriptions
  OPENAI_API_KEY      API credential
  TRANSCRIPTION_MODEL Default model override
EOF
  exit "${1:-2}"
}

require_value() {
  local flag="$1"
  local value="${2:-}"
  if [[ -z "$value" ]]; then
    echo "Missing value for $flag" >&2
    usage 2
  fi
}

if [[ "${1:-}" == "" ]]; then
  usage 2
fi
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage 0
fi

input="$1"
shift

model="${TRANSCRIPTION_MODEL:-$DEFAULT_MODEL}"
output=""
language=""
prompt=""
response_format="text"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      require_value "$1" "${2:-}"
      model="$2"
      shift 2
      ;;
    --out)
      require_value "$1" "${2:-}"
      output="$2"
      shift 2
      ;;
    --language)
      require_value "$1" "${2:-}"
      language="$2"
      shift 2
      ;;
    --prompt)
      require_value "$1" "${2:-}"
      prompt="$2"
      shift 2
      ;;
    --json)
      response_format="json"
      shift
      ;;
    -h|--help)
      usage 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage 2
      ;;
  esac
done

if [[ ! -f "$input" ]]; then
  echo "File not found: $input" >&2
  exit 1
fi

if [[ -z "${OPENAI_BASE_URL:-}" ]]; then
  echo "Missing OPENAI_BASE_URL" >&2
  exit 1
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "Missing OPENAI_API_KEY" >&2
  exit 1
fi

if [[ -z "$output" ]]; then
  output="${input%.*}.$([[ "$response_format" == "json" ]] && printf json || printf txt)"
fi

mkdir -p "$(dirname "$output")"
api_base="${OPENAI_BASE_URL%/}"
temporary="$(mktemp "${TMPDIR:-/tmp}/parakeet-transcribe.XXXXXX")"
normalized=""
trap 'rm -f "$temporary" "$normalized"' EXIT

curl_args=(
  --silent
  --show-error
  --fail-with-body
  --output "$temporary"
  "${api_base}/audio/transcriptions"
  --header "Authorization: Bearer ${OPENAI_API_KEY}"
  --header "Accept: application/json"
  --form "file=@${input}"
  --form "model=${model}"
  --form "response_format=${response_format}"
)

if [[ -n "$language" ]]; then
  curl_args+=(--form "language=${language}")
fi
if [[ -n "$prompt" ]]; then
  curl_args+=(--form "prompt=${prompt}")
fi

if ! curl "${curl_args[@]}"; then
  if [[ -s "$temporary" ]]; then
    echo "Transcription API response:" >&2
    head -c 4096 "$temporary" >&2
    echo >&2
  fi
  exit 1
fi

# Some compatible servers return {"text":"..."} even when response_format=text.
# Normalize that response so a .txt output always contains transcript text.
if [[ "$response_format" == "text" ]]; then
  normalized="$(mktemp "${TMPDIR:-/tmp}/parakeet-transcribe.XXXXXX")"
  python3 - "$temporary" "$normalized" <<'PY'
import json
import shutil
import sys

source, destination = sys.argv[1:]
try:
    with open(source, encoding="utf-8") as handle:
        payload = json.load(handle)
except (UnicodeDecodeError, json.JSONDecodeError):
    shutil.copyfile(source, destination)
else:
    text = payload.get("text") if isinstance(payload, dict) else None
    if not isinstance(text, str):
        raise SystemExit("Transcription response JSON is missing a text field")
    with open(destination, "w", encoding="utf-8") as handle:
        handle.write(text)
PY
  mv -f "$normalized" "$temporary"
fi

mv -f "$temporary" "$output"
trap - EXIT
printf '%s\n' "$output"
