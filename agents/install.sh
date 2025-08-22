#!/bin/bash
# Installation script for Superdesign Essential Agents

echo "🚀 Installing Superdesign Essential Agents..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# Make scripts executable
echo "🔧 Setting up permissions..."
chmod +x "$SCRIPT_DIR/code-validator.py"
chmod +x "$SCRIPT_DIR/accessibility-auditor.py"
chmod +x "$SCRIPT_DIR/performance-analyzer.py"
chmod +x "$SCRIPT_DIR/asset-manager.py"
chmod +x "$SCRIPT_DIR/superdesign-integration.py"

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import sys
try:
    from bs4 import BeautifulSoup
    import cssutils
    import requests
    print('✅ All dependencies installed successfully!')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    sys.exit(1)
"

echo "🎉 Installation complete!"
echo ""
echo "Usage:"
echo "  # Run quality assurance on a design file"
echo "  python3 agents/superdesign-integration.py your-design.html"
echo ""
echo "  # Run individual agents"
echo "  python3 agents/code-validator.py your-design.html"
echo "  python3 agents/accessibility-auditor.py your-design.html"
echo "  python3 agents/performance-analyzer.py your-design.html"
echo "  python3 agents/asset-manager.py your-design.html"