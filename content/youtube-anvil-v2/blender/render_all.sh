#!/usr/bin/env bash
# Render every section to frames/s<N>/ as PNG sequences. At most 4 blender processes at once.
# Frames that already exist are skipped (use_overwrite is off), so an interrupted render resumes.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER="${BLENDER:-blender}"
CHUNK=${CHUNK:-60}

# Generate initial job list from durations.json
python3 - > /tmp/render_jobs.txt <<'PY'
import json
import sys
d = json.load(open("durations.json"))["sections"]
for s in sorted(d, key=int):
    # Validate section ID is an integer
    try:
        int(s)
    except ValueError:
        print(f"ERROR: Invalid section ID '{s}', must be an integer", file=sys.stderr)
        sys.exit(1)
    n = d[s]["frames"]
    for a in range(1, n + 1, 60):
        print(s, n, a, min(a + 59, n))
PY

mkdir -p frames/logs

# Worker function that judges chunks by outputs and records outcome
run_chunk() {
  s=$1; n=$2; a=$3; b=$4
  out="frames/s${s}"
  log="frames/logs/render-s${s}-${a}.log"
  outcome="frames/logs/outcome-s${s}-${a}.json"

  # Check if this is a sweep pass (requeue)
  is_requeued="false"
  attempts=1
  if [ -n "${SWEEP_PASS:-}" ] && [ "$SWEEP_PASS" != "0" ]; then
    is_requeued="true"
    attempts=$((SWEEP_PASS + 1))
  fi

  # Run blender and capture exit code
  set +e
  xvfb-run -a "$BLENDER" -b -P blender/film.py -- "$s" "$n" "$out" 100 "$a" "$b" > "$log" 2>&1
  exit_code=$?
  set -e

  # Judge chunk by outputs: all frames exist AND DONE line with correct count
  expected_count=$((b - a + 1))
  frames_exist=true
  for ((f=a; f<=b; f++)); do
    frame_file=$(printf "%s/f_%04d.png" "$out" $f)
    if [ ! -f "$frame_file" ]; then
      frames_exist=false
      break
    fi
  done

  done_count=0
  if grep -q "SECTION_RENDER_DONE" "$log" 2>/dev/null; then
    done_count=$(grep "SECTION_RENDER_DONE" "$log" | sed -n 's/.*frames=\([0-9]*\).*/\1/p' | head -1)
  fi

  success=false
  if [ "$frames_exist" = "true" ] && [ "$done_count" = "$expected_count" ]; then
    success=true
  fi

  # Write outcome record using JSON encoder
  frames_on_disk=$(find "$out" -name "f_*.png" 2>/dev/null | wc -l)
  if [ "$is_requeued" = "true" ]; then
    python3 << PYEND > "$outcome"
import json
print(json.dumps({
  'section': '$s',
  'first_frame': $a,
  'last_frame': $b,
  'exit_code': $exit_code,
  'success': '$success' == 'true',
  'frames_expected': $expected_count,
  'frames_on_disk': $frames_on_disk,
  'requeued': True,
  'attempts': $attempts
}))
PYEND
  else
    python3 << PYEND > "$outcome"
import json
print(json.dumps({
  'section': '$s',
  'first_frame': $a,
  'last_frame': $b,
  'exit_code': $exit_code,
  'success': '$success' == 'true',
  'frames_expected': $expected_count,
  'frames_on_disk': $frames_on_disk
}))
PYEND
  fi

  if [ "$success" = "true" ]; then
    grep -h "SECTION_RENDER_DONE" "$log" || true
  fi

  # Always return 0 so queue never aborts
  return 0
}

export -f run_chunk
export BLENDER

# Initial queue
cat /tmp/render_jobs.txt | xargs -P 4 -L 1 bash -c 'run_chunk "$@"' _

# Completion sweeps: up to 2 passes
for sweep in 1 2; do
  # Compute missing frames per section
  python3 - > /tmp/sweep_jobs.txt <<'PY'
import json
import sys
from pathlib import Path

durations = json.load(open("durations.json"))["sections"]
chunk_size = 60

for s in sorted(durations, key=int):
    # Validate section ID is an integer
    try:
        int(s)
    except ValueError:
        print(f"ERROR: Invalid section ID '{s}', must be an integer", file=sys.stderr)
        sys.exit(1)
    expected = durations[s]["frames"]
    frames_dir = Path(f"frames/s{s}")

    # Find which frames exist
    existing = set()
    if frames_dir.exists():
        for f in frames_dir.glob("f_*.png"):
            frame_num = int(f.stem.split("_")[1])
            existing.add(frame_num)

    # Find missing ranges
    missing_ranges = []
    range_start = None
    for frame in range(1, expected + 1):
        if frame not in existing:
            if range_start is None:
                range_start = frame
        else:
            if range_start is not None:
                missing_ranges.append((range_start, frame - 1))
                range_start = None
    if range_start is not None:
        missing_ranges.append((range_start, expected))

    # Chunk missing ranges at chunk_size
    for start, end in missing_ranges:
        for a in range(start, end + 1, chunk_size):
            b = min(a + chunk_size - 1, end)
            print(s, expected, a, b)
PY

  # If no missing frames, we're done
  if [ ! -s /tmp/sweep_jobs.txt ]; then
    break
  fi

  # Run sweep queue with SWEEP_PASS set
  export SWEEP_PASS=$sweep
  cat /tmp/sweep_jobs.txt | xargs -P 4 -L 1 bash -c 'run_chunk "$@"' _
  unset SWEEP_PASS
done

# Check for still-missing frames after sweeps
python3 - <<'PY'
import json
import sys
from pathlib import Path

durations = json.load(open("durations.json"))["sections"]
missing = []

for s in sorted(durations, key=int):
    # Validate section ID is an integer
    try:
        int(s)
    except ValueError:
        print(f"ERROR: Invalid section ID '{s}', must be an integer", file=sys.stderr)
        sys.exit(1)
    expected = durations[s]["frames"]
    frames_dir = Path(f"frames/s{s}")

    existing = set()
    if frames_dir.exists():
        for f in frames_dir.glob("f_*.png"):
            frame_num = int(f.stem.split("_")[1])
            existing.add(frame_num)

    # Find missing ranges
    missing_ranges = []
    range_start = None
    for frame in range(1, expected + 1):
        if frame not in existing:
            if range_start is None:
                range_start = frame
        else:
            if range_start is not None:
                missing_ranges.append((range_start, frame - 1))
                range_start = None
    if range_start is not None:
        missing_ranges.append((range_start, expected))

    if missing_ranges:
        for start, end in missing_ranges:
            missing.append(f"section {s} frames {start}-{end}")

if missing:
    print("ERROR: Missing frames after 2 sweep passes:")
    for m in missing:
        print(f"  {m}")
    sys.exit(1)
PY
