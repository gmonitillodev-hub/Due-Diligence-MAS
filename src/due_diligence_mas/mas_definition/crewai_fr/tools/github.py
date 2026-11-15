import os
import re

import requests
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

API = "https://api.github.com"
TIMEOUT = 15

def _get(path: str, params: dict | None = None) -> requests.Response:
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(f"{API}{path}", headers=headers, params=params, timeout=TIMEOUT)


def _contributors(full_name: str) -> int | None:
    # per_page=1 so the page number in the Link header equals the total
    resp = _get(f"/repos/{full_name}/contributors", {"per_page": 1, "anon": "true"})
    if resp.status_code != 200:
        return None
    last = resp.links.get("last", {}).get("url", "")
    match = re.search(r"[?&]page=(\d+)", last)
    return int(match.group(1)) if match else len(resp.json())


@tool("GitHub repositories")
def github_repos(owner: str, max_repos: int = 5) -> str:
    """List the top public repositories (by stars) of a GitHub organization or user with
    name, URL, description, stars, forks, license, languages, last push and contributors count.
    `owner` is the organization or user name (e.g. 'openai'); `max_repos` is capped at 10."""
    max_repos = max(1, min(max_repos, 10))
    try:
        resp = _get(f"/users/{owner}/repos", {"per_page": 100, "sort": "pushed"})
        if resp.status_code != 200:
            return f"GitHub data unavailable for '{owner}' (HTTP {resp.status_code})."

        repos = [r for r in resp.json() if not r["fork"] and not r["archived"]]
        repos.sort(key=lambda r: r["stargazers_count"], reverse=True)

        lines = []
        for r in repos[:max_repos]:
            langs = _get(f"/repos/{r['full_name']}/languages").json()
            lines.append(
                f"- {r['name']} ({r['html_url']}): {r.get('description') or 'n/a'} | "
                f"stars={r['stargazers_count']} forks={r['forks_count']} "
                f"license={(r.get('license') or {}).get('spdx_id')} "
                f"languages={list(langs)} last_push={r['pushed_at']} "
                f"contributors={_contributors(r['full_name'])}"
            )
        return "\n".join(lines) or f"No public repositories found for '{owner}'."
    except requests.RequestException as e:
        return f"GitHub request failed: {e}"
