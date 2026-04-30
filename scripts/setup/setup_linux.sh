#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Checking Mark2TeX dependencies for Linux...${NC}"

# 1. Privilege Check
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo: sudo bash scripts/setup/setup_linux.sh"
  exit 1
fi

# 2. Check Docker
if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is already installed.${NC}"
else
    echo "Installing Docker..."
    curl -sSL https://get.docker.com | sh
    echo -e "${GREEN}✓ Docker installed successfully.${NC}"
fi

# 3. Check Python
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Python3 is already installed.${NC}"
else
    echo "Installing Python3..."
    apt-get update && apt-get install -y python3 python3-pip python3-venv
    echo -e "${GREEN}✓ Python3 installed successfully.${NC}"
fi

# 4. Final Validation
docker --version && python3 --version

echo -e "\n${BLUE}Post-installation step:${NC}"
echo "Run 'sudo usermod -aG docker \$USER' and restart your session to use Docker without sudo."
