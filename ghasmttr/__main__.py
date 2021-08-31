import os
import argparse
from dataclasses import dataclass

from ghasmttr.__version__ import *
from ghasmttr.github import GitHub
from ghasmttr.exporters import __EXPORTERS__
from ghasmttr.models import *

__HERE__ = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(__name__)

parser.add_argument("-c", "--config")
parser.add_argument("--owner", default=os.environ.get("GITHUB_REPOSITORY_OWNER"))
parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
parser.add_argument("-t", "--token", default=os.environ.get("GITHUB_TOKEN"))

parser.add_argument("--exporter", default="issues", help="Exporter name")
parser.add_argument("--exporter-list", action="store_true", help="Exporter list")

parser.add_argument(
    "--template-path",
    default=os.path.join(__HERE__, "templates"),
    help="Template folder",
)
parser.add_argument(
    "--instance",
    default=os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
)


if __name__ == "__main__":
    arguments = parser.parse_args()

    if arguments.exporter_list:
        for exporter, exporter_func in __EXPORTERS__.items():
            print(f" >> Exporter :: {exporter}")

        exit(0)

    github = GitHub(
        arguments.owner,
        name=arguments.repository,
        instance=arguments.instance,
        token=arguments.token,
    )

    print(f"GitHub Repository :: {github.repository}")

    # repositories = [{"name": "AutoBuilder"}]

    repositories = github.getRepositories()
    print(f"Total Repositories :: {len(repositories)}")

    repositories_results = []

    print("::group::Processing Repositories")

    for repo in repositories:
        repository_name = repo.get("name")
        print(f"Processing :: {repository_name}")

        repository = Repository(arguments.owner, repository_name)

        results = github.getSecurityIssues(repository_name)

        if results:
            security_alerts = RepositorySecurityAlerts()

            for result in results:
                security_alerts.addAlert(**result)

            repository.total = len(security_alerts.alerts)
            repository.closed = len(security_alerts.getClosed())
            repository.open = repository.total - repository.closed

            print(f"All Results :: {repository.total}")
            print(f"Closed      :: {repository.closed}")

            repository.mttr = security_alerts.getTTR()
            print(f"Time to Remediate :: {repository.mttr}")
        else:
            print("Skipping as not security issues...")

        repositories_results.append(repository)

    print("::endgroup::")

    for exporter, exporter_func in __EXPORTERS__.items():
        if exporter == arguments.exporter or arguments.exporter == "all":
            print(f" >> Exporter :: {exporter}")
            exporter_func(
                github=github,
                repositories=repositories_results,
                template_path=arguments.template_path,
            )
