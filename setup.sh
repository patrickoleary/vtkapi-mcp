#!/bin/bash
# VTK API MCP Server - Setup Script
# Creates virtual environment and installs dependencies
#
# Usage:
#   ./setup.sh          # Standard installation
#   ./setup.sh --dev    # Include development/testing dependencies

set -e  # Exit on error

# Check for --dev flag
INSTALL_DEV=false
if [[ "$1" == "--dev" ]]; then
    INSTALL_DEV=true
fi

echo "========================================="
echo "VTK API MCP Server Setup"
echo "========================================="
echo ""
if [ "$INSTALL_DEV" = true ]; then
    echo "Mode: Development (with testing dependencies)"
else
    echo "Mode: Standard installation"
fi
echo ""

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is required but was not found on your PATH."
    echo "Install it from https://github.com/astral-sh/uv or via: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check Python version (helpful for troubleshooting)
if command -v python3 &> /dev/null; then
    echo "Detected Python version:"
    python3 --version
else
    echo "Warning: python3 command not found. uv will download/drive the required interpreter."
fi

# Create or reuse virtual environment
if [ -d ".venv" ]; then
    echo "Virtual environment '.venv' already exists – reusing it."
else
    echo ""
    echo "Creating virtual environment with uv..."
    uv venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Sync dependencies via uv
SYNC_ARGS=()
if [ "$INSTALL_DEV" = true ]; then
    SYNC_ARGS+=(--extra dev)
fi

echo ""
echo "Installing project dependencies with uv sync ${SYNC_ARGS[*]}..."
uv sync "${SYNC_ARGS[@]}"
echo "✓ Dependencies installed"

# Check for data file
echo ""
echo "Checking for VTK API data..."
if [ -f "data/vtk-python-docs.jsonl" ]; then
    echo "✓ VTK API data found: data/vtk-python-docs.jsonl"
else
    echo "⚠ Warning: VTK API data not found at data/vtk-python-docs.jsonl"
    echo "  This file is required for the MCP server to function."
    echo "  Please ensure the data file is present before running the server."
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo ""
echo "Next steps:"
echo "  1. Test MCP integration:"
echo "     python demo_mcp_integration.py"
echo ""
echo "  2. Configure in your MCP client (e.g., Claude Desktop):"
echo '     Add to config.json:'
echo '     {'
echo '       "mcpServers": {'
echo '         "vtk-api": {'
echo '           "command": "python",'
echo '           "args": ['
echo '             "-m",'
echo '             "vtkapi_mcp",'
echo '             "--api-docs",'
echo '             "/full/path/to/vtkapi-mcp/data/vtk-python-docs.jsonl"'
echo '           ],'
echo '           "cwd": "/full/path/to/vtkapi-mcp"'
echo '         }'
echo '       }'
echo '     }'
echo ""
echo "See README.md for full documentation."
echo ""
