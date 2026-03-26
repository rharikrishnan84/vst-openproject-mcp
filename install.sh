#!/usr/bin/env bash
# =============================================================================
# OpenProject MCP Server — Installer for Linux / macOS
# Voyage Software Technologies
# =============================================================================
set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

banner()  { echo -e "\n${CYAN}${BOLD}$1${NC}"; }
step()    { echo -e "\n${BLUE}${BOLD}▶  $1${NC}"; }
ok()      { echo -e "   ${GREEN}✔${NC}  $1"; }
warn()    { echo -e "   ${YELLOW}⚠${NC}  $1"; }
err()     { echo -e "   ${RED}✖${NC}  $1"; }
info()    { echo -e "   ${CYAN}ℹ${NC}  $1"; }
divider() { echo -e "${CYAN}${BOLD}────────────────────────────────────────────────${NC}"; }

clear
divider
echo -e "${CYAN}${BOLD}   OpenProject MCP Server — Installer${NC}"
echo -e "${CYAN}   Voyage Software Technologies${NC}"
divider

# ── 1. Python check ───────────────────────────────────────────────────────────
step "Checking Python 3.11+"

PYTHON_CMD=""
for cmd in python3.11 python3.12 python3.13 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        MAJ=$(echo "$VER" | cut -d. -f1)
        MIN=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJ" -ge 3 ] && [ "$MIN" -ge 11 ]; then
            PYTHON_CMD="$cmd"
            ok "Python $VER found  →  $cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    err "Python 3.11+ not found."
    echo
    echo "  Install options:"
    echo "    Ubuntu/Debian : sudo apt install python3.11 python3-pip"
    echo "    Fedora/RHEL   : sudo dnf install python3.11"
    echo "    macOS (brew)  : brew install python@3.11"
    echo "    pyenv         : pyenv install 3.11"
    exit 1
fi

# ── 2. pip check ──────────────────────────────────────────────────────────────
if ! "$PYTHON_CMD" -m pip --version &>/dev/null; then
    err "pip not found for $PYTHON_CMD."
    echo "  Run: $PYTHON_CMD -m ensurepip --upgrade"
    exit 1
fi
ok "pip available"

# ── 3. Install package ────────────────────────────────────────────────────────
step "Installing openproject-mcp"

if "$PYTHON_CMD" -c "import openproject_mcp" &>/dev/null 2>&1; then
    CUR_VER=$("$PYTHON_CMD" -c "import openproject_mcp; print(openproject_mcp.__version__)" 2>/dev/null || echo "unknown")
    ok "Already installed  (v$CUR_VER)"
    echo -ne "   Upgrade to latest? [y/N]: "
    read -r UPGRADE
    if [[ "${UPGRADE,,}" == "y" ]]; then
        info "Upgrading..."
        "$PYTHON_CMD" -m pip install --upgrade \
            "git+https://github.com/rharikrishnan84/vst-openproject-mcp.git" \
            --quiet --no-warn-script-location
        ok "Upgraded"
    fi
else
    info "Installing from GitHub..."
    "$PYTHON_CMD" -m pip install \
        "git+https://github.com/rharikrishnan84/vst-openproject-mcp.git" \
        --quiet --no-warn-script-location
    ok "Installed successfully"
fi

# Determine runnable command
if command -v openproject-mcp &>/dev/null; then
    MCP_CMD="openproject-mcp"
    ok "Command available: openproject-mcp"
else
    MCP_CMD="$PYTHON_CMD -m openproject_mcp"
    warn "openproject-mcp not on PATH — will use: $MCP_CMD"
fi

# ── 4. Configuration prompts ──────────────────────────────────────────────────
step "Configuration"

DEFAULT_URL="https://projects.voyagesoftwaretech.com"
echo -ne "   OpenProject URL  [${DEFAULT_URL}]: "
read -r INPUT_URL
OPENPROJECT_URL="${INPUT_URL:-$DEFAULT_URL}"
# Strip trailing slash
OPENPROJECT_URL="${OPENPROJECT_URL%/}"
ok "URL: $OPENPROJECT_URL"

echo -ne "   API Token (hidden): "
read -rs OPENPROJECT_API_TOKEN
echo
if [ -z "$OPENPROJECT_API_TOKEN" ]; then
    err "API token cannot be empty."
    exit 1
fi
ok "Token received (${#OPENPROJECT_API_TOKEN} characters)"

# ── 5. Test connection ────────────────────────────────────────────────────────
step "Testing connection to OpenProject"

TEST_OUTPUT=$("$PYTHON_CMD" - <<PYEOF 2>&1
import asyncio, sys

async def main():
    try:
        import httpx
    except ImportError:
        print("ERR:httpx not installed")
        return

    url    = "$OPENPROJECT_URL"
    token  = "$OPENPROJECT_API_TOKEN"

    try:
        async with httpx.AsyncClient(
            auth=("apikey", token),
            timeout=15.0,
            verify=True,
            follow_redirects=True,
        ) as client:
            r = await client.get(f"{url}/api/v3/users/me")
            if r.status_code == 200:
                d = r.json()
                print(f"OK:{d.get('name','?')}:{d.get('email','')}")
            else:
                print(f"ERR:HTTP {r.status_code} — check URL and token")
    except httpx.ConnectError:
        print(f"ERR:Cannot reach {url} — check URL and network")
    except httpx.TimeoutException:
        print(f"ERR:Request timed out — server may be slow or unreachable")
    except Exception as e:
        print(f"ERR:{e}")

asyncio.run(main())
PYEOF
)

if [[ "$TEST_OUTPUT" == OK:* ]]; then
    IFS=':' read -r _ UNAME UEMAIL <<< "$TEST_OUTPUT"
    ok "Connected as: ${BOLD}${UNAME}${NC} (${UEMAIL})"
else
    ERR_MSG="${TEST_OUTPUT#ERR:}"
    err "Connection failed: ${ERR_MSG}"
    echo
    echo -ne "   Continue with configuration anyway? [y/N]: "
    read -r CONT
    [[ "${CONT,,}" == "y" ]] || { echo "Aborted."; exit 1; }
fi

# ── 6. Scan and configure MCP clients ─────────────────────────────────────────
step "Scanning for installed MCP clients"

CONFIGURED=0

# Helper: write/merge MCP server entry into a JSON config file
configure_client() {
    local LABEL="$1"
    local CONFIG_FILE="$2"

    echo
    info "${BOLD}${LABEL}${NC}"
    info "Config path: $CONFIG_FILE"

    RESULT=$("$PYTHON_CMD" - <<PYEOF 2>&1
import json, pathlib, sys

config_path = pathlib.Path("""$CONFIG_FILE""").expanduser()
config_path.parent.mkdir(parents=True, exist_ok=True)

if config_path.exists():
    try:
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        config = {}
else:
    config = {}

config.setdefault("mcpServers", {})

config["mcpServers"]["openproject"] = {
    "command": "$MCP_CMD",
    "env": {
        "OPENPROJECT_URL":        "$OPENPROJECT_URL",
        "OPENPROJECT_API_TOKEN":  "$OPENPROJECT_API_TOKEN"
    }
}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)

print("CONFIGURED")
PYEOF
)

    if [[ "$RESULT" == *"CONFIGURED"* ]]; then
        ok "Configured ${LABEL}"
        return 0
    else
        err "Failed to configure ${LABEL}: $RESULT"
        return 1
    fi
}

# ── Claude Desktop ────────────────────────────────────────────────────────────
CLAUDE_DESKTOP_CONFIG=""
if [ -d "$HOME/Library/Application Support/Claude" ]; then
    CLAUDE_DESKTOP_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [ -d "$HOME/.config/claude" ]; then
    CLAUDE_DESKTOP_CONFIG="$HOME/.config/claude/claude_desktop_config.json"
elif [ -f "$HOME/.config/Claude/claude_desktop_config.json" ]; then
    CLAUDE_DESKTOP_CONFIG="$HOME/.config/Claude/claude_desktop_config.json"
fi

if [ -n "$CLAUDE_DESKTOP_CONFIG" ]; then
    if configure_client "Claude Desktop" "$CLAUDE_DESKTOP_CONFIG"; then
        CONFIGURED=$((CONFIGURED + 1))
    fi
else
    warn "Claude Desktop not detected — skipping"
    info "Manual config: ~/.config/claude/claude_desktop_config.json"
fi

# ── Cursor IDE ────────────────────────────────────────────────────────────────
if [ -d "$HOME/.cursor" ]; then
    if configure_client "Cursor IDE" "$HOME/.cursor/mcp.json"; then
        CONFIGURED=$((CONFIGURED + 1))
    fi
else
    warn "Cursor IDE not detected — skipping"
    info "Manual config: ~/.cursor/mcp.json"
fi

# ── Claude Code CLI ───────────────────────────────────────────────────────────
if command -v claude &>/dev/null; then
    if configure_client "Claude Code CLI" "$HOME/.claude/settings.json"; then
        CONFIGURED=$((CONFIGURED + 1))
    fi
else
    warn "Claude Code CLI not detected — skipping"
    info "Manual config: ~/.claude/settings.json"
fi

# ── No clients found — print manual config ───────────────────────────────────
if [ "$CONFIGURED" -eq 0 ]; then
    echo
    warn "No MCP clients were auto-configured."
    echo
    info "Add this block manually to your client's MCP config file:"
    echo
    cat <<JSON
{
  "mcpServers": {
    "openproject": {
      "command": "$MCP_CMD",
      "env": {
        "OPENPROJECT_URL": "$OPENPROJECT_URL",
        "OPENPROJECT_API_TOKEN": "<your-token>"
      }
    }
  }
}
JSON
fi

# ── 7. Summary ────────────────────────────────────────────────────────────────
echo
divider
echo -e "${GREEN}${BOLD}   Installation complete!${NC}"
divider
echo
ok "openproject-mcp installed"
ok "MCP clients configured: ${BOLD}${CONFIGURED}${NC}"
echo
info "Restart Claude Desktop / Cursor to activate."
info "Then ask: \"List all my OpenProject projects\""
echo
