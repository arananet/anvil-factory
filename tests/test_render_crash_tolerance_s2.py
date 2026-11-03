import json
import subprocess
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent


class RenderCrashToleranceS2Tests(unittest.TestCase):
    def test_s2_failing_chunk_does_not_abort_queue(self):
        """render-crash-tolerance S2: first job fails hard, all later jobs still launch"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up durations.json with 4 sections to verify all jobs run
            durations = {
                "sections": {
                    "1": {"frames": 60},
                    "2": {"frames": 60},
                    "3": {"frames": 60},
                    "4": {"frames": 60}
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

            # Invocation log to track which chunks ran
            invocation_log = work / "invocations.log"

            # Create fake blender that logs invocations, fails for section 1, succeeds for others
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text(f"""#!/bin/bash
# Arguments: section, total_frames, outdir, res_percent, first_frame, last_frame
s=$5; n=$6; out=$7; res=$8; a=$9; b=${{10}}
mkdir -p "$out"

# Log this invocation
echo "s=$s a=$a b=$b" >> {invocation_log}

# Section 1: hard failure (no frames, no DONE, exit 1)
if [ "$s" = "1" ]; then
    exit 1
fi

# All other sections: success
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

            # Read invocation log
            self.assertTrue(invocation_log.exists(), "Invocation log should exist")
            invocations = invocation_log.read_text().strip().split('\n')

            # Verify all 4 sections were attempted in initial queue
            sections_invoked = set()
            for inv in invocations:
                # Parse "s=N a=A b=B"
                parts = inv.split()
                for part in parts:
                    if part.startswith("s="):
                        sections_invoked.add(part.split("=")[1])

            # All sections should have been invoked
            self.assertIn("1", sections_invoked, "Section 1 (failing) should have been invoked")
            self.assertIn("2", sections_invoked, "Section 2 should have been invoked despite section 1 failure")
            self.assertIn("3", sections_invoked, "Section 3 should have been invoked despite section 1 failure")
            self.assertIn("4", sections_invoked, "Section 4 should have been invoked despite section 1 failure")

            # At minimum, we should see section 1 fail and sections 2-4 succeed in initial queue
            # (Plus sweeps for section 1, but we care about the queue not aborting)
            initial_invocations = [inv for inv in invocations if any(f"s={s}" in inv for s in ["1", "2", "3", "4"])]
            self.assertGreaterEqual(len(initial_invocations), 4,
                "All 4 sections should have had initial queue invocations")

            # Verify sections 2-4 succeeded (frames exist)
            s2_frames = list((work / "frames" / "s2").glob("f_*.png"))
            s3_frames = list((work / "frames" / "s3").glob("f_*.png"))
            s4_frames = list((work / "frames" / "s4").glob("f_*.png"))

            self.assertEqual(len(s2_frames), 60, "Section 2 should have completed despite section 1 failure")
            self.assertEqual(len(s3_frames), 60, "Section 3 should have completed despite section 1 failure")
            self.assertEqual(len(s4_frames), 60, "Section 4 should have completed despite section 1 failure")

            # Section 1 should have failed (no frames or partial frames after sweeps)
            s1_dir = work / "frames" / "s1"
            s1_frames = list(s1_dir.glob("f_*.png")) if s1_dir.exists() else []
            self.assertLess(len(s1_frames), 60, "Section 1 should not have completed")


if __name__ == "__main__":
    unittest.main()
