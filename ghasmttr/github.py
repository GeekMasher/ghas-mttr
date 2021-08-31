import os
import json
import requests
from string import Template


class GitHub:
    def __init__(
        self,
        owner: str,
        name: str = None,
        instance: str = "https://github.com",
        token: str = None,
        cache_path: str = ".mttr",
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

        self.cache_path = cache_path
        os.makedirs(self.cache_path, exist_ok=True)

    @property
    def repository(self):
        return f"{self.owner}/{self.name}"

    def cache(self, name: str, file_type: str = "json"):
        path = os.path.join(self.cache_path, name + "." + file_type)
        if os.path.exists(path) and file_type == "json":
            print(f"Reading from cache file: {path}")

            with open(path, "r") as handle:
                return json.load(handle)

    def cacheSave(self, name: str, data, file_type: str = "json"):
        path = os.path.join(self.cache_path, name + "." + file_type)
        if file_type == "json":
            with open(path, "w") as handle:
                json.dump(data, handle, indent=2)

    def getRepositories(self):
        url = f"{self.instance_api}/orgs/{self.owner}/repos"
        return self.getRequest(url)

    def getSecurityIssues(self, repository: str, ref: str = None):
        cache_key = f"{self.owner}_{repository}"
        cache = self.cache(cache_key)
        if cache:
            return cache

        url = (
            f"{self.instance_api}/repos/{self.owner}/{repository}/code-scanning/alerts"
        )
        print(f"Getting Security Results for :: {self.owner}/{repository}")
        data = self.getRequest(url)
        self.cacheSave(cache_key, data)
        return data

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
