"""Community files renderer for ANVIL projects."""

from pathlib import Path


def render_community_files(name, description=None, contact=None):
    """Render the community file set from project metadata.

    Args:
        name: Project name
        description: Project description (optional)
        contact: Contact email for enforcement and security reporting (optional)

    Returns:
        Dictionary mapping relative file paths to rendered content
    """
    templates_dir = Path(__file__).parent.parent / "templates" / "community"

    # Prepare substitution values
    project_name = name

    # Handle contact substitution
    if contact:
        contact_line = contact
        contact_fallback = f"**Alternative contact**: {contact}"
    else:
        contact_line = "the project maintainers through GitHub private vulnerability reporting or by opening an issue in this repository"
        contact_fallback = ""

    # Read and render templates
    code_of_conduct_template = (templates_dir / "code_of_conduct.md").read_text(encoding="utf-8")
    code_of_conduct = code_of_conduct_template.replace("{{CONTACT}}", contact_line)

    contributing_template = (templates_dir / "contributing.md").read_text(encoding="utf-8")
    contributing = contributing_template.replace("{{PROJECT_NAME}}", project_name)

    security_template = (templates_dir / "security.md").read_text(encoding="utf-8")
    security = security_template.replace("{{PROJECT_NAME}}", project_name)
    security = security.replace("{{CONTACT_FALLBACK}}", contact_fallback)

    bug_report_template = (templates_dir / "bug_report.md").read_text(encoding="utf-8")
    bug_report = bug_report_template.replace("{{PROJECT_NAME}}", project_name)

    work_order_template = (templates_dir / "work_order.md").read_text(encoding="utf-8")
    work_order = work_order_template.replace("{{PROJECT_NAME}}", project_name)

    issue_config_template = (templates_dir / "issue_config.yml").read_text(encoding="utf-8")
    # Remove the placeholder repo link since we don't have the repo name yet
    issue_config = issue_config_template.replace("{{REPO_PLACEHOLDER}}", "owner/repo")

    pr_template = (templates_dir / "pull_request_template.md").read_text(encoding="utf-8")

    return {
        "CONTRIBUTING.md": contributing,
        "CODE_OF_CONDUCT.md": code_of_conduct,
        "SECURITY.md": security,
        ".github/ISSUE_TEMPLATE/bug_report.md": bug_report,
        ".github/ISSUE_TEMPLATE/work_order.md": work_order,
        ".github/ISSUE_TEMPLATE/config.yml": issue_config,
        ".github/pull_request_template.md": pr_template,
    }
