@echo off
setlocal enabledelayedexpansion
:: =============================================================================
:: OpenProject MCP Server — Installer for Windows
:: Voyage Software Technologies
:: =============================================================================

:: Use PowerShell for colored output and hidden input
set "PS=powershell -NoProfile -NonInteractive -Command"
set "PSI=powershell -NoProfile -Command"

cls
call :banner

:: ── 1. Python check ───────────────────────────────────────────────────────────
call :step "Checking Python 3.11+"

set "PYTHON_CMD="
for %%c in (python3.11 python3.12 python3.13 python3 python) do (
    if "!PYTHON_CMD!"=="" (
        where %%c >nul 2>&1 && (
            for /f "delims=" %%v in ('%%c -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2^>nul') do (
                for /f "tokens=1,2 delims=." %%a in ("%%v") do (
                    if %%a GEQ 3 (
                        if %%b GEQ 11 (
                            set "PYTHON_CMD=%%c"
                            call :ok "Python %%v found  →  %%c"
                        )
                    )
                )
            )
        )
    )
)

if "!PYTHON_CMD!"=="" (
    call :err "Python 3.11+ not found."
    echo.
    echo    Install from: https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

:: ── 2. pip check ──────────────────────────────────────────────────────────────
!PYTHON_CMD! -m pip --version >nul 2>&1
if errorlevel 1 (
    call :err "pip not found."
    echo    Run: !PYTHON_CMD! -m ensurepip --upgrade
    pause
    exit /b 1
)
call :ok "pip available"

:: ── 3. Install package ────────────────────────────────────────────────────────
call :step "Installing openproject-mcp"

!PYTHON_CMD! -c "import openproject_mcp" >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%v in ('!PYTHON_CMD! -c "import openproject_mcp; print(openproject_mcp.__version__)" 2^>nul') do set "CUR_VER=%%v"
    call :ok "Already installed  (v!CUR_VER!)"
    set /p "UPGRADE=   Upgrade to latest? [y/N]: "
    if /i "!UPGRADE!"=="y" (
        call :info "Upgrading..."
        !PYTHON_CMD! -m pip install --upgrade "git+https://github.com/rharikrishnan84/vst-openproject-mcp.git" --quiet --no-warn-script-location
        call :ok "Upgraded"
    )
) else (
    call :info "Installing from GitHub..."
    !PYTHON_CMD! -m pip install "git+https://github.com/rharikrishnan84/vst-openproject-mcp.git" --quiet --no-warn-script-location
    if errorlevel 1 (
        call :err "Installation failed. Check your internet connection."
        pause
        exit /b 1
    )
    call :ok "Installed successfully"
)

:: Determine runnable command
set "MCP_CMD=openproject-mcp"
where openproject-mcp >nul 2>&1
if errorlevel 1 (
    set "MCP_CMD=!PYTHON_CMD! -m openproject_mcp"
    call :warn "openproject-mcp not on PATH — will use: !PYTHON_CMD! -m openproject_mcp"
) else (
    call :ok "Command available: openproject-mcp"
)

:: ── 4. Configuration prompts ──────────────────────────────────────────────────
call :step "Configuration"

set "DEFAULT_URL=https://projects.voyagesoftwaretech.com"
set /p "INPUT_URL=   OpenProject URL [%DEFAULT_URL%]: "
if "!INPUT_URL!"=="" set "INPUT_URL=!DEFAULT_URL!"

:: Strip trailing slash
if "!INPUT_URL:~-1!"=="/" set "INPUT_URL=!INPUT_URL:~0,-1!"
set "OPENPROJECT_URL=!INPUT_URL!"
call :ok "URL: !OPENPROJECT_URL!"

:: Hidden token input via PowerShell
echo    API Token (hidden):
for /f "delims=" %%t in ('!PSI! "$s = Read-Host 'Press Enter after pasting your API token' -AsSecureString; try { $p = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)); Write-Output $p } catch { $s2 = Read-Host 'API Token'; Write-Output $s2 }"') do (
    set "OPENPROJECT_API_TOKEN=%%t"
)

if "!OPENPROJECT_API_TOKEN!"=="" (
    call :err "API token cannot be empty."
    pause
    exit /b 1
)
call :ok "Token received"

:: ── 5. Test connection ────────────────────────────────────────────────────────
call :step "Testing connection to OpenProject"

set "TMPTEST=%TEMP%\op_mcp_test.py"
(
    echo import asyncio, sys
    echo async def main^(^):
    echo     try:
    echo         import httpx
    echo     except ImportError:
    echo         print^("ERR:httpx not installed"^)
    echo         return
    echo     url   = r"!OPENPROJECT_URL!"
    echo     token = r"!OPENPROJECT_API_TOKEN!"
    echo     try:
    echo         async with httpx.AsyncClient^(
    echo             auth=^("apikey", token^),
    echo             timeout=15.0,
    echo             verify=True,
    echo             follow_redirects=True,
    echo         ^) as client:
    echo             r = await client.get^(f"{url}/api/v3/users/me"^)
    echo             if r.status_code == 200:
    echo                 d = r.json^(^)
    echo                 print^(f"OK:{d.get^('name','?'^)}:{d.get^('email',''^)}"^)
    echo             else:
    echo                 print^(f"ERR:HTTP {r.status_code} — check URL and token"^)
    echo     except httpx.ConnectError:
    echo         print^(f"ERR:Cannot reach {url} — check URL and network"^)
    echo     except httpx.TimeoutException:
    echo         print^("ERR:Request timed out"^)
    echo     except Exception as e:
    echo         print^(f"ERR:{e}"^)
    echo asyncio.run^(main^(^)^)
) > "!TMPTEST!"

for /f "delims=" %%r in ('!PYTHON_CMD! "!TMPTEST!" 2^>^&1') do set "TEST_RESULT=%%r"
del "!TMPTEST!" >nul 2>&1

echo !TEST_RESULT! | findstr /B "OK:" >nul
if not errorlevel 1 (
    for /f "tokens=2,3 delims=:" %%a in ("!TEST_RESULT!") do (
        call :ok "Connected as: %%a (%%b)"
    )
) else (
    set "ERR_MSG=!TEST_RESULT:ERR:=!"
    call :err "Connection failed: !ERR_MSG!"
    echo.
    set /p "CONT=   Continue with configuration anyway? [y/N]: "
    if /i not "!CONT!"=="y" (
        echo Aborted.
        pause
        exit /b 1
    )
)

:: ── 6. Scan and configure MCP clients ─────────────────────────────────────────
call :step "Scanning for installed MCP clients"

set "CONFIGURED=0"

:: Helper: write Python config script to temp file and run it
:: Usage: call :configure_client "Label" "C:\path\to\config.json"
goto :skip_configure_fn

:configure_client
    set "LABEL=%~1"
    set "CONFIG_FILE=%~2"
    echo.
    call :info "!LABEL!"
    call :info "Config: !CONFIG_FILE!"

    set "TMPCFG=%TEMP%\op_mcp_config.py"
    (
        echo import json, pathlib, sys
        echo config_path = pathlib.Path(r"!CONFIG_FILE!")
        echo config_path.parent.mkdir^(parents=True, exist_ok=True^)
        echo if config_path.exists^(^):
        echo     try:
        echo         with open^(config_path, encoding='utf-8'^) as f:
        echo             config = json.load^(f^)
        echo     except Exception:
        echo         config = {}
        echo else:
        echo     config = {}
        echo config.setdefault^("mcpServers", {}^)
        echo config["mcpServers"]["openproject"] = {
        echo     "command": r"!MCP_CMD!",
        echo     "env": {
        echo         "OPENPROJECT_URL":       r"!OPENPROJECT_URL!",
        echo         "OPENPROJECT_API_TOKEN": r"!OPENPROJECT_API_TOKEN!"
        echo     }
        echo }
        echo with open^(config_path, 'w', encoding='utf-8'^) as f:
        echo     json.dump^(config, f, indent=2^)
        echo print^("CONFIGURED"^)
    ) > "!TMPCFG!"

    for /f "delims=" %%r in ('!PYTHON_CMD! "!TMPCFG!" 2^>^&1') do set "CFG_RESULT=%%r"
    del "!TMPCFG!" >nul 2>&1

    echo !CFG_RESULT! | findstr "CONFIGURED" >nul
    if not errorlevel 1 (
        call :ok "Configured !LABEL!"
        set /a CONFIGURED+=1
    ) else (
        call :err "Failed: !CFG_RESULT!"
    )
    goto :eof

:skip_configure_fn

:: ── Claude Desktop ────────────────────────────────────────────────────────────
set "CLAUDE_CFG=%APPDATA%\Claude\claude_desktop_config.json"
if exist "%APPDATA%\Claude\" (
    call :configure_client "Claude Desktop" "!CLAUDE_CFG!"
) else (
    call :warn "Claude Desktop not detected — skipping"
    call :info "Manual config: %APPDATA%\Claude\claude_desktop_config.json"
)

:: ── Cursor IDE ────────────────────────────────────────────────────────────────
if exist "%USERPROFILE%\.cursor\" (
    call :configure_client "Cursor IDE" "%USERPROFILE%\.cursor\mcp.json"
) else (
    call :warn "Cursor IDE not detected — skipping"
    call :info "Manual config: %USERPROFILE%\.cursor\mcp.json"
)

:: ── Claude Code CLI ───────────────────────────────────────────────────────────
where claude >nul 2>&1
if not errorlevel 1 (
    call :configure_client "Claude Code CLI" "%USERPROFILE%\.claude\settings.json"
) else (
    call :warn "Claude Code CLI not detected — skipping"
    call :info "Manual config: %USERPROFILE%\.claude\settings.json"
)

:: ── No clients found ─────────────────────────────────────────────────────────
if "!CONFIGURED!"=="0" (
    echo.
    call :warn "No MCP clients were auto-configured."
    echo.
    call :info "Add this to your client's MCP config file manually:"
    echo.
    echo    {
    echo      "mcpServers": {
    echo        "openproject": {
    echo          "command": "openproject-mcp",
    echo          "env": {
    echo            "OPENPROJECT_URL": "!OPENPROJECT_URL!",
    echo            "OPENPROJECT_API_TOKEN": "^<your-token^>"
    echo          }
    echo        }
    echo      }
    echo    }
)

:: ── 7. Summary ────────────────────────────────────────────────────────────────
echo.
call :divider
%PS% "Write-Host '   Installation complete!' -ForegroundColor Green -BackgroundColor Black"
call :divider
echo.
call :ok "openproject-mcp installed"
call :ok "MCP clients configured: !CONFIGURED!"
echo.
call :info "Restart Claude Desktop / Cursor to activate."
call :info "Then ask: ""List all my OpenProject projects"""
echo.
pause
goto :eof

:: =============================================================================
:: Utility functions
:: =============================================================================
:banner
    %PS% "Write-Host '────────────────────────────────────────────────' -ForegroundColor Cyan"
    %PS% "Write-Host '   OpenProject MCP Server - Installer' -ForegroundColor Cyan"
    %PS% "Write-Host '   Voyage Software Technologies' -ForegroundColor Cyan"
    %PS% "Write-Host '────────────────────────────────────────────────' -ForegroundColor Cyan"
    echo.
    goto :eof

:step
    echo.
    %PS% "Write-Host '▶  %~1' -ForegroundColor Blue"
    goto :eof

:ok
    %PS% "Write-Host '   ✔  %~1' -ForegroundColor Green"
    goto :eof

:warn
    %PS% "Write-Host '   ⚠  %~1' -ForegroundColor Yellow"
    goto :eof

:err
    %PS% "Write-Host '   ✖  %~1' -ForegroundColor Red"
    goto :eof

:info
    %PS% "Write-Host '   ℹ  %~1' -ForegroundColor Cyan"
    goto :eof

:divider
    %PS% "Write-Host '────────────────────────────────────────────────' -ForegroundColor Cyan"
    goto :eof
