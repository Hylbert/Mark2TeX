#!/bin/bash
set -e

# 1. Create ~/.mark2tex/ folder
echo "📁 Creating installation directory ~/.mark2tex..."
mkdir -p ~/.mark2tex/

# 2. Copy current project files
echo "📦 Copying project files..."
cp -r bin templates src requirements.txt ~/.mark2tex/

# 3. Check for uv installation
if ! command -v uv &> /dev/null
then
    echo "⚠️  uv is not installed. Installing uv now..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to path for current session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# 4. Create Python Virtual Environment using uv (with --clear to avoid prompts)
echo "🐍 Creating virtual environment with uv in ~/.mark2tex/venv..."
uv venv --clear ~/.mark2tex/venv

# 5. Install python dependencies using the global uv pointing to the venv python
echo "📦 Installing Python dependencies with uv..."
uv pip install -r ~/.mark2tex/requirements.txt --python ~/.mark2tex/venv/bin/python

# 6. Create a wrapper script to run the TUI with the venv
echo "📝 Creating runner script..."
cat <<EOF > ~/.mark2tex/mark2tex-runner
#!/bin/bash
export PYTHONPATH="\$HOME/.mark2tex/src"
~/.mark2tex/venv/bin/python \$HOME/.mark2tex/src/main.py "\$@"
EOF
chmod +x ~/.mark2tex/mark2tex-runner

# 7. Create symlink to /usr/local/bin/mark2tex
echo "🔗 Creating global symlink..."
sudo ln -sf ~/.mark2tex/mark2tex-runner /usr/local/bin/mark2tex

echo "🎉 Mark2TeX installed successfully! You can now run 'mark2tex' from any directory."
