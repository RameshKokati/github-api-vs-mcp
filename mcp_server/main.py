"""MCP server exposing GitHub issue lookup as an AI-callable tool.

Run from the project root with `python -m mcp_server.main`.
"""

from mcp.server.fastmcp import FastMCP
from urllib.error import HTTPError, URLError

from shared.github_issues import fetch_open_issues


# FastMCP handles the MCP protocol and makes registered functions available
# to a connected MCP client as tools.
server = FastMCP("GitHub Issues")


@server.tool()
def get_open_issues(owner: str, repo: str, limit: int = 5) -> dict:
    """Get open issues from a public GitHub repository.

    Args:
        owner: GitHub account or organization, such as "pallets".
        repo: Repository name, such as "flask".
        limit: Maximum number of issues to return (1-100).
    """
    if not owner or not repo:
        raise ValueError("Both owner and repo must be non-empty.")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100.")

    try:
        # This is the same GitHub request used by the direct script and web API.
        issues = fetch_open_issues(owner, repo, limit)
    except HTTPError as error:
        if error.code == 404:
            return {"error": "GitHub repository not found", "repository": "{}/{}".format(owner, repo)}
        return {"error": "GitHub returned HTTP {}".format(error.code)}
    except (URLError, TimeoutError) as error:
        return {"error": "Could not reach GitHub: {}".format(error)}

    # The MCP client receives structured data as the tool result.
    return {
        "repository": "{}/{}".format(owner, repo),
        "count": len(issues),
        "issues": [
            {"number": issue["number"], "title": issue["title"], "url": issue["html_url"]}
            for issue in issues
        ],
    }


if __name__ == "__main__":
    # The default transport is stdio, used by local MCP host applications.
    server.run()
