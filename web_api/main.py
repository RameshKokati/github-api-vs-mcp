"""A small HTTP API that returns issues from a public GitHub repository.

Run it from the project root with `python -m uvicorn web_api.main:app --reload`.
"""

from fastapi import FastAPI, HTTPException, Query
from urllib.error import HTTPError, URLError

from shared.github_issues import fetch_open_issues


# FastAPI uses this object to register routes and generate /docs automatically.
app = FastAPI(
    title="GitHub Issues Learning API",
    description="A small API that returns open issues from a public GitHub repository.",
    version="1.0.0",
)


@app.get("/issues")
def get_issues(
    # These are URL query parameters. Defaults let a user call /issues alone;
    # the constraints reject empty names and unreasonable result limits.
    owner: str = Query("python", min_length=1, max_length=100),
    repo: str = Query("cpython", min_length=1, max_length=100),
    limit: int = Query(5, ge=1, le=100),
):
    """Return JSON with issues for the requested repository.

    Example: /issues?owner=pallets&repo=flask&limit=5
    """
    try:
        # Reuse the same function as direct_api/main.py; our endpoint does not
        # implement a second version of the GitHub request.
        issues = fetch_open_issues(owner, repo, limit)
    except HTTPError as error:
        # Translate GitHub's error into an HTTP error from our own API.
        if error.code == 404:
            raise HTTPException(status_code=404, detail="GitHub repository not found")
        raise HTTPException(status_code=502, detail="GitHub returned HTTP {}".format(error.code))
    except (URLError, TimeoutError) as error:
        raise HTTPException(status_code=502, detail="Could not reach GitHub: {}".format(error))

    # FastAPI converts this Python dictionary into a JSON HTTP response.
    return {"repository": "{}/{}".format(owner, repo), "count": len(issues), "issues": issues}
