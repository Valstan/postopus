#!/bin/bash
# Setup MCP (ssh-mcp) for remote VPS access on Linux/macOS
# This script validates prerequisites and helps configure MCP server

set -e

echo "=== MCP Server Setup (Linux/macOS) ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Node.js
echo "[1/4] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    echo "Install Node.js 22+ from https://nodejs.org/"
    exit 1
fi
node_version=$(node -v)
echo -e "${GREEN}✓ Node.js installed: ${node_version}${NC}"
echo

# Check SSH key
echo "[2/4] Checking SSH key..."
ssh_key="${HOME}/.ssh/id_rsa"
if [ -f "$ssh_key" ]; then
    echo -e "${GREEN}✓ SSH key found at ${ssh_key}${NC}"
else
    echo -e "${YELLOW}⚠ SSH key not found at ${ssh_key}${NC}"
    echo "Generate with: ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa"
    echo
fi
echo

# Check npx
echo "[3/4] Checking npx..."
if ! command -v npx &> /dev/null; then
    echo -e "${RED}✗ npx not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npx available${NC}"
echo

# Test ssh-mcp installation (dry run)
echo "[4/4] Testing ssh-mcp setup..."
if npx -y ssh-mcp --help &> /dev/null; then
    echo -e "${GREEN}✓ ssh-mcp can be installed${NC}"
else
    echo -e "${YELLOW}⚠ ssh-mcp test inconclusive (will install on first use)${NC}"
fi
echo

echo "=== Setup Prerequisites Complete ==="
echo
echo "Next steps:"
echo "1. Add your SSH public key to the remote server's ~/.ssh/authorized_keys"
echo "2. Test SSH connection: ssh -p <PORT> <USER>@<HOST>"
echo "3. Configure MCP in your editor (Cursor/VS Code):"
echo "   - See MCP_SETUP_README.md for configuration examples"
echo "4. Restart your editor"
echo

exit 0
