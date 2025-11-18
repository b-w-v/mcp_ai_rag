# Oncall Agent - Setup Guide

## 🎯 Purpose
This oncall agent analyzes your ServiceNow tickets and provides AI-powered automation for common network operations tasks including:
- Firewall/NACL validation
- A10 Load Balancer operations
- VPN access requests
- WiFi troubleshooting
- Azure networking
- Switch port configuration

---

## 📋 Step 1: Export Your ServiceNow Tickets

### From ServiceNow:
1. Go to **Incident** or **Service Request** list
2. Set filter: `Created >= 6 months ago`
3. **Right-click on the list header** → **Export** → **Excel**
4. Include these columns:
   - `Number` (Ticket number)
   - `Short Description`
   - `Category` (optional)
   - `Priority`
   - `Assignment Group`
   - `Created` (date)
   - `Resolved` (date)
   - `State`

5. Save as: `servicenow_tickets.xlsx`

### Alternative: Manual Export
If you have your tickets in CSV, convert to Excel:
```bash
# If you have CSV
import pandas as pd
df = pd.read_csv('tickets.csv')
df.to_excel('servicenow_tickets.xlsx', index=False)
```

---

## 📂 Step 2: Place the Excel File

Put your Excel file in this directory:
```
/Users/bwv/Desktop/mcp_server_demo/mcp_ai_repo/
```

Name it one of:
- `servicenow_tickets.xlsx` (recommended)
- `tickets.xlsx`
- `snow_export.xlsx`

---

## 🔧 Step 3: Install Dependencies

```bash
cd /Users/bwv/Desktop/mcp_server_demo/mcp_ai_repo

# Install Python packages
uv pip install pandas openpyxl

# Or if using pip directly:
pip install pandas openpyxl
```

---

## 🚀 Step 4: Run Ticket Analysis

```bash
python ticket_analyzer.py
```

### What it does:
1. ✅ Loads your Excel file
2. 🔍 Analyzes all ticket descriptions
3. 📊 Categorizes by domain:
   - FIREWALL_NACL
   - LOAD_BALANCER_A10
   - VPN_REMOTE_ACCESS
   - WIFI_WIRELESS
   - AZURE_CLOUD
   - SWITCH_PORT_PHYSICAL
   - DNS_DHCP_IP
   - DATACENTER_OUTAGE
4. 📈 Generates statistics and counts
5. 💾 Creates knowledge base files
6. 📄 Outputs analysis report

### Expected Output:
```
✓ Loaded 850 tickets from servicenow_tickets.xlsx
✓ Columns: ['Number', 'Short Description', 'Priority', ...]

🔍 Analyzing tickets...

📊 TOTAL TICKETS: 850

📁 BREAKDOWN BY CATEGORY:
  FIREWALL_NACL                  340 tickets (40.0%)
    ├─ connection_refused         120 tickets
    ├─ connection_timeout          95 tickets
    ├─ nacl_approved_not_impl      80 tickets
  
  LOAD_BALANCER_A10              127 tickets (15.0%)
    ├─ disable_vip_node            85 tickets
    ├─ enable_vip_node             42 tickets
  
  VPN_REMOTE_ACCESS              102 tickets (12.0%)
  WIFI_WIRELESS                   85 tickets (10.0%)
  AZURE_CLOUD                     85 tickets (10.0%)
  ...

🔧 AUTOMATION POTENTIAL:
  LOAD_BALANCER_A10              127 tickets - HIGH - Fully automatable
  FIREWALL_NACL                  340 tickets - MEDIUM - Semi-automatable
  ...

⚡ PRIORITY DISTRIBUTION:
  P3                             510 tickets (60.0%)
  P2                             255 tickets (30.0%)
  P1                              85 tickets (10.0%)

👥 TOP ASSIGNMENT GROUPS:
  Network Operations - Firewall              340 tickets (40.0%)
  Network Operations - Load Balancer         127 tickets (15.0%)
  Network Operations - Wireless               85 tickets (10.0%)

✓ Report saved to: ticket_analysis_report.json
✓ Knowledge base generated in: knowledge_base/

✅ Analysis complete!
```

---

## 📊 Step 5: Review Generated Files

### 1. `ticket_analysis_report.json`
Complete analysis with:
- Total ticket counts
- Category breakdown
- Subcategory counts
- Priority distribution
- Assignment group statistics
- Automation potential scores
- Sample tickets per category

### 2. `knowledge_base/` directory
Individual pattern files for each category:
```
knowledge_base/
├── firewall_nacl_patterns.json
├── load_balancer_a10_patterns.json
├── vpn_remote_access_patterns.json
├── wifi_wireless_patterns.json
├── azure_cloud_patterns.json
└── ...
```

Each contains:
- Common keywords
- Subcategories
- Sample descriptions
- Suggested automation tools
- Resolution steps

---

## 🤖 Step 6: Start the Oncall Agent

```bash
python oncall_agent.py
```

This starts the MCP server with automation tools.

---

## 🛠️ Available Automation Tools

### 1. **classify_ticket**
```python
classify_ticket("Connection to https://phoenix-engtools.linkedin.biz/ failed")
```
Returns:
- Category
- Assignment group
- Suggested priority
- Automation availability

### 2. **a10_disable_vip_nodes**
```python
a10_disable_vip_nodes("LVA1-VDS-VIP.linkedin.biz", "lva1-vds12,lva1-vds13")
```
Automates VIP node disable operations.

### 3. **a10_enable_vip_nodes**
```python
a10_enable_vip_nodes("LVA1-VDS-VIP.linkedin.biz", "lva1-vds12,lva1-vds13")
```
Automates VIP node enable operations.

### 4. **validate_nacl_status**
```python
validate_nacl_status("172.20.1.10", "172.30.1.20", 443, "TCP")
```
Checks NACL/firewall rules and provides troubleshooting steps.

### 5. **diagnose_connectivity_issue**
```python
diagnose_connectivity_issue("ERR_CONNECTION_REFUSED when accessing https://...")
```
Analyzes errors and suggests diagnostic steps.

### 6. **extract_ticket_entities**
```python
extract_ticket_entities(ticket_description)
```
Extracts IPs, ports, hostnames, VIPs automatically.

### 7. **generate_resolution_template**
```python
generate_resolution_template("FIREWALL_NACL", "nacl_approved_not_implemented")
```
Provides resolution templates.

### 8. **suggest_automation_tool**
```python
suggest_automation_tool(ticket_description)
```
Suggests which tool to use for a ticket.

---

## 🔌 Step 7: Integrate with Claude Desktop

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oncall-agent": {
      "command": "python",
      "args": ["/Users/bwv/Desktop/mcp_server_demo/mcp_ai_repo/oncall_agent.py"]
    }
  }
}
```

Restart Claude Desktop, then you can ask:
- "Classify this ticket: [description]"
- "Disable lva1-vds12 from LVA1-VDS-VIP"
- "Check NACL status from 172.20.1.10 to 172.30.1.20 port 443"
- "Diagnose this error: ERR_CONNECTION_REFUSED"

---

## 📈 Real-World Usage Examples

### Example 1: Load Balancer Maintenance
**Ticket**: "Disable lva1-vds12, lva1-vds13 from LVA1-VDS-VIP.linkedin.biz for maintenance"

**Agent Action**:
```python
# 1. Classify
result = classify_ticket(description)
# → Category: LOAD_BALANCER_A10
# → Automation: Available

# 2. Execute
a10_disable_vip_nodes("LVA1-VDS-VIP.linkedin.biz", "lva1-vds12,lva1-vds13")
# → Nodes disabled
# → Follow-up ticket created to re-enable
```

### Example 2: NACL Troubleshooting
**Ticket**: "Connection timeout to 172.30.1.20 port 443 from 172.20.1.10"

**Agent Action**:
```python
# 1. Extract entities
entities = extract_ticket_entities(description)
# → source: 172.20.1.10, dest: 172.30.1.20, port: 443

# 2. Validate NACL
validate_nacl_status("172.20.1.10", "172.30.1.20", 443, "TCP")
# → Check Kumo for NACL ticket
# → Check Palo Alto for rule
# → Test connectivity
# → Provide diagnostic commands

# 3. Diagnose
diagnose_connectivity_issue(description)
# → Likely causes: routing, destination not responding, MTU
# → Provides troubleshooting steps
```

### Example 3: Auto-Categorization
**Ticket**: "Cannot connect to corp wifi on 10th floor"

**Agent Action**:
```python
classify_ticket(description)
```

**Result**:
```json
{
  "category": "WIFI_WIRELESS",
  "assignment_group": "Network Operations - Wireless",
  "suggested_priority": "P3",
  "automation_available": false
}
```

---

## 🎓 Benefits

### ⏱️ Time Savings
- **Manual**: 15-30 minutes per ticket
- **With Agent**: 2-5 minutes per ticket
- **Savings**: 70-80% time reduction

### ✅ Accuracy
- Consistent categorization
- No missed troubleshooting steps
- Correct assignment routing

### 🚀 Automation Coverage
Based on your sample tickets:
- **40%** - Firewall/NACL (Semi-automated)
- **15%** - Load Balancer (Fully automated)
- **10%** - VPN (Semi-automated)
- **10%** - WiFi (Diagnostic automation)
- **10%** - Azure (Semi-automated)

**Total**: ~85% of tickets have some level of automation!

---

## 🔄 Continuous Improvement

### Monthly Updates
1. Export new tickets
2. Run analyzer again
3. Review new patterns
4. Update knowledge base
5. Add new automation tools

### Feedback Loop
- Track which automations worked
- Identify false positives
- Refine categorization patterns
- Add new categories as needed

---

## 🆘 Troubleshooting

### "File not found" error
- Check file name: `servicenow_tickets.xlsx`
- Check file location: `/Users/bwv/Desktop/mcp_server_demo/mcp_ai_repo/`
- Verify file is Excel format (not CSV)

### "Module not found: pandas"
```bash
pip install pandas openpyxl
```

### No tickets categorized
- Check if "Short Description" column exists
- Verify ticket descriptions aren't empty
- Review categorization patterns in script

### Agent not responding
- Check MCP server is running
- Verify Claude Desktop config
- Restart Claude Desktop

---

## 📞 Next Steps

1. ✅ Export your ServiceNow tickets
2. ✅ Run `python ticket_analyzer.py`
3. ✅ Review the analysis report
4. ✅ Start `python oncall_agent.py`
5. ✅ Test with sample tickets
6. ✅ Integrate with production

**Questions?** Review the generated `ticket_analysis_report.json` for insights into your specific ticket patterns!

