#!/usr/bin/env bash
# Render every section to frames/s<N>/ as PNG sequences. At most 4 blender processes at once.
# Frames that already exist are skipped (use_overwrite is off), so an interrupted render resumes.
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER="${BLENDER:-blender}"
CHUNK=${CHUNK:-60}
python3 - > /tmp/render_jobs.txt <<'PY'
import json
d = json.load(open("durations.json"))["sections"]
for s in sorted(d, key=int):
    n = d[s]["frames"]
    for a in range(1, n + 1, 60):
        print(s, n, a, min(a + 59, n))
PY
mkdir -p frames/logs
cat /tmp/render_jobs.txt | xargs -P 4 -L 1 bash -c '
  s=$0; n=$1; a=$2; b=$3
  xvfb-run -a "'"$BLENDER"'" -b -P blender/film.py -- $s $n frames/s$s 100 $a $b > frames/logs/render-s${s}-${a}.log 2>&1 || { echo "FAILED s$s $a"; exit 255; }
  grep -h "SECTION_RENDER_DONE" frames/logs/render-s${s}-${a}.log
'
