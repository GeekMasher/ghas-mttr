### Description

This report is automatically generated to obtain the average time to remediate for an organization.

### Applications

| Name (owner/repo) | MTTR (all issues) | Total Issues | Total Remediated Issues (dismissed only) |
| :---------------- | :---------------: | :----------: | :--------------------------------------: |
{%- for repository in repositories %}
| [{{ repository.repository }}]({{ github.instance }}/{{ repository.repository }}/security/code-scanning) | {{ repository.mttr }} | {{ repository.total }} | {{ repository.closed }} |
{%- endfor %}
