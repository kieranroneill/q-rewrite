#!/usr/bin/env bash

ERROR_PREFIX="\033[0;31m[ERROR]\033[0m"
INFO_PREFIX="\033[1;33m[INFO]\033[0m"

# Private: Stops the background Ollama process if it is running.
function cleanup() {
  if kill -0 "${OLLAMA_PID:-0}" 2>/dev/null; then
    kill "${OLLAMA_PID}" || true
    wait "${OLLAMA_PID}" || true
  fi
}

# Public: Starts Ollama, ensures the configured model is present, then runs the server in the foreground.
#
# Environment Variables
#
# $MODEL - The model to pull and serve, defaults to "qwen2.5-coder:3b".
#
# Examples
#   ./entrypoint.sh
function main() {
  local attempt
  local healthcheck_url
  local host
  local model
  local ready
  local model_exists

  model="${MODEL:-qwen2.5-coder:3b}"
  host="${OLLAMA_HOST:-0.0.0.0:11434}"
  healthcheck_url="http://127.0.0.1:11434/api/tags"
  ready=0

  printf "%b starting ollama on \"%s\"...\n" "${INFO_PREFIX}" "${host}"
  export OLLAMA_HOST="${host}"
  /bin/ollama serve &
  OLLAMA_PID=$!

  trap cleanup EXIT

  printf "%b waiting for ollama api...\n" "${INFO_PREFIX}"
  for attempt in $(seq 1 60); do
    if curl -fsS "${healthcheck_url}" >/dev/null; then
      ready=1
      break
    fi

    sleep 1
  done

  if [[ "${ready}" -ne 1 ]]; then
    printf "%b ollama api did not become ready in time.\n" "${ERROR_PREFIX}" >&2
    exit 1
  fi

  # check if the requested model exists
  model_exists=$(curl -fsS "${healthcheck_url}" | jq -e --arg model "${model}" '.models[] | select(.name == $model)' >/dev/null && echo "yes" || echo "no")

  if [[ "${model_exists}" != "yes" ]]; then
    printf "%b pulling model \"%s\"\n" "${INFO_PREFIX}" "${model}"
    /bin/ollama pull "${model}"
  else
    printf "%b model \"%s\" already present\n" "${INFO_PREFIX}" "${model}"
  fi

  printf "%b restarting ollama in foreground...\n" "${INFO_PREFIX}"
  cleanup
  trap - EXIT
  exec /bin/ollama serve
}

# and so, it begins...
main "$@"
