#!/bin/bash
# MCP Development Environment Setup
# This script permanently disables authentication for development

# Export environment variables
export DANGEROUSLY_OMIT_AUTH=true
export MCP_INSPECTOR_PORT=6278

# Optional: Add to shell profile for permanent effect
echo "export DANGEROUSLY_OMIT_AUTH=true" >> ~/.zshrc
echo "export MCP_INSPECTOR_PORT=6278" >> ~/.zshrc

echo "✅ MCP authentication disabled permanently"
echo "✅ Environment variables added to ~/.zshrc"
echo "✅ Restart your terminal or run 'source ~/.zshrc' to apply changes"

