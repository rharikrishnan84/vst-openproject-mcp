# OpenProject MCP Server

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/rharikrishnan84/vst-openproject-mcp/releases/tag/v0.1.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for the [OpenProject](https://www.openproject.org) REST API.

Connect your AI assistant — **Claude**, **Cursor**, or any MCP-compatible client — directly to your OpenProject instance. Manage projects, tasks, users, and versions through natural language without leaving your AI tool.

---

## Quick Install

### Claude Desktop / Claude Code — One-Click (recommended)

Download and double-click the bundle for your platform:

| File | Format | Compatible with |
|---|---|---|
| [openproject-mcp-0.1.0.mcpb](https://github.com/rharikrishnan84/vst-openproject-mcp/releases/download/v0.1.0/openproject-mcp-0.1.0.mcpb) | MCPB (current) | Claude Desktop, Claude Code, MCP for Windows |
| [openproject-mcp-0.1.0.dxt](https://github.com/rharikrishnan84/vst-openproject-mcp/releases/download/v0.1.0/openproject-mcp-0.1.0.dxt) | DXT (legacy) | Claude Desktop (older versions) |

Claude will prompt you for your **OpenProject URL** and **API token** on first launch.

> **Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) to be installed.** `uv` manages Python and all dependencies automatically — no separate pip install needed.

---

### Installer Script (Windows / Linux / macOS)

**Windows:**
```bat
curl -LO https://github.com/rharikrishnan84/vst-openproject-mcp/releases/download/v0.1.0/install.bat && install.bat
```

**Linux / macOS:**
```bash
curl -fsSL https://github.com/rharikrishnan84/vst-openproject-mcp/releases/download/v0.1.0/install.sh | bash
```

The installer will:
- Check Python 3.11+
- Install the package
- Prompt for your OpenProject URL and API token
- Test the connection live
- Auto-detect and configure Claude Desktop, Cursor, and Claude Code CLI

> **Prefer full control?** See [Manual Installation](#manual-installation) below.

---

## Table of Contents

- [Features](#features)
- [Quick Install](#quick-install)
- [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Client Setup](#client-setup)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## Features

- **29 tools** covering the full OpenProject workflow
- **Projects** — list, get, create, update, delete (with confirmation)
- **Work Packages** — list/filter, get, create, update, delete (with confirmation), comments, relations
- **Users** — list, get, current user, project members
- **Statuses / Types / Priorities** — reference data lookup
- **Versions** — list, get, create, update
- **Delete protection** — all destructive actions require explicit user confirmation
- **Cross-platform** — Windows, Linux, macOS
- **Configurable** via environment variables — no hardcoded credentials

---

## Manual Installation

### Option 1 — pip from GitHub (recommended)

```bash
pip install git+https://github.com/rharikrishnan84/vst-openproject-mcp.git
```

### Option 2 — pip from wheel

Download the wheel from [Releases](https://github.com/rharikrishnan84/vst-openproject-mcp/releases/tag/v0.1.0):

```bash
pip install openproject_mcp-0.1.0-py3-none-any.whl
```

### Option 3 — from source

```bash
git clone https://github.com/rharikrishnan84/vst-openproject-mcp.git
cd vst-openproject-mcp
pip install -e .
```

---

## Configuration

### Getting your API token

1. Log in to your OpenProject instance
2. Click your avatar → **My Account**
3. Go to **Access Tokens** in the left sidebar
4. Click **+ API access token** and copy the token

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENPROJECT_URL` | **Yes** | — | Base URL (e.g. `https://projects.example.com`) |
| `OPENPROJECT_API_TOKEN` | **Yes** | — | Your personal API access token |
| `OPENPROJECT_TIMEOUT` | No | `30` | HTTP request timeout in seconds |
| `OPENPROJECT_VERIFY_SSL` | No | `true` | Set `false` for self-signed certificates |

### Local `.env` file (development only)

```bash
cp .env.example .env
# Edit .env and fill in your values
```

Do **not** commit `.env` — it is gitignored.

---

## Client Setup

### Claude Desktop

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

Restart Claude Desktop after saving.

### Cursor IDE

**Global** — `~/.cursor/mcp.json`:

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

**Per workspace** — create `.cursor/mcp.json` in your project root.
Enable MCP in Cursor: **Settings → Features → MCP → Enable**.

### Claude Code CLI

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

Add to `~/.claude/settings.json` (global) or `.claude/settings.json` (per project).

> **`openproject-mcp` not on PATH?** Use `python -m openproject_mcp` as the command instead.

---

## Available Tools

### Projects (5 tools)

| Tool | Description |
|---|---|
| `list_projects` | List all accessible projects (paginated) |
| `get_project` | Get project details by ID or identifier |
| `create_project` | Create with name, identifier, description, visibility |
| `update_project` | Update name, description, public flag, or status |
| `delete_project` | Delete permanently — **requires user confirmation** |

### Work Packages (9 tools)

| Tool | Description |
|---|---|
| `list_work_packages` | List with filters: project, status, assignee, type, priority, subject |
| `get_work_package` | Get full details of a single work package |
| `create_work_package` | Create with type, status, priority, assignee, dates, hours |
| `update_work_package` | Update any field (requires `lockVersion`) |
| `delete_work_package` | Delete permanently — **requires user confirmation** |
| `list_work_package_activities` | Get comments and change history |
| `add_work_package_comment` | Post a comment |
| `list_work_package_relations` | List relations (blocks, follows, etc.) |
| `create_work_package_relation` | Create a relation between two work packages |

### Users (4 tools)

| Tool | Description |
|---|---|
| `get_current_user` | Get the authenticated user's profile |
| `list_users` | List all users (requires admin) |
| `get_user` | Get a specific user by ID |
| `list_project_members` | List members of a project with their roles |

### Statuses (2 tools)

| Tool | Description |
|---|---|
| `list_statuses` | List all statuses (New, In Progress, Closed, etc.) |
| `get_status` | Get a status by ID |

### Types (3 tools)

| Tool | Description |
|---|---|
| `list_types` | List all types globally (Bug, Task, Feature, etc.) |
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
| `create_version` | Create with dates, status, sharing scope |
| `update_version` | Update name, dates, or status |

---

## Delete Confirmation

All destructive delete operations use a two-step confirmation flow to prevent accidental data loss.

**Step 1** — AI calls the delete tool without `confirm`:
```
[!] CONFIRMATION REQUIRED

You are about to permanently delete:
  #8644  Fix login page
  Type    : Bug
  Status  : In Progress
  Project : Shipcrm Intelligence Enhancer
  Assignee: Harikrishnan

This action CANNOT be undone.

Are you sure you want to delete work package #8644 'Fix login page'?
```

**Step 2** — User says "yes" → AI calls again with `confirm=True` → deletion executes.

---

## Usage Examples

```
"List all my open projects"
"Show me all high-priority bugs in the Shipcrm project"
"Create a task called 'Fix login page' assigned to Harikrishnan, due 2025-04-15"
"What work packages are assigned to me and In Progress?"
"Add a comment to #123 saying the fix is deployed to staging"
"Mark work package #456 as Testing Completed"
"Create a Sprint 14 version in the EHR project, due 2025-04-30"
"Delete work package #789"  ← will ask for confirmation first
```

---

## Project Structure

```
vst-openproject-mcp/
├── install.bat                         # One-click installer for Windows
├── install.sh                          # One-click installer for Linux/macOS
├── pyproject.toml                      # Package metadata + entry point
├── .env.example                        # Configuration template
└── src/openproject_mcp/
    ├── server.py                       # MCP server entry point (FastMCP)
    ├── config.py                       # Pydantic Settings — OPENPROJECT_* env vars
    ├── client.py                       # Async httpx client — auth + error handling
    └── tools/
        ├── projects.py                 # 5 tools
        ├── work_packages.py            # 9 tools
        ├── users.py                    # 4 tools
        ├── statuses.py                 # 2 tools
        ├── types.py                    # 3 tools
        ├── priorities.py               # 2 tools
        └── versions.py                 # 4 tools
```

---

## Development

```bash
git clone https://github.com/rharikrishnan84/vst-openproject-mcp.git
cd vst-openproject-mcp
pip install -e .
cp .env.example .env   # fill in your credentials
```

**Test connectivity:**

```bash
python -c "
import asyncio
from openproject_mcp.config import get_settings
from openproject_mcp.client import OpenProjectClient

async def check():
    c = OpenProjectClient(get_settings())
    me = await c.get('/api/v3/users/me')
    print(f'Connected as: {me[\"name\"]} ({me[\"email\"]})')
    await c.aclose()

asyncio.run(check())
"
```

**Build wheel for distribution:**

```bash
pip install build
python -m build
# Output: dist/openproject_mcp-0.1.0-py3-none-any.whl
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `OPENPROJECT_URL` / `OPENPROJECT_API_TOKEN` required | Set env vars in your MCP client config `env` block |
| `openproject-mcp: command not found` | Use `python -m openproject_mcp` as the command |
| SSL certificate error | Add `"OPENPROJECT_VERIFY_SSL": "false"` to env |
| `409 Conflict` on update | Fetch the work package first to get current `lockVersion` |
| `403 Forbidden` on `list_users` | Requires administrator privileges |
| MCP not appearing in client | Restart the app after editing config; validate JSON syntax |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Built for [Voyage Software Technologies](https://voyagesoftwaretech.com)*
