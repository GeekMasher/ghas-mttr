import requests
from string import Template


class GitHub:
    def __init__(
        self,
        owner: str,
        name: str = None,
        instance: str = "https://github.com",
        token: str = None,
    ):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token " + token,
        }
        self.instance = instance

        if instance == "https://github.com":
            self.instance_api = "https://api.github.com"
        else:
            raise Exception("Server URL not supported right now")

        self.token = token

        self.owner = owner
        self.name = name

    @property
    def repository(self):
        return f"{self.owner}/{self.name}"

    def getRepositories(self):
        url = f"{self.instance_api}/orgs/{self.owner}/repos"
        return self.getRequest(url)

    def getSecurityIssues(self, repository: str, ref: str = None):
        url = (
            f"{self.instance_api}/repos/{self.owner}/{repository}/code-scanning/alerts"
        )
        print(f"Getting Security Results for :: {self.owner}/{repository}")
        return self.getRequest(url)

    def createSummaryIssue(
        self, repository: str, title: str, body: str, assignees: list[str] = []
    ):
        owner, repo = repository.split("/")

        url = f"{self.instance_api}/repos/{owner}/{repo}/issues"

        data = {"title": title, "body": body, "assignees": assignees}

        response = requests.post(url, headers=self.headers, json=data)

        return response.json()

    def getRequest(self, url: str, optional_params: dict = {}):
        results = []

        # print(f"Request URL :: {url}")

        page_counter = 1
        per_page = 100

        while True:
            response = requests.get(
                url,
                headers=self.headers,
                params={"page": page_counter, "per_page": per_page},
            )

            if response.status_code != 200:
                return None

            results.extend(response.json())

            if len(response.json()) < per_page:
                break
            page_counter += 1

        return results
