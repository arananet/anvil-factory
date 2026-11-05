import json
import subprocess
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent


class RenderCrashToleranceS4Tests(unittest.TestCase):
    def test_s4_persistent_failure_after_two_sweeps(self):
        """render-crash-tolerance S4: frames missing after 2 sweeps fail step, missing range named"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up durations.json with 2 sections
            durations = {
                "sections": {
                    "1": {"frames": 60},
                    "2": {"frames": 60}
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

            # Create fake blender that succeeds for section 2 but always fails for section 1
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text("""#!/bin/bash
# Arguments: section, total_frames, outdir, res_percent, first_frame, last_frame
s=$5; n=$6; out=$7; res=$8; a=$9; b=${10}
mkdir -p "$out"

# Section 2 works fine
if [ "$s" = "2" ]; then
    for ((f=a; f<=b; f++)); do
        printf -v fn "f_%04d.png" $f
        echo "frame $f" > "$out/$fn"
    done
    echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
    exit 0
fi

# Section 1 never writes frames (persistent failure)
echo "SECTION_RENDER_DONE s$s frames=0 seconds=0.0"
exit 1
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

            # Should fail after 2 sweep passes
            self.assertNotEqual(result.returncode, 0, "Render should fail when frames still missing after 2 sweeps")

            # Check that failure output names the missing range
            output = result.stdout + result.stderr
            self.assertIn("section 1", output.lower(), "Failure should name section 1")
            self.assertIn("1", output, "Failure should identify section 1")
            # Should mention frames or range
            self.assertTrue(
                any(word in output.lower() for word in ["frame", "range", "missing"]),
                "Failure should describe what is missing"
            )

            # Section 2 should have succeeded
            s2_frames = list((work / "frames" / "s2").glob("f_*.png"))
            self.assertEqual(len(s2_frames), 60, "Section 2 should have completed despite section 1 failure")

            # Section 1 should have no frames
            s1_dir = work / "frames" / "s1"
            s1_frames = list(s1_dir.glob("f_*.png")) if s1_dir.exists() else []
            self.assertEqual(len(s1_frames), 0, "Section 1 should have no frames")

            # Run statistics aggregation
            subprocess.run(
                ["python3", str(FACTORY / "tools" / "render_stats.py")],
                cwd=FACTORY,
                check=True
            )

            # Check render-stats.json records failed outcome
            stats = json.loads((work / "render-stats.json").read_text())
            self.assertIn("failed", stats, "Statistics should include failed outcomes")
            failed = stats["failed"]
            self.assertEqual(len(failed), 1, "Should have one failed chunk")
            self.assertEqual(failed[0]["section"], "1", "Failed chunk should be section 1")


if __name__ == "__main__":
    unittest.main()
