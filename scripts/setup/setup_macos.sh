#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Checking Mark2TeX dependencies for macOS...${NC}"

# 1. Check Homebrew
if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# 2. Check Docker
if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is already installed.${NC}"
else
    echo "Installing Docker Desktop..."
    brew install --cask docker
    echo -e "${GREEN}✓ Docker installed successfully.${NC}"
fi

# 3. Check Python
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Python3 is already installed.${NC}"
else
    echo "Installing Python3..."
    brew install python
    echo -e "${GREEN}✓ Python3 installed successfully.${NC}"
fi

# 4. Final Validation
docker --version && python3 --version
