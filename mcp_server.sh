#!/bin/bash
# MCP Server Management Script

case "$1" in
    start)
        echo "🚀 Starting MCP dev server..."
        cd /Users/bwv/Desktop/mcp_server_demo/network_controller
        uv run mcp dev controller.py &
        echo "✅ MCP server started in background"
        echo "🌐 Access at: http://localhost:6274"
        ;;
    stop)
        echo "🛑 Stopping MCP dev server..."
        pkill -f "mcp dev"
        lsof -ti:6274 -ti:6277 | xargs kill -9 2>/dev/null
        echo "✅ MCP server stopped"
        ;;
    status)
        if pgrep -f "mcp dev" > /dev/null; then
            echo "✅ MCP server is running"
            echo "🌐 Access at: http://localhost:6274"
        else
            echo "❌ MCP server is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        echo "  start  - Start MCP dev server"
        echo "  stop   - Stop MCP dev server"
        echo "  status - Check MCP server status"
        exit 1
        ;;
esac

