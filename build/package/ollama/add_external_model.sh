#!/usr/bin/env bash

ERROR_PREFIX="\033[0;31m[ERROR]\033[0m"
INFO_PREFIX="\033[1;33m[INFO]\033[0m"

# Public: Checks for an external model in the "/root/.models" directory and adds it to ollama if it doesn't exist.
#
# Environment Variables
#
# $1 - The model name of the external model.
#
# Examples
#   ./add_external_model.sh "sft_quantum_circuit_gen_8B"
function add_external_model() {
  local healthcheck_url
  local model
  local modelfile_path

  healthcheck_url="http://127.0.0.1:11434/api/tags"
  model="${1}"

  if [ -z "${model}" ]; then
    printf "%b no model supplied, skipping \n" "${ERROR_PREFIX}"
    return 1
  fi

  modelfile_path="/root/.models/${model}/Modelfile"

  if [[ ! -f "${modelfile_path}" ]]; then
    printf "%b Modelfile for external model \"%s\" not found at \"%s\", skipping\n" \
      "${INFO_PREFIX}" "${model}" "${modelfile_path}"
    return 0
  fi

  model_exists=$(curl -fsS "${healthcheck_url}" | jq -e --arg model "${model}" '.models[] | select(.name == $model)' >/dev/null && echo "yes" || echo "no")

  if [[ "${model_exists}" != "yes" ]]; then
    printf "%b external model \"%s\" not found, creating from Modelfile at \"%s\"\n" "${INFO_PREFIX}" "${model}" "${modelfile_path}"

    # create the model in ollama
    if ! /bin/ollama create "${model}" -f "${modelfile_path}"; then
      printf "%b failed to create external model \"%s\" from Modelfile\n" "${ERROR_PREFIX}" "${model}" >&2
      return 1
    fi
  else
    printf "%b external model \"%s\" already present, skipping\n" "${INFO_PREFIX}" "${model}"
  fi

  return 0
}
