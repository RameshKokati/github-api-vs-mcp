"""Command-line demo that calls the shared GitHub issue lookup directly."""

import sys
from urllib.error import HTTPError, URLError
from shared.github_issues import fetch_open_issues


def main():
    # Read owner and repository from command-line arguments, or use a default.
    # Example: python direct_api.py pallets flask
    owner = sys.argv[1] if len(sys.argv) > 1 else "python"
    repo = sys.argv[2] if len(sys.argv) > 2 else "cpython"

    try:
        # This is the same lookup used by the web API and future MCP tool.
        issues = fetch_open_issues(owner, repo)
    except HTTPError as error:
        print("GitHub returned HTTP {}: {}".format(error.code, error.reason))
        return 1
    except URLError as error:
        print("Could not reach GitHub: {}".format(error.reason))
        return 1
    except TimeoutError:
        print("The request to GitHub timed out.")
        return 1

    # Print a compact, readable version instead of dumping all returned JSON.
    print("Open issues in {}/{} (up to 5):\n".format(owner, repo))
    for issue in issues:
        print("#{} {}".format(issue["number"], issue["title"]))
        print("  {}\n".format(issue["html_url"]))

    return 0


if __name__ == "__main__":
    # Only run main() when this file is executed as a script, not imported.
    sys.exit(main())
