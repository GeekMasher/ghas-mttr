import os
from datetime import datetime

from jinja2 import Template

from ghasmttr.github import GitHub


def createSummaryIssue(github: GitHub = None, **kargvs):

    options = {
        "github": {"instance": github.instance},
        "repositories": kargvs.get("repositories"),
        "today": datetime.now().strftime("%Y-%m-%d"),
    }

    template_path = os.path.join(kargvs.get("template_path"), "issue.md")

    if not os.path.exists(template_path):
        raise Exception(f"Template does not exists: {template_path}")

    with open(template_path, "r") as handle:
        template = Template(handle.read())

    content = template.render(**options)

    title = "GHAS - Mean Time to Remediate Summary Report"

    github.createSummaryIssue(github.repository, title, content)
