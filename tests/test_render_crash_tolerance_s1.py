import json
import subprocess
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent


class RenderCrashToleranceS1Tests(unittest.TestCase):
    def test_s1_chunk_crash_after_completion_tolerated(self):
        """render-crash-tolerance S1: chunk with frames and DONE but exit 1 counts success, recorded as tolerated_crash"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up minimal durations.json with 2 sections
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

            # Create fake blender that writes frames and DONE but exits 1 for first chunk, 0 for second
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text("""#!/bin/bash
# Arguments: section, total_frames, outdir, res_percent, first_frame, last_frame
s=$5; n=$6; out=$7; res=$8; a=$9; b=${10}
mkdir -p "$out"
# Write all frames
for ((f=a; f<=b; f++)); do
    printf -v fn "f_%04d.png" $f
    echo "frame $f" > "$out/$fn"
done
# Write DONE line
echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
# First chunk exits 1 (crash), second chunk exits 0 (clean)
if [ "$s" = "1" ] && [ "$a" = "1" ]; then
    exit 1
fi
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

            # Should succeed overall
            self.assertEqual(result.returncode, 0, f"Render failed: {result.stderr}")

            # Check frames exist for both sections
            s1_frames = list((work / "frames" / "s1").glob("f_*.png"))
            s2_frames = list((work / "frames" / "s2").glob("f_*.png"))
            self.assertEqual(len(s1_frames), 60, "Section 1 should have 60 frames")
            self.assertEqual(len(s2_frames), 60, "Section 2 should have 60 frames")

            # Run statistics aggregation
            subprocess.run(
                ["python3", str(FACTORY / "tools" / "render_stats.py")],
                cwd=FACTORY,
                env={"PYTHONPATH": str(FACTORY), "VIDEO_CONTENT_DIR": str(work)},
                check=True
            )

            # Check render-stats.json records tolerated_crash for section 1
            stats = json.loads((work / "render-stats.json").read_text())
            self.assertIn("tolerated_crash", stats, "Statistics should include tolerated_crash outcomes")
            tolerated = stats["tolerated_crash"]
            self.assertEqual(len(tolerated), 1, "Should have one tolerated crash")
            self.assertEqual(tolerated[0]["section"], "1", "Tolerated crash should be section 1")
            self.assertEqual(tolerated[0]["first_frame"], 1, "Tolerated crash should be at frame 1")

    def test_s1_invocation_arguments_match_film_py_contract(self):
        """render-crash-tolerance S1 (F2): verify wrapper invokes with all 6 film.py arguments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up minimal durations.json
            durations = {
                "sections": {
                    "1": {"frames": 60}
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

            # Invocation log
            invocation_log = work / "invocations.log"

            # Create fake blender that records all its arguments
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text(f"""#!/bin/bash
# Record all positional arguments after the --
echo "args: $5 | $6 | $7 | $8 | $9 | ${{10}}" >> {invocation_log}
s=$5; n=$6; out=$7; res=$8; a=$9; b=${{10}}
mkdir -p "$out"
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

            self.assertEqual(result.returncode, 0, f"Render failed: {result.stderr}")

            # Verify invocation arguments
            self.assertTrue(invocation_log.exists(), "Invocation log should exist")
            invocations = invocation_log.read_text().strip().split('\n')
            
            # Should have one invocation for section 1, frames 1-60
            self.assertGreaterEqual(len(invocations), 1, "Should have at least one invocation")
            
            # Parse first invocation: args: section | total_frames | outdir | res_percent | first_frame | last_frame
            first_inv = invocations[0]
            self.assertTrue(first_inv.startswith("args: "), "Invocation should start with 'args: '")
            
            # Extract the 6 arguments
            args_part = first_inv.replace("args: ", "")
            args = [a.strip() for a in args_part.split("|")]
            
            self.assertEqual(len(args), 6, f"Should have exactly 6 arguments, got {len(args)}: {args}")
            self.assertEqual(args[0], "1", "Arg 1 should be section ID")
            self.assertEqual(args[1], "60", "Arg 2 should be total frames")
            self.assertTrue(args[2].endswith("frames/s1"), f"Arg 3 should be output directory, got {args[2]}")
            self.assertEqual(args[3], "100", "Arg 4 should be resolution percent (100)")
            self.assertEqual(args[4], "1", "Arg 5 should be first frame")
            self.assertEqual(args[5], "60", "Arg 6 should be last frame")


    def test_s1_invalid_section_id_rejected(self):
        """render-crash-tolerance F4a: invalid section IDs in durations.json are rejected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up durations.json with invalid section ID (non-integer)
            durations = {
                "sections": {
                    "1": {"frames": 60},
                    "not-a-number": {"frames": 60}
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

            # Create minimal fake blender
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text("""#!/bin/bash
s=$5; n=$6; out=$7; res=$8; a=$9; b=${10}
mkdir -p "$out"
for ((f=a; f<=b; f++)); do
    printf -v fn "f_%04d.png" $f
    echo "frame $f" > "$out/$fn"
done
echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
exit 0
""")
            fake_blender.chmod(0o755)

            # Run render - should fail due to invalid section ID
            env = {"BLENDER": str(fake_blender), "CHUNK": "60"}
            result = subprocess.run(
                ["bash", "blender/render_all.sh"],
                cwd=work,
                capture_output=True,
                text=True,
                env={**env}
            )

            # Should fail with error about invalid section ID
            self.assertNotEqual(result.returncode, 0, "Render should fail with invalid section ID")
            output = result.stdout + result.stderr
            # Error could be from int() conversion or explicit validation
            self.assertTrue(
                "Invalid section ID" in output or "invalid literal for int()" in output,
                f"Error should mention invalid section ID, got: {output}"
            )
            self.assertIn("not-a-number", output, "Error should identify the invalid section ID")


if __name__ == "__main__":
    unittest.main()
