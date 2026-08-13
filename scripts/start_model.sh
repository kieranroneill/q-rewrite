#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "${0}")

source "${SCRIPT_DIR}/utilities/_set_vars.sh"

# Starts the model locally via Docker.
#
# $1 - [optional] a model to start in Docker, otherwise the model from the `.env.dev` file is read.
#
# Examples
#
#   ./start_model.sh # reads the model in the .env.dev file
#   ./start_model.sh "qwen2.5-coder:7b"
#
# Returns exit code 0.
function main() {
  _set_vars

  # load the env file
  set -a
  source .env.dev
  set +a

  # a passed model parameter takes precedence over .env.dev
  if [ -n "${1-}" ]; then
    OLLAMA_MODEL="${1}"
  fi

  # start the services
  printf "%b starting \"%b\" model... \n" "${INFO_PREFIX}" "${OLLAMA_MODEL}"
  docker compose \
	 	-f ./deployments/compose.development.yml \
	 	-p q-rewrite-dev \
		up
}

# and so, it begins...
main "$1"
