# OpenProject MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for the [OpenProject](https://www.openproject.org) REST API.

Connect your AI assistant (Claude, Cursor, or any MCP-compatible client) directly to your OpenProject instance. Ask natural language questions and perform actions — list projects, create tasks, update statuses, assign work, add comments — without leaving your AI tool.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Install from wheel (recommended)](#install-from-wheel-recommended)
  - [Install from source](#install-from-source)
  - [Build the wheel yourself](#build-the-wheel-yourself)
- [Configuration](#configuration)
  - [Getting your API token](#getting-your-api-token)
  - [Environment variables](#environment-variables)
- [Client Setup](#client-setup)
  - [Claude Desktop](#claude-desktop-setup)
  - [Cursor IDE](#cursor-ide-setup)
  - [Claude Code CLI](#claude-code-cli-setup)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **29 tools** covering the full OpenProject workflow
- **Projects** — list, get, create, update, delete
- **Work Packages** — list with filters, get, create, update, delete, comments, relations
- **Users** — list, get, current user, project members
- **Statuses / Types / Priorities** — reference data lookup
- **Versions** — list, get, create, update (milestones / sprints)
- Fully **async** — non-blocking HTTP via `httpx`
- **Cross-platform** — Windows, Linux, macOS
- **Configurable** via environment variables — no hardcoded credentials

---

## Prerequisites

| Requirement | Minimum version | Notes |
|---|---|---|
| Python | 3.11 | `python --version` to check |
| pip | any | bundled with Python |
| OpenProject | any hosted/self-hosted | Needs API access token |

---

## Installation

### Install from wheel (recommended)

Download the latest `.whl` from [Releases](../../releases) and install:

```bash
pip install openproject_mcp-0.1.0-py3-none-any.whl
```

### Install from source

```bash
git clone https://github.com/rharikrishnan84/vst-openproject-mcp.git
cd vst-openproject-mcp
pip install -e .
```

### Build the wheel yourself

```bash
git clone https://github.com/rharikrishnan84/vst-openproject-mcp.git
cd vst-openproject-mcp
pip install build
python -m build
# Output: dist/openproject_mcp-0.1.0-py3-none-any.whl
```

Share the `.whl` file with colleagues — they install it with a single `pip install` command.

---

## Configuration

### Getting your API token

1. Log in to your OpenProject instance
2. Click your avatar (top-right) → **My Account**
3. Go to **Access Tokens** in the left sidebar
4. Click **+ API access token**
5. Copy the generated token (shown only once)

### Environment variables

All configuration is via environment variables with the `OPENPROJECT_` prefix:

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENPROJECT_URL` | **Yes** | — | Base URL of your OpenProject instance (e.g. `https://projects.example.com`) |
| `OPENPROJECT_API_TOKEN` | **Yes** | — | Your personal API access token |
| `OPENPROJECT_TIMEOUT` | No | `30` | HTTP request timeout in seconds |
| `OPENPROJECT_VERIFY_SSL` | No | `true` | Set `false` for self-signed TLS certificates |

#### Local development (`.env` file)

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```ini
OPENPROJECT_URL=https://your-openproject.example.com
OPENPROJECT_API_TOKEN=your-api-token-here
```

The server loads `.env` automatically when running locally. Do **not** commit `.env` — it is gitignored.

> **Security note:** Never put credentials in MCP config files that are committed to source control. Always use the `env` block in the client config (see below) or a `.env` file that is gitignored.

---

## Client Setup

### Claude Desktop Setup

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux/macOS:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openproject": {
      "command": "openproject-mcp",
      "env": {
        "OPENPROJECT_URL": "https://your-openproject.example.com",
        "OPENPROJECT_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

> If `openproject-mcp` is not on PATH, use `python -m openproject_mcp` instead:
>
> ```json
> {
>   "mcpServers": {
>     "openproject": {
>       "command": "python",
>       "args": ["-m", "openproject_mcp"],
>       "env": {
>         "OPENPROJECT_URL": "https://your-openproject.example.com",
>         "OPENPROJECT_API_TOKEN": "your-api-token-here"
>       }
>     }
>   }
> }
> ```

Restart Claude Desktop after saving the config.

---

### Cursor IDE Setup

**Global** (applies to all workspaces) — `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "openproject": {
      "command": "openproject-mcp",
      "env": {
        "OPENPROJECT_URL": "https://your-openproject.example.com",
        "OPENPROJECT_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Per workspace** — create `.cursor/mcp.json` in your project root with the same content. Useful when different projects use different OpenProject instances.

Enable MCP in Cursor: **Settings → Features → MCP → Enable MCP**.

---

### Claude Code CLI Setup

Add to your global Claude Code settings (`~/.claude/settings.json` or via `claude config`):

```json
{
  "mcpServers": {
    "openproject": {
      "command": "openproject-mcp",
      "env": {
        "OPENPROJECT_URL": "https://your-openproject.example.com",
        "OPENPROJECT_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

Or add it to a project-level `.claude/settings.json` for per-project configuration.

---

## Available Tools

### Projects (5 tools)

| Tool | Description |
|---|---|
| `list_projects` | List all accessible projects (paginated) |
| `get_project` | Get project details by numeric ID or string identifier |
| `create_project` | Create a new project with name, identifier, description, visibility |
| `update_project` | Update name, description, public flag, or status |
| `delete_project` | Permanently delete a project |

### Work Packages (9 tools)

| Tool | Description |
|---|---|
| `list_work_packages` | List work packages with optional filters: project, status, assignee, type, priority, subject text |
| `get_work_package` | Get full details of a single work package |
| `create_work_package` | Create with type, status, priority, assignee, dates, estimated hours |
| `update_work_package` | Update any field (requires `lockVersion` for conflict detection) |
| `delete_work_package` | Permanently delete a work package |
| `list_work_package_activities` | Get comments and change history |
| `add_work_package_comment` | Post a comment |
| `list_work_package_relations` | List relations (blocks, follows, relates to, etc.) |
| `create_work_package_relation` | Create a relation between two work packages |

### Users (4 tools)

| Tool | Description |
|---|---|
| `get_current_user` | Get the authenticated user's profile |
| `list_users` | List all users (requires admin privileges) |
| `get_user` | Get a specific user by ID |
| `list_project_members` | List members of a project with their roles |

### Statuses (2 tools)

| Tool | Description |
|---|---|
| `list_statuses` | List all work package statuses (New, In Progress, Closed, etc.) |
| `get_status` | Get a status by ID |

### Types (3 tools)

| Tool | Description |
|---|---|
| `list_types` | List all work package types globally (Bug, Task, Feature, etc.) |
| `list_project_types` | List types enabled for a specific project |
| `get_type` | Get a type by ID |

### Priorities (2 tools)

| Tool | Description |
|---|---|
| `list_priorities` | List all priorities (Low, Normal, High, Immediate) |
| `get_priority` | Get a priority by ID |

### Versions (4 tools)

| Tool | Description |
|---|---|
| `list_versions` | List versions/sprints/milestones in a project |
| `get_version` | Get a version by ID |
| `create_version` | Create a version with dates, status, sharing scope |
| `update_version` | Update version name, dates, or status |

---

## Usage Examples

Once configured, you can talk to your OpenProject instance naturally through your AI client:

```
"List all my open projects"
"Show me all high-priority bugs in the Reports project"
"Create a task called 'Fix login page' in the Shipcrm project, assign it to Harikrishnan"
"What work packages are assigned to me and still In Progress?"
"Add a comment to work package #123 saying the fix is deployed"
"Close work package #456 — mark it as Testing Completed"
"Create a version called Sprint 14 in the EHR project, due 2025-04-30"
"Who are the members of the Shipcrm Intelligence Enhancer project?"
```

---

## Project Structure

```
vst-openproject-mcp/
├── pyproject.toml                      # Package metadata, dependencies, entry point
├── .env.example                        # Template for environment variables
├── .gitignore
└── src/
    └── openproject_mcp/
        ├── __init__.py                 # Package version
        ├── __main__.py                 # Enables python -m openproject_mcp
        ├── server.py                   # MCP server entry point (FastMCP + Windows asyncio fix)
        ├── config.py                   # Pydantic Settings — env var loading with OPENPROJECT_ prefix
        ├── client.py                   # Async httpx client — auth, error handling
        └── tools/
            ├── __init__.py             # register_all() wires all tool modules into FastMCP
            ├── projects.py             # 5 project tools
            ├── work_packages.py        # 9 work package tools
            ├── users.py                # 4 user tools
            ├── statuses.py             # 2 status tools
            ├── types.py                # 3 type tools
            ├── priorities.py           # 2 priority tools
            └── versions.py             # 4 version tools
```

---

## Development

### Setup

```bash
git clone https://github.com/rharikrishnan84/vst-openproject-mcp.git
cd vst-openproject-mcp
pip install -e .
cp .env.example .env
# Edit .env with your credentials
```

### Running locally

```bash
# The server communicates over stdio (MCP protocol)
# To test it's working, run a quick import check:
python -c "from openproject_mcp.server import main; print('OK')"

# Or test live API connectivity:
python -c "
import asyncio
from openproject_mcp.config import get_settings
from openproject_mcp.client import OpenProjectClient

async def check():
    c = OpenProjectClient(get_settings())
    me = await c.get('/api/v3/users/me')
    print(f'Connected as: {me[\"name\"]}')
    await c.aclose()

asyncio.run(check())
"
```

### Building for distribution

```bash
pip install build
python -m build
# Produces dist/openproject_mcp-0.1.0-py3-none-any.whl
```

### Adding a new tool

1. Find the right module in `src/openproject_mcp/tools/` (or create a new one)
2. Add an async function decorated with `@mcp.tool()` inside the `register()` function
3. Include a full docstring — it becomes the tool description the AI sees
4. If creating a new module, import and call `register()` in `tools/__init__.py`

Example:

```python
@mcp.tool()
async def my_new_tool(project_id: str, some_param: str | None = None) -> dict:
    """Short one-line description shown to the AI.

    Longer explanation if needed.

    Args:
        project_id: The project to operate on.
        some_param: Optional parameter description.
    """
    return await client.get(f"/api/v3/projects/{project_id}/something")
```

---

## Troubleshooting

### `ValidationError: OPENPROJECT_URL` or `OPENPROJECT_API_TOKEN` field required

The server could not find the required environment variables. Make sure they are set in the `env` block of your MCP client config (not just in a `.env` file, which is only loaded for local runs).

### `openproject-mcp: command not found`

The script was not added to PATH. Use the full path or switch to `python -m openproject_mcp`:

```json
"command": "python",
"args": ["-m", "openproject_mcp"]
```

On Windows with a virtual environment, the script is typically at:
`C:\Users\<user>\AppData\Local\Programs\Python\Python311\Scripts\openproject-mcp.exe`

### `SSL certificate verify failed`

Your OpenProject instance uses a self-signed or internal CA certificate. Add to the `env` block:

```json
"OPENPROJECT_VERIFY_SSL": "false"
```

### `409 Conflict` when updating a work package

OpenProject uses optimistic locking. You must fetch the work package first with `get_work_package` and pass its `lockVersion` to `update_work_package`. Another user may have updated it between your read and write.

### `403 Forbidden` on `list_users`

Listing all users requires **administrator** privileges. The current API token's user does not have admin rights.

### MCP server not appearing in Claude / Cursor

- Restart the client application after editing the config file
- Validate the JSON config (no trailing commas, correct nesting)
- Check that `openproject-mcp` is reachable: run `openproject-mcp --help` in a terminal (it will error but confirms the command exists)

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-tool`
3. Make your changes and test against a real OpenProject instance
4. Open a pull request with a description of what was added/changed

---

## License

MIT — see [LICENSE](LICENSE) for details.
