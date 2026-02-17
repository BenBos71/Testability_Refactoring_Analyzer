#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SYSTEM_TESTS_DIR="${SCRIPT_DIR}/system_tests"

VENV_ANALYZER="${REPO_ROOT}/.venv/bin/testability-analyzer"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"

if [[ -x "${VENV_ANALYZER}" ]]; then
  ANALYZER_CMD=("${VENV_ANALYZER}")
elif [[ -x "${VENV_PYTHON}" ]]; then
  ANALYZER_CMD=("${VENV_PYTHON}" -m testability_analyzer.cli)
elif command -v testability-analyzer >/dev/null 2>&1; then
  ANALYZER_CMD=(testability-analyzer)
else
  ANALYZER_CMD=(python3 -m testability_analyzer.cli)
fi

shopt -s nullglob

exit_code=0

files=("${SYSTEM_TESTS_DIR}"/*.py)
IFS=$'\n' files=($(printf '%s\n' "${files[@]}" | LC_ALL=C sort))
unset IFS

for file in "${files[@]}"; do
  base="$(basename "${file}")"
  if [[ "${base}" == "validate_examples.py" ]]; then
    continue
  fi

  set +e
  output="$(${ANALYZER_CMD[@]} "${file}" --verbose 2>&1)"
  cmd_status=$?
  set -e

  if [[ ${cmd_status} -ne 0 ]]; then
    exit_code=1
    printf 'System test failed for %s\n' "${base}" >&2
    continue
  fi

  clean_output="$(printf '%s\n' "${output}" | sed -E $'s/\x1B\[[0-9;]*[A-Za-z]//g')"

  score_line="$(printf '%s\n' "${clean_output}" | grep -E "^Score: [0-9]+" | head -n 1 || true)"
  score="$(printf '%s\n' "${score_line}" | awk '{print $2}' || true)"

  if [[ -z "${score}" ]]; then
    exit_code=1
    printf 'Failed to extract score for %s\n' "${base}" >&2
    continue
  fi

  printf '%s %s\n' "${base}" "${score}"
done

exit "${exit_code}"
