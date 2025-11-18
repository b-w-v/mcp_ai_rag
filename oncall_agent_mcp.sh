#!/bin/bash

# MCP Server launcher for Oncall Agent
# Use this in your claude_desktop_config.json

cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the oncall agent MCP server
exec python oncall_agent.py

