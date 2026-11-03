import json
import subprocess
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent


class RenderCrashToleranceS5Tests(unittest.TestCase):
    def test_s5_statistics_record_all_outcome_classes(self):
        """render-crash-tolerance S5: statistics record clean_exit, tolerated_crash, requeued, failed outcomes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir) / "work"
            work.mkdir()

            # Set up durations.json with 4 sections to cover all outcome classes
            durations = {
                "sections": {
                    "1": {"frames": 60},  # Will be clean exit
                    "2": {"frames": 60},  # Will be tolerated crash
                    "3": {"frames": 90},  # Will need re-queue (partial then complete)
                    "4": {"frames": 60}   # Will fail persistently
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

            # State tracking
            state_file = work / "state.log"

            # Create fake blender with different behaviors per section
            fake_blender = work / "fake_blender.sh"
            fake_blender.write_text(f"""#!/bin/bash
s=$5; a=$7; b=$8; out=$6
mkdir -p "$out"

# Section 1: clean exit (frames + DONE, exit 0)
if [ "$s" = "1" ]; then
    for ((f=a; f<=b; f++)); do
        printf -v fn "f_%04d.png" $f
        echo "frame $f" > "$out/$fn"
    done
    echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
    exit 0
fi

# Section 2: tolerated crash (frames + DONE, exit 1)
if [ "$s" = "2" ]; then
    for ((f=a; f<=b; f++)); do
        printf -v fn "f_%04d.png" $f
        echo "frame $f" > "$out/$fn"
    done
    echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
    exit 1
fi

# Section 3: partial then complete (re-queue case)
if [ "$s" = "3" ]; then
    # First chunk (1-60): only write half on first attempt
    if [ "$a" = "1" ] && [ ! -f "{state_file}.s3_first_done" ]; then
        for ((f=1; f<=30; f++)); do
            printf -v fn "f_%04d.png" $f
            echo "frame $f" > "$out/$fn"
        done
        echo "SECTION_RENDER_DONE s$s frames=30 seconds=1.0"
        touch "{state_file}.s3_first_done"
        exit 0
    fi
    # On sweep or second chunk, write full range
    for ((f=a; f<=b; f++)); do
        printf -v fn "f_%04d.png" $f
        echo "frame $f" > "$out/$fn"
    done
    echo "SECTION_RENDER_DONE s$s frames=$((b-a+1)) seconds=1.5"
    exit 0
fi

# Section 4: persistent failure (no frames)
if [ "$s" = "4" ]; then
    echo "SECTION_RENDER_DONE s$s frames=0 seconds=0.0"
    exit 1
fi

exit 0
""")
            fake_blender.chmod(0o755)

            # Run render (will fail due to section 4, but that's expected)
            env = {"BLENDER": str(fake_blender), "CHUNK": "60"}
            result = subprocess.run(
                ["bash", "blender/render_all.sh"],
                cwd=work,
                capture_output=True,
                text=True,
                env={**env}
            )

            # Run statistics aggregation
            subprocess.run(
                ["python3", str(FACTORY / "tools" / "render_stats.py")],
                cwd=FACTORY,
                check=True
            )

            # Check render-stats.json has all outcome classes
            stats_file = work / "render-stats.json"
            self.assertTrue(stats_file.exists(), "render-stats.json should be created")
            stats = json.loads(stats_file.read_text())

            # Verify existing keys are preserved
            self.assertIn("blender_version", stats, "Existing key blender_version should be preserved")
            self.assertIn("renderer", stats, "Existing key renderer should be preserved")
            self.assertIn("resolution", stats, "Existing key resolution should be preserved")
            self.assertIn("fps", stats, "Existing key fps should be preserved")
            self.assertIn("sections", stats, "Existing key sections should be preserved")
            self.assertIn("total_frames_on_disk", stats, "Existing key total_frames_on_disk should be preserved")

            # Verify all outcome classes are present
            self.assertIn("clean_exit", stats, "Statistics should include clean_exit outcomes")
            self.assertIn("tolerated_crash", stats, "Statistics should include tolerated_crash outcomes")
            self.assertIn("requeued", stats, "Statistics should include requeued outcomes")
            self.assertIn("failed", stats, "Statistics should include failed outcomes")

            # Verify each outcome class has expected entries
            clean_exits = stats["clean_exit"]
            self.assertGreaterEqual(len(clean_exits), 1, "Should have at least one clean exit (section 1)")
            self.assertTrue(any(c["section"] == "1" for c in clean_exits), "Section 1 should be in clean_exit")

            tolerated_crashes = stats["tolerated_crash"]
            self.assertGreaterEqual(len(tolerated_crashes), 1, "Should have at least one tolerated crash (section 2)")
            self.assertTrue(any(c["section"] == "2" for c in tolerated_crashes), "Section 2 should be in tolerated_crash")

            requeued = stats["requeued"]
            self.assertGreaterEqual(len(requeued), 1, "Should have at least one re-queued chunk (section 3)")
            self.assertTrue(any(c["section"] == "3" for c in requeued), "Section 3 should have re-queued chunk")
            # Re-queued chunks should have attempts count
            for req in requeued:
                self.assertIn("attempts", req, "Re-queued chunk should record attempts count")

            failed = stats["failed"]
            self.assertGreaterEqual(len(failed), 1, "Should have at least one failed chunk (section 4)")
            self.assertTrue(any(c["section"] == "4" for c in failed), "Section 4 should be in failed")


if __name__ == "__main__":
    unittest.main()
