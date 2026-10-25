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
      "args": ["-m", "mcp_server.main"],
      "env": {
        "SSL_CERT_FILE": "/absolute/path/to/your/venv/lib/python3.13/site-packages/certifi/cacert.pem"
      }
    }
  }
}
```

The `.mcp.json` is machine-specific and is intentionally ignored by Git. VS Code's Copilot Chat can read a workspace-root `.mcp.json`; in Agent mode, start `githubIssues`, enable `get_open_issues` in Configure Tools, and ask it to retrieve issues for `pallets/flask`.

The server uses MCP's stdio transport. Run by itself, it waits for a compatible client and does not print issue results to the terminal. The client launches it and exchanges MCP messages.

## Connect the MCP Server to VS Code

These steps use VS Code with GitHub Copilot Chat in Agent mode.

1. Clone the project and open its root folder in VS Code:

   ```bash
   git clone https://github.com/RameshKokati/github-api-vs-mcp.git
   cd github-api-vs-mcp
   ```

2. Create the virtual environment and install the project dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   If your Mac's `python3` is older than 3.10, use an installed newer interpreter, such as `python3.13`, in the `venv` command.

3. In the project root, create `.mcp.json`. Replace both example paths with absolute paths from your machine. Find the `certifi` bundle path by running `python -c "import certifi; print(certifi.where())"` inside the activated environment and use its output for `SSL_CERT_FILE`:

   ```json
   {
     "mcpServers": {
       "githubIssues": {
         "command": "/absolute/path/to/github-api-vs-mcp/.venv/bin/python",
         "args": ["-m", "mcp_server.main"],
         "env": {
           "SSL_CERT_FILE": "/absolute/path/to/.venv/lib/python3.13/site-packages/certifi/cacert.pem"
         }
       }
     }
   }
   ```

   `SSL_CERT_FILE` points Python at trusted CA certificates and avoids the macOS `CERTIFICATE_VERIFY_FAILED` error seen in some installations. The `.mcp.json` file is machine-specific and is ignored by Git; do not commit it. If you do not need the certificate override, you can remove the `env` block.

4. Open the project root folder in VS Code. In the MCP Servers list, start or restart `githubIssues`. In Copilot Chat, select **Agent** mode, open **Configure Tools**, and enable `get_open_issues` under `githubIssues`.

5. Try this prompt in Copilot Chat:

   > Use the `get_open_issues` tool from `githubIssues` with owner `pallets`, repo `flask`, and limit `5`. Return the issue titles and links.

Confirm that the tool call is labeled `get_open_issues` from `githubIssues`. Another installed GitHub MCP server may have a similarly named issue-listing tool. This server uses stdio, so launching `python -m mcp_server.main` manually in a terminal waits for an MCP client instead of printing the issue results.

## Troubleshooting

### SSL certificate verification fails on macOS

If Python reports `CERTIFICATE_VERIFY_FAILED` when contacting GitHub, first confirm that `certifi` is installed in this project's virtual environment, then print its CA bundle path:

```bash
python -m pip install certifi
python -c "import certifi; print(certifi.where())"
```

Use the printed path for `SSL_CERT_FILE`. For a one-time direct script run:

```bash
SSL_CERT_FILE="$(python -c 'import certifi; print(certifi.where())')" \
python -m direct_api.main pallets flask
```

For the web API, start Uvicorn with the same environment variable:

```bash
SSL_CERT_FILE="$(python -c 'import certifi; print(certifi.where())')" \
python -m uvicorn web_api.main:app --reload
```

For MCP, put the path printed by the Python command into the `.mcp.json` `env.SSL_CERT_FILE` field, save the file, and restart the `githubIssues` server in your MCP client. Paths inside `.mcp.json` are literal strings; shell expressions such as `$(...)` are not evaluated there.

### MCP server appears, but the expected tool is not called

Confirm the `githubIssues` server is running and enable its `get_open_issues` tool in the client's tool configuration. Ask for the tool by name and provide `owner`, `repo`, and `limit`. A different server may expose a similarly named issue-listing tool; check the tool-call label to confirm the call came from `githubIssues`.

### MCP server prints nothing in the terminal

This server uses stdio and is meant to be launched by an MCP client. Starting `python -m mcp_server.main` manually normally waits for the client instead of printing issue results. Make the request through the client's `get_open_issues` tool.

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
