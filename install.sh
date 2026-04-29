#!/bin/bash
set -e

# 1. Create ~/.mark2tex/ folder
echo "📁 Creating installation directory ~/.mark2tex..."
mkdir -p ~/.mark2tex/

# 2. Copy current project files
echo "📦 Copying project files..."
cp -r bin templates src requirements.txt ~/.mark2tex/

# 3. Install python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r ~/.mark2tex/requirements.txt

# 4. Create symlink to /usr/local/bin/mark2tex
echo "🔗 Creating global symlink..."
# Using sudo for /usr/local/bin as it's a system directory
sudo ln -sf ~/.mark2tex/src/main.py /usr/local/bin/mark2tex

# 5. Ensure main.py is executable
echo "⚙️ Setting permissions..."
chmod +x ~/.mark2tex/src/main.py

echo "🎉 Mark2TeX installed successfully! You can now run 'mark2tex' from any directory."
