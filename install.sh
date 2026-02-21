#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CW_PY="$SCRIPT_DIR/cw.py"
INSTALL_DIR="$HOME/.local/bin"
TARGET="$INSTALL_DIR/cw"

# Resolve the Python interpreter: prefer the project venv, fall back to python3
if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON="$(command -v python3)"
else
    echo "Error: no Python interpreter found." >&2
    exit 1
fi

# Verify cw.py exists
if [[ ! -f "$CW_PY" ]]; then
    echo "Error: $CW_PY not found." >&2
    exit 1
fi

# Check that ~/.local/bin exists
if [[ ! -d "$INSTALL_DIR" ]]; then
    read -r -p "$INSTALL_DIR does not exist. Create it? [y/N] " reply
    if [[ "$reply" =~ ^[Yy]$ ]]; then
        mkdir -p "$INSTALL_DIR"
        echo "Created $INSTALL_DIR"
    else
        echo "Aborting installation." >&2
        exit 1
    fi
fi

# Warn if ~/.local/bin is not in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "Warning: $INSTALL_DIR is not in your PATH."
    echo "  Add the following to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Prompt before overwriting an existing cw command
if [[ -e "$TARGET" ]]; then
    read -r -p "$TARGET already exists. Overwrite? [y/N] " reply
    if [[ ! "$reply" =~ ^[Yy]$ ]]; then
        echo "Aborting installation." >&2
        exit 1
    fi
fi

# Write the wrapper script
cat > "$TARGET" <<EOF
#!/usr/bin/env bash
exec "$PYTHON" "$CW_PY" "\$@"
EOF
chmod +x "$TARGET"

echo "Installed: $TARGET"
echo "  Using Python: $PYTHON"
echo "  Script: $CW_PY"
