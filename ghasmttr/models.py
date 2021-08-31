from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class SecurityAlert:
    id: str
    state: str
    #  Security rule name
    rule: str
    tool: str
    # Dates and Times
    created: str
    dismissed: str = None

    @property
    def time_to_remediate(self):
        if self.dismissed is None:
            return None
        alert_creation_time = datetime.strptime(self.created, "%Y-%m-%dT%XZ")
        alert_dismissed_time = datetime.strptime(self.dismissed, "%Y-%m-%dT%XZ")

        return alert_dismissed_time - alert_creation_time


@dataclass
class RepositorySecurityAlerts:
    alerts: list[SecurityAlert] = field(default_factory=list)

    def getClosed(self):
        results: list[SecurityAlert] = []
        for alert in self.alerts:
            #  TODO: Can't add 'alert.state == "fixed"' as this doesn't return
            #   datetimes for tracking
            if alert.state == "dismissed":
                results.append(alert)
        return results

    def addAlert(self, **data):
        # https://docs.github.com/en/rest/reference/code-scanning#list-code-scanning-alerts-for-a-repository
        alert = SecurityAlert(
            id=data.get("number"),
            state=data.get("state"),
            rule=data.get("rule", {}).get("name"),
            tool=data.get("tool", {}).get("name"),
            created=data.get("created_at"),
            dismissed=data.get("dismissed_at"),
        )
        self.alerts.append(alert)

    def getTTR(self):
        deltatimes = [alert.time_to_remediate for alert in self.getClosed()]
        if len(deltatimes) == 0:
            return timedelta(0)
        return sum(deltatimes, timedelta(0)) / len(deltatimes)


@dataclass
class Repository:
    owner: str
    name: str

    total: int = 0
    open: int = 0
    closed: int = 0

    mttr: str = None

    @property
    def repository(self):
        return f"{self.owner}/{self.name}"
