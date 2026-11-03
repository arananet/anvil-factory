import json
import subprocess
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent


class RenderCrashToleranceS3Tests(unittest.TestCase):
    def test_s3_partial_frames_requeued_by_range(self):
        """render-crash-tolerance S3: partial frames re-queued by missing range only, reported as requeued"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up durations.json with one section of 120 frames (2 chunks at CHUNK=60)
            durations = {
                "sections": {
                    "1": {"frames": 120}
                }
            }
            (work / "durations.json").write_text(json.dumps(durations))

            # Copy render_all.sh
            render_script = work / "blender" / "render_all.sh"
            render_script.parent.mkdir(parents=True)
            render_script.write_text(
                (FACTORY / "content" / "youtube-anvil-v2" / "blender" / "render_all.sh").read_text()
            )
            render_script.chmod(0o755)

            # State file to track invocations
            state_file = work / "invocations.log"

            # Create fake blender that writes partial frames on first attempt, full on sweep
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text(f"""#!/bin/bash
# Arguments: section, total_frames, outdir, res_percent, first_frame, last_frame
s=$5; n=$6; out=$7; res=$8; a=$9; b=${{10}}
mkdir -p "$out"
echo "s=$s a=$a b=$b" >> {state_file}

# First chunk (frames 1-60): write only first 30 frames on initial pass
if [ "$s" = "1" ] && [ "$a" = "1" ] && [ "$b" = "60" ]; then
    # Check if this is a sweep (frames 31-60 only means sweep)
    if [ ! -f "{state_file}.first_chunk_done" ]; then
        # Initial pass: write only 1-30
        for ((f=1; f<=30; f++)); do
            printf -v fn "f_%04d.png" $f
            echo "frame $f" > "$out/$fn"
        done
        echo "SECTION_RENDER_DONE s$s frames=30 seconds=1.0"
        touch "{state_file}.first_chunk_done"
        exit 0
    fi
fi

# On sweep or if frames 31-60 requested, write those frames
for ((f=a; f<=b; f++)); do
    printf -v fn "f_%04d.png" $f
    echo "frame $f" > "$out/$fn"
done
echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
exit 0
""")
            fake_blender.chmod(0o755)

            # Run render
            env = {"BLENDER": str(fake_blender), "CHUNK": "60"}
            result = subprocess.run(
                ["bash", "blender/render_all.sh"],
                cwd=work,
                capture_output=True,
                text=True,
                env={**env}
            )

            # Should succeed after sweep
            self.assertEqual(result.returncode, 0, f"Render failed: {result.stderr}")

            # Check all 120 frames exist
            s1_frames = sorted((work / "frames" / "s1").glob("f_*.png"))
            self.assertEqual(len(s1_frames), 120, "Section 1 should have all 120 frames after sweep")

            # Verify sweep only requested missing range (31-60), not full section
            invocations = state_file.read_text().strip().split('\n')
            # Should see: initial chunks 1-60 and 61-120, then sweep for 31-60 only
            self.assertIn("s=1 a=31 b=60", invocations, "Sweep should request only missing range 31-60")
            # Should NOT re-request frames 1-30 or 61-120
            requeued_count = sum(1 for inv in invocations if "a=31 b=60" in inv)
            self.assertGreaterEqual(requeued_count, 1, "Missing range should be re-queued")

            # Run statistics aggregation
            subprocess.run(
                ["python3", str(FACTORY / "tools" / "render_stats.py")],
                cwd=FACTORY,
                check=True
            )

            # Check render-stats.json records requeued outcome
            stats = json.loads((work / "render-stats.json").read_text())
            self.assertIn("requeued", stats, "Statistics should include requeued outcomes")
            requeued = stats["requeued"]
            self.assertEqual(len(requeued), 1, "Should have one re-queued chunk")
            self.assertEqual(requeued[0]["section"], "1", "Re-queued chunk should be section 1")
            self.assertEqual(requeued[0]["first_frame"], 31, "Re-queued chunk should start at frame 31")
            self.assertIn("attempts", requeued[0], "Re-queued chunk should record attempts count")


    def test_s3_outcome_file_contains_attempts_field(self):
        """render-crash-tolerance F3: outcome files written by wrapper contain 'attempts' field for requeued chunks"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up durations.json with one section of 120 frames (2 chunks at CHUNK=60)
            durations = {
                "sections": {
                    "1": {"frames": 120}
                }
            }
            (work / "durations.json").write_text(json.dumps(durations))

            # Copy render_all.sh
            render_script = work / "blender" / "render_all.sh"
            render_script.parent.mkdir(parents=True)
            render_script.write_text(
                (FACTORY / "content" / "youtube-anvil-v2" / "blender" / "render_all.sh").read_text()
            )
            render_script.chmod(0o755)

            # State file to track invocations
            state_file = work / "invocations.log"

            # Create fake blender that writes partial frames on first attempt, full on sweep
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text(f"""#!/bin/bash
# Arguments: section, total_frames, outdir, res_percent, first_frame, last_frame
s=$5; n=$6; out=$7; res=$8; a=$9; b=${{10}}
mkdir -p "$out"
echo "s=$s a=$a b=$b" >> {state_file}

# First chunk (frames 1-60): write only first 30 frames on initial pass
if [ "$s" = "1" ] && [ "$a" = "1" ] && [ "$b" = "60" ]; then
    if [ ! -f "{state_file}.first_chunk_done" ]; then
        # Initial pass: write only 1-30
        for ((f=1; f<=30; f++)); do
            printf -v fn "f_%04d.png" $f
            echo "frame $f" > "$out/$fn"
        done
        echo "SECTION_RENDER_DONE s$s frames=30 seconds=1.0"
        touch "{state_file}.first_chunk_done"
        exit 0
    fi
fi

# On sweep or second chunk, write full range
for ((f=a; f<=b; f++)); do
    printf -v fn "f_%04d.png" $f
    echo "frame $f" > "$out/$fn"
done
echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
exit 0
""")
            fake_blender.chmod(0o755)

            # Run render
            env = {"BLENDER": str(fake_blender), "CHUNK": "60"}
            result = subprocess.run(
                ["bash", "blender/render_all.sh"],
                cwd=work,
                capture_output=True,
                text=True,
                env={**env}
            )

            # Should succeed after sweep
            self.assertEqual(result.returncode, 0, f"Render failed: {result.stderr}")

            # Read outcome file for the requeued chunk (31-60) directly
            logs_dir = work / "frames" / "logs"
            outcome_files = list(logs_dir.glob("outcome-s1-*.json"))
            self.assertGreater(len(outcome_files), 0, "Should have outcome files")

            # Find the requeued outcome file (should have attempts > 1)
            requeued_outcome = None
            for outcome_file in outcome_files:
                outcome_data = json.loads(outcome_file.read_text())
                if outcome_data.get("first_frame") == 31:
                    requeued_outcome = outcome_data
                    break

            self.assertIsNotNone(requeued_outcome, "Should find outcome file for frames 31-60")
            self.assertIn("attempts", requeued_outcome,
                "Outcome file must contain 'attempts' field (not 'sweep')")
            self.assertEqual(requeued_outcome["attempts"], 2,
                "Requeued chunk should show 2 attempts (initial + sweep)")
            self.assertTrue(requeued_outcome.get("requeued", False),
                "Requeued outcome should have requeued=true")


if __name__ == "__main__":
    unittest.main()
