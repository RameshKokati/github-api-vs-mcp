"""Shared GitHub issue lookup used by the script, web API, and later MCP tool.

Keeping this function in one module lets each demo use the same GitHub request.
"""

import json
from urllib.request import Request, urlopen


def fetch_open_issues(owner, repo, limit=5):
    """Call GitHub's REST API and return open issues (excluding pull requests).

    Args:
        owner: GitHub account or organization, such as "pallets".
        repo: Repository name, such as "flask".
        limit: Maximum number of results to ask GitHub for (1-100).
    """
    # GitHub's REST API provides issue data at this URL. Query parameters
    # restrict the results to open items and ask for at most `limit` entries.
    url = "https://api.github.com/repos/{}/{}/issues?state=open&per_page={}".format(
        owner, repo, limit
    )

    # GitHub expects a User-Agent header, and Accept selects its JSON response.
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-api-vs-mcp-learning-demo",
        },
    )

    # Send the HTTP GET request. The context manager closes the connection
    # automatically, and timeout prevents the program waiting forever.
    with urlopen(request, timeout=15) as response:
        # The response body is bytes; decode it to text, then parse JSON into
        # Python dictionaries and lists.
        results = json.loads(response.read().decode("utf-8"))

    # GitHub's issues endpoint also includes pull requests.
    # Keep only actual issues so all demos return the same kind of result.
    return [issue for issue in results if "pull_request" not in issue]
