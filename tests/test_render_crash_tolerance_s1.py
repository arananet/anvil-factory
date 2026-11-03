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
s=$5; a=$7; b=$8; out=$6
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
                env={"PYTHONPATH": str(FACTORY)},
                check=True
            )

            # Check render-stats.json records tolerated_crash for section 1
            stats = json.loads((work / "render-stats.json").read_text())
            self.assertIn("tolerated_crash", stats, "Statistics should include tolerated_crash outcomes")
            tolerated = stats["tolerated_crash"]
            self.assertEqual(len(tolerated), 1, "Should have one tolerated crash")
            self.assertEqual(tolerated[0]["section"], "1", "Tolerated crash should be section 1")
            self.assertEqual(tolerated[0]["first_frame"], 1, "Tolerated crash should be at frame 1")


if __name__ == "__main__":
    unittest.main()
