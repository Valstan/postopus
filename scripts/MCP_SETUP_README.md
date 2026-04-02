# MCP Server Setup Guide

This directory contains scripts and documentation for configuring MCP (Model Context Protocol) via SSH to access remote VPS from your development environment.

## Quick Start

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_mcp_windows.ps1
```

Then configure your editor using the examples below.

### Linux / macOS (Bash)

```bash
bash ./scripts/setup_mcp_server.sh
```

Then configure your editor using the examples below.

## Editor Configuration

### Cursor

**File location:** `~/.cursor/mcp.json` (macOS/Linux) or `%APPDATA%\Cursor\mcp.json` (Windows)

### VS Code

**File location:** `~/.vscode/mcp.json` (macOS/Linux) or `%APPDATA%\Code\mcp.json` (Windows)

## Configuration Template

```json
{
  "mcpServers": {
    "vps-remote": {
      "command": "npx",
      "args": [
        "-y",
        "ssh-mcp",
        "--host=your.vps.host.com",
        "--port=22",
        "--user=username",
        "--key=/path/to/ssh/key",
        "--timeout=120000"
      ]
    }
  }
}
```

## Important: Argument Format

**✓ CORRECT** — Use `--key=value` format (with equals sign):

```json
"args": [
  "--host=example.com",
  "--port=22",
  "--user=valstan",
  "--key=/home/user/.ssh/id_rsa"
]
```

**✗ INCORRECT** — Do NOT use `--key value` format (with space):

```json
"args": [
  "--host",
  "example.com",
  "--port",
  "22"
]
```

Using spaces will cause `Missing required --host` errors because ssh-mcp cannot parse the spaced format on Windows and some shells.

## Prerequisites

- **Node.js 22+** installed and available in PATH
- **SSH key pair** (`~/.ssh/id_rsa` and `~/.ssh/id_rsa.pub`)
- **Public key on remote server** in `~/.ssh/authorized_keys`
- **SSH access** to the remote VPS

## Setup Steps

### 1. Generate SSH Key (if needed)

**Windows:**
```powershell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa"
```

**Linux/macOS:**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
```

### 2. Add Public Key to Remote Server

Copy your public key to the remote server:

```bash
ssh-copy-id -p <PORT> -i ~/.ssh/id_rsa <USER>@<HOST>
```

Or manually:

```bash
cat ~/.ssh/id_rsa.pub | ssh -p <PORT> <USER>@<HOST> "cat >> ~/.ssh/authorized_keys"
```

### 3. Test SSH Connection

```bash
ssh -p <PORT> <USER>@<HOST> "echo OK"
```

If this succeeds, MCP configuration should work.

### 4. Create/Update Editor Configuration

Edit your editor's `mcp.json` file and add the MCP server configuration using the template above.

**Replace placeholders:**
- `your.vps.host.com` — Your VPS hostname or IP
- `22` — SSH port
- `username` — SSH username
- `/path/to/ssh/key` — Full path to private key

### 5. Restart Editor

Close and reopen your editor (Cursor/VS Code) to load the new MCP configuration.

### 6. Verify Connection

- Check the MCP status in your editor's settings
- Status should show **green** (enabled)
- If red, check the MCP logs

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Missing required --host` / `--user` | Arguments use spaces instead of `=` | Use `--host=value` format, NOT `--host value` |
| `SSH exec error: No response from server` | SSH timeout or server busy | Retry; increase `--timeout` if needed |
| `ENOENT` when starting | Node.js not in PATH | Verify `node --version` and `npx --version` work |
| `Permission denied (publickey)` | Public key not on server | Run `ssh-copy-id` or manually add key to server |
| Editor freezes on first use | npx downloading ssh-mcp package | Wait 10–15 seconds; npx caches the package |
| MCP shows red status | Connection failed or configuration error | Check editor MCP logs for details |

## File Locations

**SSH Key:**
- Windows: `C:\Users\<USERNAME>\.ssh\id_rsa`
- Linux/macOS: `~/.ssh/id_rsa`

**Editor MCP Config:**
- Cursor Windows: `%APPDATA%\Cursor\mcp.json`
- Cursor macOS/Linux: `~/.cursor/mcp.json`
- VS Code Windows: `%APPDATA%\Code\mcp.json`
- VS Code macOS/Linux: `~/.vscode/mcp.json`

**Editor MCP Logs:**
- Cursor: `%APPDATA%\Cursor\logs\` (Windows) or `~/.config/Cursor/logs/` (macOS/Linux)
- Check for `MCP` log files to diagnose connection issues

## Additional Resources

- [SSH-MCP GitHub](https://github.com/anysphere/ssh-mcp)
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- SSH documentation: `man ssh`, `man ssh-keygen`, `man ssh-copy-id`

## Non-Destructive Nature

These scripts and configuration:
- Only **validate** prerequisites; they do not install or modify anything without explicit user action
- Do not modify existing SSH keys or configurations
- Do not write to system files
- Simply provide **guidance** and setup instructions
- Users must explicitly update their editor configuration file
