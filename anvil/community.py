"""Community files renderer for ANVIL projects."""

import re
from pathlib import Path


def render_community_files(name, description=None, contact=None):
    """Render the community file set from project metadata.

    Args:
        name: Project name
        description: Project description (optional)
        contact: Contact email for enforcement and security reporting (optional)

    Returns:
        Dictionary mapping relative file paths to rendered content

    Raises:
        ValueError: If inputs contain newlines, are malformed, exceed length limits, or name is empty
    """
    # Validate name: required, no newlines, max 200 chars
    if not name or not name.strip():
        raise ValueError("Project name cannot be empty")
    if '\n' in name or '\r' in name:
        raise ValueError("Project name cannot contain newline characters")
    if len(name) > 200:
        raise ValueError("Project name cannot exceed 200 characters")

    # Validate description: optional, no newlines, max 500 chars
    if description:
        if '\n' in description or '\r' in description:
            raise ValueError("Project description cannot contain newline characters")
        if len(description) > 500:
            raise ValueError("Project description cannot exceed 500 characters")

    # Validate contact: optional, must be email format, no newlines, max 100 chars
    if contact:
        if '\n' in contact or '\r' in contact:
            raise ValueError("Contact email cannot contain newline characters")
        if len(contact) > 100:
            raise ValueError("Contact email cannot exceed 100 characters")
        # Validate email format
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(contact):
            raise ValueError("Contact must be a valid email address")

    templates_dir = Path(__file__).parent.parent / "templates" / "community"

    # Prepare substitution values
    project_name = name
    project_description = description if description else ""

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
    # If description is empty, remove the placeholder line entirely to avoid blank lines
    if project_description:
        contributing = contributing.replace("{{PROJECT_DESCRIPTION}}\n\n", project_description + "\n\n")
    else:
        contributing = contributing.replace("{{PROJECT_DESCRIPTION}}\n\n", "")

    security_template = (templates_dir / "security.md").read_text(encoding="utf-8")
    security = security_template.replace("{{PROJECT_NAME}}", project_name)
    security = security.replace("{{CONTACT_FALLBACK}}", contact_fallback)

    bug_report_template = (templates_dir / "bug_report.md").read_text(encoding="utf-8")
    bug_report = bug_report_template.replace("{{PROJECT_NAME}}", project_name)

    work_order_template = (templates_dir / "work_order.md").read_text(encoding="utf-8")
    work_order = work_order_template.replace("{{PROJECT_NAME}}", project_name)

    issue_config_template = (templates_dir / "issue_config.yml").read_text(encoding="utf-8")
    issue_config = issue_config_template

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
