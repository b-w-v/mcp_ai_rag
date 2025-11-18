#!/bin/bash

# Quick Start Script for Oncall Agent
# This script helps you set up and run the ticket analyzer

echo "🤖 Oncall Agent - Quick Start"
echo "================================"
echo ""

# Check if Excel file exists
if [ -f "servicenow_tickets.xlsx" ]; then
    echo "✅ Found: servicenow_tickets.xlsx"
    EXCEL_FILE="servicenow_tickets.xlsx"
elif [ -f "tickets.xlsx" ]; then
    echo "✅ Found: tickets.xlsx"
    EXCEL_FILE="tickets.xlsx"
elif [ -f "snow_export.xlsx" ]; then
    echo "✅ Found: snow_export.xlsx"
    EXCEL_FILE="snow_export.xlsx"
else
    echo "❌ No Excel file found!"
    echo ""
    echo "Please export your ServiceNow tickets and save as:"
    echo "  📄 servicenow_tickets.xlsx"
    echo ""
    echo "Place it in this directory:"
    echo "  📁 $(pwd)"
    echo ""
    echo "Required columns:"
    echo "  - Number"
    echo "  - Short Description"
    echo "  - Category (optional)"
    echo "  - Priority"
    echo "  - Assignment Group"
    echo "  - Created"
    echo "  - Resolved"
    echo ""
    echo "Then run this script again: ./quick_start.sh"
    echo ""
    exit 1
fi

echo ""
echo "📦 Installing dependencies..."
uv pip install pandas openpyxl 2>/dev/null || pip install pandas openpyxl

echo ""
echo "🔍 Analyzing tickets from: $EXCEL_FILE"
echo ""
python ticket_analyzer.py

echo ""
echo "================================"
echo "✅ Analysis Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Review: ticket_analysis_report.json"
echo "  2. Review: knowledge_base/ directory"
echo "  3. Start agent: python oncall_agent.py"
echo "  4. Read guide: ONCALL_AGENT_GUIDE.md"
echo ""
echo "🚀 To start the oncall agent now, run:"
echo "   python oncall_agent.py"
echo ""

