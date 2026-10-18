# GitHub API vs MCP

A hands-on learning project comparing three ways to retrieve open issues from a public GitHub repository:

1. A Python command-line script calls GitHub's REST API directly.
2. A FastAPI web service exposes our own HTTP endpoint and calls GitHub.
3. An MCP server exposes the same lookup as a tool an AI client can discover and call.

All three demos reuse the same GitHub request function in `shared/github_issues.py`. The comparison focuses on how the operation is invoked and how its result is returned; MCP does not replace GitHub's API.

## Requirements

- Python 3.10 or newer (the project was developed with Python 3.13)
- An MCP-compatible client to try the MCP tool (the README's VS Code example uses Copilot Chat)
- Internet access to reach GitHub's public API

No GitHub token is needed for these public repositories. GitHub applies unauthenticated API rate limits.

## Setup

From the project root, create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On macOS, if `python3` points to an older system version, use the installed version explicitly, for example:

```bash
python3.13 -m venv .venv
```

## Demo 1: Direct GitHub API call

Run from the project root:

```bash
python -m direct_api.main [owner] [repo]
```

For example:

```bash
python -m direct_api.main pallets flask
```

If no arguments are provided, the script defaults to `python/cpython`. It prints up to five issue numbers, titles, and links.

## Demo 2: Our HTTP API

Start the local FastAPI service:

```bash
python -m uvicorn web_api.main:app --reload
```

Try the endpoint in a browser:

```text
http://127.0.0.1:8000/issues?owner=pallets&repo=flask&limit=5
```

FastAPI's interactive documentation is at `http://127.0.0.1:8000/docs`. Stop the server with **Ctrl+C**.

The local API accepts query parameters, calls GitHub through the shared function, and returns JSON.

## Demo 3: MCP tool

The MCP server in `mcp_server/main.py` exposes one tool, `get_open_issues(owner, repo, limit)`. It uses the same shared function as the other demos.

For local VS Code use, create a workspace-root `.mcp.json` with the following configuration. Replace the Python path with the path to this project's `.venv/bin/python`:

```json
{
  "mcpServers": {
    "githubIssues": {
      "command": "/absolute/path/to/github-api-vs-mcp/.venv/bin/python",
      "args": ["-m", "mcp_server.main"]
    }
  }
}
```

The `.mcp.json` is machine-specific and is intentionally ignored by Git. VS Code's Copilot Chat can read a workspace-root `.mcp.json`; in Agent mode, start `githubIssues`, enable `get_open_issues` in Configure Tools, and ask it to retrieve issues for `pallets/flask`.

The server uses MCP's stdio transport. Run by itself, it waits for a compatible client and does not print issue results to the terminal. The client launches it and exchanges MCP messages.

## Project layout

```text
direct_api/     Command-line demo
web_api/        FastAPI HTTP service
mcp_server/     MCP server and tool
shared/         GitHub API request reused by all demos
requirements.txt
```

## What the comparison demonstrates

| Demo | How inputs arrive | Interface used | Result delivered as |
|---|---|---|---|
| Direct script | Command-line arguments | Python process | Terminal text |
| Web API | HTTP query parameters | HTTP endpoint | JSON response |
| MCP | Tool arguments chosen by an MCP client | MCP protocol | Structured tool result |

This is a small educational example, not a performance benchmark. GitHub's REST API retrieves the data in every demo; the script, web API, and MCP server provide different ways to invoke the lookup.
