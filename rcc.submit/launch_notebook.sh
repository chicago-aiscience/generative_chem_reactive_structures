#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SBATCH_SCRIPT="${1:-$SCRIPT_DIR/notebook.slurm}"

if [[ ! -f "$SBATCH_SCRIPT" ]]; then
  echo "Error: sbatch script not found: $SBATCH_SCRIPT" >&2
  exit 1
fi

if ! command -v sbatch >/dev/null 2>&1; then
  echo "Error: 'sbatch' not found. Run this on a machine with Slurm client tools." >&2
  exit 1
fi

echo "Submitting: $SBATCH_SCRIPT"
SUBMIT_OUT="$(sbatch "$SBATCH_SCRIPT" 2>&1 || true)"
echo "$SUBMIT_OUT"

JOB_ID="$(echo "$SUBMIT_OUT" | awk '/Submitted batch job/ {print $NF}' | tail -n 1 | tr -d '[:space:]')"
if [[ -z "$JOB_ID" || ! "$JOB_ID" =~ ^[0-9]+$ ]]; then
  echo "Error: could not parse job id from sbatch output." >&2
  exit 1
fi

echo "Job id: $JOB_ID"

echo "Waiting for job to reach RUNNING state..."

wait_until_running() {
  # Wait until Slurm reports RUNNING (best-effort).
  # If squeue is unavailable, fall back to a short sleep.
  if ! command -v squeue >/dev/null 2>&1; then
    echo "Warning: 'squeue' not found; sleeping 30s instead of waiting for RUNNING state." >&2
    sleep 30
    return 0
  fi

  local max_wait_s=600 # 10 minutes
  local waited_s=0
  while (( waited_s < max_wait_s )); do
    # %T may return: RUNNING, PENDING, etc. We also accept single-letter R.
    state="$(squeue -j "$JOB_ID" -h -o "%T" 2>/dev/null | head -n1 || true)"
    if [[ "$state" == "RUNNING" || "$state" == "R" ]]; then
      echo "Job $JOB_ID is RUNNING."
      return 0
    elif [[ "$state" == "FAILED" || "$state" == "F" ]]; then
      echo "Job $JOB_ID has FAILED."
      return 1
    fi
    sleep 5
    (( waited_s += 5 ))
  done

  echo "Warning: job $JOB_ID did not reach RUNNING within ${max_wait_s}s; proceeding anyway." >&2
  return 0
}

wait_until_running

echo "Waiting 60s for Jupyter to start and write logs..."
sleep 60

OUT_FILE="jupyter_logs/output-${JOB_ID}.txt"
ERR_FILE="jupyter_logs/error-${JOB_ID}.txt"

if [[ ! -f "$OUT_FILE" && ! -f "$ERR_FILE" ]]; then
  echo "Warning: log files not found yet: '$OUT_FILE' / '$ERR_FILE'." >&2
fi

extract_urls() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  # Extract http(s) URLs containing `token=`; Jupyter prints them on startup.
  # -Eo keeps only the matched URL.
  grep -Eo 'https?://[^[:space:]]*token=[^[:space:]]+' "$f" 2>/dev/null || true
}

mapfile -t urls < <(
  {
    extract_urls "$OUT_FILE"
    extract_urls "$ERR_FILE"
  } | sort -u
)

# If nothing was found, do one additional quick scan (common if logs were delayed).
if (( ${#urls[@]} == 0 )); then
  echo "No URLs found in logs yet; waiting another 30s and retrying..."
  sleep 30
  mapfile -t urls < <(
    {
      extract_urls "$OUT_FILE"
      extract_urls "$ERR_FILE"
    } | sort -u
  )
fi

if (( ${#urls[@]} == 0 )); then
  echo "Error: could not recover any Jupyter URLs containing `token=` from logs." >&2
  echo "Checked: '$OUT_FILE' and '$ERR_FILE'." >&2
  exit 2
fi

echo
echo "Recovered Jupyter URLs:"
for u in "${urls[@]}"; do
  echo "$u"
done

# Extract host + port from the first recovered URL and print tunnel command.
first_url="${urls[0]}"
host_port="$(echo "$first_url" | sed -E 's#^https?://([^/]+).*#\1#' || true)"
host_ip="${host_port%%:*}"
port_num="${host_port##*:}"

if [[ -n "$host_ip" && -n "$port_num" && "$port_num" =~ ^[0-9]+$ && "$host_ip" != "$port_num" ]]; then
  cnetid="${CNETID:-${USER:-<your-CNetID>}}"
  echo
  echo "Detected HOST_IP: $host_ip"
  echo "Detected PORT:    $port_num"
  echo
  echo "SSH tunnel command:"
  echo "ssh -N -f -L ${port_num}:${host_ip}:${port_num} ${cnetid}@midway3.rcc.uchicago.edu"
fi


