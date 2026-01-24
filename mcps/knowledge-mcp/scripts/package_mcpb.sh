#!/bin/bash
# Package knowledge-mcp as MCPB bundle for Claude Desktop
#
# Prerequisites:
#   npm install -g @anthropic-ai/mcpb
#
# Usage:
#   ./scripts/package_mcpb.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== Packaging knowledge-mcp as MCPB bundle ==="
echo ""

# Check mcpb installed
if ! command -v mcpb &> /dev/null; then
    echo "ERROR: mcpb not found. Install with:"
    echo "  npm install -g @anthropic-ai/mcpb"
    exit 1
fi

# Check manifest exists
if [ ! -f manifest.json ]; then
    echo "ERROR: manifest.json not found"
    exit 1
fi

# Validate manifest
echo "Validating manifest.json..."
mcpb validate manifest.json
echo ""

# Run tests before packaging
echo "Running tests..."
poetry run pytest tests/ -v --tb=short
echo ""

# Create bundle
echo "Creating .mcpb bundle..."
mcpb pack

# Find created bundle
BUNDLE=$(ls -t *.mcpb 2>/dev/null | head -1)

if [ -n "$BUNDLE" ]; then
    echo ""
    echo "=== SUCCESS ==="
    echo "Bundle created: $BUNDLE"
    echo ""
    echo "Installation options:"
    echo "  1. Double-click $BUNDLE"
    echo "  2. Drag to Claude Desktop"
    echo "  3. Run: mcpb install $BUNDLE"
    echo ""
    echo "Required configuration:"
    echo "  OPENAI_API_KEY - OpenAI API key for embeddings"
    echo ""
    echo "Optional configuration:"
    echo "  QDRANT_URL, QDRANT_API_KEY - For Qdrant Cloud storage"
    echo "  CHROMADB_PATH - For local ChromaDB storage"
else
    echo "ERROR: Bundle not created"
    exit 1
fi
