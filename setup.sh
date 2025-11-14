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

# Check Python version
echo "Checking Python version..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment already exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists."
    echo "To use existing: source .venv/bin/activate"
    echo "To recreate: rm -rf .venv && ./setup.sh"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install core requirements
echo ""
echo "Installing core dependencies..."
pip install -r requirements.txt
echo "✓ Core dependencies installed"

# Install development dependencies if requested
if [ "$INSTALL_DEV" = true ]; then
    echo ""
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
    echo "✓ Development dependencies installed"
fi

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
