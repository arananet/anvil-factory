import re
import tempfile
import unittest
from pathlib import Path

from anvil.community import render_community_files
from anvil.onboard import onboard_project
from anvil.scaffold import init_project


class CommunityFilesTests(unittest.TestCase):
    def test_s1_init_project_creates_full_community_set(self):
        """community-by-default S1: scaffolded project has all seven files, values substituted, no template residue"""
        with tempfile.TemporaryDirectory() as tmp:
            root = init_project(
                Path(tmp) / "demo",
                "Demo Project",
                description="A demonstration project for testing",
                contact="security@example.org"
            )
            expected_files = [
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                "SECURITY.md",
                ".github/ISSUE_TEMPLATE/bug_report.md",
                ".github/ISSUE_TEMPLATE/work_order.md",
                ".github/ISSUE_TEMPLATE/config.yml",
                ".github/pull_request_template.md"
            ]
            for rel_path in expected_files:
                path = root / rel_path
                self.assertTrue(path.exists(), f"{rel_path} should exist")
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("{{", content, f"{rel_path} contains template marker {{{{")
                self.assertNotIn("}}", content, f"{rel_path} contains template marker }}}}")
                self.assertNotIn("TODO", content, f"{rel_path} contains TODO marker")
                self.assertNotIn("[INSERT", content.upper(), f"{rel_path} contains bracketed insert instruction")

            # Verify project name appears in files
            contributing = (root / "CONTRIBUTING.md").read_text(encoding="utf-8")
            self.assertIn("Demo Project", contributing)

            # Verify contact substitution in CODE_OF_CONDUCT.md
            conduct = (root / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
            self.assertIn("security@example.org", conduct)

            # Verify contact in SECURITY.md
            security = (root / "SECURITY.md").read_text(encoding="utf-8")
            self.assertIn("security@example.org", security)

    def test_s2_onboard_preserves_existing_contributing(self):
        """community-by-default S2: onboard preserves existing CONTRIBUTING.md, creates the other six"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "legacy"
            root.mkdir(parents=True)
            (root / "README.md").write_text("# Legacy\n\nAn existing project.\n")

            # Create a recognizable CONTRIBUTING.md with sentinel content
            sentinel = "# Our Custom Contributing Guide\n\nThis is the existing content that must not change.\n"
            (root / "CONTRIBUTING.md").write_text(sentinel)

            result = onboard_project(
                root,
                name="Legacy Project",
                description="An existing project",
                contact="legacy@example.org"
            )

            # CONTRIBUTING.md must be byte-identical and in the kept list
            self.assertEqual((root / "CONTRIBUTING.md").read_text(encoding="utf-8"), sentinel)
            self.assertIn("CONTRIBUTING.md", result["kept"])

            # The other six community files should be created
            expected_created = [
                "CODE_OF_CONDUCT.md",
                "SECURITY.md",
                ".github/ISSUE_TEMPLATE/bug_report.md",
                ".github/ISSUE_TEMPLATE/work_order.md",
                ".github/ISSUE_TEMPLATE/config.yml",
                ".github/pull_request_template.md"
            ]
            for rel_path in expected_created:
                path = root / rel_path
                self.assertTrue(path.exists(), f"{rel_path} should exist")
                self.assertIn(rel_path, result["created"])

            # Verify ONBOARDING.md reflects both kept and created
            onboarding = (root / "ONBOARDING.md").read_text(encoding="utf-8")
            self.assertIn("CONTRIBUTING.md", onboarding)
            self.assertIn("CODE_OF_CONDUCT.md", onboarding)

    def test_s3_scaffold_and_onboard_produce_identical_files(self):
        """community-by-default S3: same metadata renders identical community files through both doors"""
        metadata = {
            "name": "Identical Project",
            "description": "Testing consistency across doors",
            "contact": "consistent@example.org"
        }

        with tempfile.TemporaryDirectory() as tmp:
            # Scaffold door
            scaffold_root = init_project(
                Path(tmp) / "scaffold",
                metadata["name"],
                description=metadata["description"],
                contact=metadata["contact"]
            )

            # Onboard door
            onboard_root = Path(tmp) / "onboard"
            onboard_root.mkdir(parents=True)
            (onboard_root / "README.md").write_text("# Onboard\n\nA project to onboard.\n")
            onboard_project(
                onboard_root,
                name=metadata["name"],
                description=metadata["description"],
                contact=metadata["contact"]
            )

            # Compare the seven community files
            community_files = [
                "CONTRIBUTING.md",
                "CODE_OF_CONDUCT.md",
                "SECURITY.md",
                ".github/ISSUE_TEMPLATE/bug_report.md",
                ".github/ISSUE_TEMPLATE/work_order.md",
                ".github/ISSUE_TEMPLATE/config.yml",
                ".github/pull_request_template.md"
            ]

            for rel_path in community_files:
                scaffold_content = (scaffold_root / rel_path).read_text(encoding="utf-8")
                onboard_content = (onboard_root / rel_path).read_text(encoding="utf-8")
                self.assertEqual(
                    scaffold_content,
                    onboard_content,
                    f"{rel_path} differs between scaffold and onboard doors"
                )

    def test_s4_contact_substitution_and_no_hardcoded_identity(self):
        """community-by-default S4: contact from configuration only, no hardcoded personal data"""
        distinctive_contact = "distinctive-security-team@example.org"

        with tempfile.TemporaryDirectory() as tmp:
            root = init_project(
                Path(tmp) / "contact-test",
                "Contact Test Project",
                description="Testing contact substitution",
                contact=distinctive_contact
            )

            conduct = (root / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
            security = (root / "SECURITY.md").read_text(encoding="utf-8")

            # Verify the distinctive contact appears as enforcement and reporting contact
            self.assertIn(distinctive_contact, conduct, "Contact must appear in CODE_OF_CONDUCT.md")
            self.assertIn(distinctive_contact, security, "Contact must appear in SECURITY.md")

            # Verify no other email-shaped strings appear (pattern: word@word.word)
            email_pattern = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')

            for file_name, content in [
                ("CODE_OF_CONDUCT.md", conduct),
                ("SECURITY.md", security),
                ("CONTRIBUTING.md", (root / "CONTRIBUTING.md").read_text(encoding="utf-8")),
                (".github/ISSUE_TEMPLATE/bug_report.md", (root / ".github/ISSUE_TEMPLATE/bug_report.md").read_text(encoding="utf-8")),
                (".github/ISSUE_TEMPLATE/work_order.md", (root / ".github/ISSUE_TEMPLATE/work_order.md").read_text(encoding="utf-8")),
                (".github/pull_request_template.md", (root / ".github/pull_request_template.md").read_text(encoding="utf-8"))
            ]:
                emails = email_pattern.findall(content)
                for email in emails:
                    self.assertEqual(
                        email,
                        distinctive_contact,
                        f"{file_name} contains unexpected email: {email}"
                    )

    def test_s4_no_contact_fallback_to_github(self):
        """community-by-default S4: with no contact, enforcement and reporting point at GitHub"""
        with tempfile.TemporaryDirectory() as tmp:
            root = init_project(
                Path(tmp) / "no-contact",
                "No Contact Project",
                description="Testing fallback when no contact is configured"
            )

            conduct = (root / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
            security = (root / "SECURITY.md").read_text(encoding="utf-8")

            # Verify no email addresses appear
            email_pattern = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
            self.assertEqual(len(email_pattern.findall(conduct)), 0, "CODE_OF_CONDUCT.md should contain no email when contact is not configured")

            # Verify GitHub references for enforcement and reporting
            self.assertIn("private vulnerability reporting", security.lower())
            self.assertIn("issue", security.lower())

    def test_renderer_produces_complete_set(self):
        """community-by-default: renderer returns mapping for all seven files"""
        files = render_community_files(
            name="Test Project",
            description="A test project",
            contact="test@example.org"
        )

        expected_paths = [
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/work_order.md",
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/pull_request_template.md"
        ]

        self.assertEqual(set(files.keys()), set(expected_paths), "Renderer must return exactly the seven community files")

        for path, content in files.items():
            self.assertIsInstance(content, str, f"{path} content must be a string")
            self.assertGreater(len(content), 0, f"{path} content must not be empty")


if __name__ == "__main__":
    unittest.main()
