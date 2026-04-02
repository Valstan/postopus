# Setup MCP (ssh-mcp) for remote VPS access on Windows
# This script validates prerequisites and helps configure MCP server
# Run as: powershell -ExecutionPolicy Bypass -File .\scripts\setup_mcp_windows.ps1

Write-Host "=== MCP Server Setup (Windows) ===" -ForegroundColor Cyan
Write-Host ""

# Check Node.js
Write-Host "[1/4] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
    Write-Host "Install Node.js 22+ from https://nodejs.org/"
    exit 1
}
Write-Host "✓ Node.js installed: $nodeVersion" -ForegroundColor Green
Write-Host ""

# Check SSH key
Write-Host "[2/4] Checking SSH key..." -ForegroundColor Yellow
$sshKey = Join-Path $env:USERPROFILE ".ssh\id_rsa"
if (Test-Path $sshKey) {
    Write-Host "✓ SSH key found at $sshKey" -ForegroundColor Green
} else {
    Write-Host "⚠ SSH key not found at $sshKey" -ForegroundColor Yellow
    Write-Host "Generate with: ssh-keygen -t rsa -b 4096 -f `"$env:USERPROFILE\.ssh\id_rsa`""
    Write-Host ""
}
Write-Host ""

# Check npx
Write-Host "[3/4] Checking npx..." -ForegroundColor Yellow
$npxTest = npx --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ npx not found" -ForegroundColor Red
    exit 1
}
Write-Host "✓ npx available: $npxTest" -ForegroundColor Green
Write-Host ""

# Test ssh-mcp availability
Write-Host "[4/4] Testing ssh-mcp setup..." -ForegroundColor Yellow
try {
    npx -y ssh-mcp --help 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ ssh-mcp can be installed" -ForegroundColor Green
    } else {
        Write-Host "⚠ ssh-mcp test inconclusive (will install on first use)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ ssh-mcp test inconclusive (will install on first use)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "=== Setup Prerequisites Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Add your SSH public key to the remote server's ~/.ssh/authorized_keys"
Write-Host "2. Test SSH connection: ssh -p <PORT> <USER>@<HOST>"
Write-Host "3. Configure MCP in your editor (Cursor/VS Code):"
Write-Host "   - See scripts\MCP_SETUP_README.md for configuration examples"
Write-Host "   - CRITICAL: Use --key=value format (with =), NOT --key value"
Write-Host "4. Restart your editor"
Write-Host ""

exit 0
