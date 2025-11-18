"""
Real Oncall Agent - Automated Ticket Handler
Uses MCP to provide automation tools for common network operations tickets
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
import json
import re
from pathlib import Path
from datetime import datetime

# Create MCP server for oncall agent
mcp = FastMCP("OncallAgent")


class TicketClassifier:
    """Classifies and routes tickets based on patterns"""
    
    def __init__(self, knowledge_base_path: str = "knowledge_base"):
        self.kb_path = Path(knowledge_base_path)
        self.patterns = self._load_patterns()
    
    def _load_patterns(self):
        """Load categorization patterns from knowledge base"""
        patterns = {
            'FIREWALL_NACL': {
                'regex': r'(?i)(NACL|firewall|allow (TCP|UDP)|port \d+|connection refused|timeout|ERR_CONNECTION)',
                'priority_boost': ['timeout', 'refused', 'failed'],
                'assignment_group': 'Network Operations - Firewall'
            },
            'LOAD_BALANCER_A10': {
                'regex': r'(?i)(disable.*nodes?|enable.*nodes?|VIP|\w+-vip\.linkedin\.biz)',
                'priority_boost': ['entire site', 'production'],
                'assignment_group': 'Network Operations - Load Balancer'
            },
            'VPN_REMOTE_ACCESS': {
                'regex': r'(?i)(VPN|RVPN|remote access|force tunnel)',
                'priority_boost': ['cannot access', 'blocked'],
                'assignment_group': 'Remote Access Team'
            },
            'WIFI_WIRELESS': {
                'regex': r'(?i)(wifi|wireless|corpnet|slow internet)',
                'priority_boost': ['entire floor', 'entire site'],
                'assignment_group': 'Network Operations - Wireless'
            },
            'AZURE_CLOUD': {
                'regex': r'(?i)(azure|lnkdprod|blob storage|subnet.*expand)',
                'priority_boost': ['production', 'deployment failed'],
                'assignment_group': 'Cloud Network Engineering'
            },
            'SWITCH_PORT_PHYSICAL': {
                'regex': r'(?i)(switch port|configure.*port|VLAN|fiber)',
                'priority_boost': [],
                'assignment_group': 'Network Operations - Infrastructure'
            },
            'DNS_DHCP_IP': {
                'regex': r'(?i)(DNS|DHCP|IP.*reserv|reserve.*IP)',
                'priority_boost': [],
                'assignment_group': 'Network Operations - IPAM'
            },
            'DATACENTER_OUTAGE': {
                'regex': r'(?i)(entire site.*lost|site.*down|outage)',
                'priority_boost': ['critical', 'emergency'],
                'assignment_group': 'Network Operations - NOC',
                'auto_priority': 'P1'
            }
        }
        return patterns
    
    def classify(self, description: str) -> Dict:
        """Classify ticket based on description"""
        for category, config in self.patterns.items():
            if re.search(config['regex'], description):
                # Check for priority boost keywords
                priority = 'P3'  # Default
                for boost_keyword in config.get('priority_boost', []):
                    if boost_keyword.lower() in description.lower():
                        priority = 'P2'
                        break
                
                if 'auto_priority' in config:
                    priority = config['auto_priority']
                
                return {
                    'category': category,
                    'assignment_group': config['assignment_group'],
                    'suggested_priority': priority,
                    'automation_available': self._check_automation_available(category)
                }
        
        return {
            'category': 'UNCATEGORIZED',
            'assignment_group': 'Network Operations - General',
            'suggested_priority': 'P3',
            'automation_available': False
        }
    
    def _check_automation_available(self, category: str) -> bool:
        """Check if automation tools are available for this category"""
        automated_categories = [
            'LOAD_BALANCER_A10',
            'FIREWALL_NACL',
            'DNS_DHCP_IP',
            'SWITCH_PORT_PHYSICAL'
        ]
        return category in automated_categories


# Initialize classifier
classifier = TicketClassifier()


@mcp.tool()
def classify_ticket(short_description: str) -> str:
    """
    Classify a ServiceNow ticket and suggest category, priority, and assignment group
    
    Args:
        short_description: The ticket short description/summary
    
    Returns:
        JSON string with classification results
    """
    result = classifier.classify(short_description)
    result['analyzed_at'] = datetime.now().isoformat()
    result['description'] = short_description
    
    return json.dumps(result, indent=2)


@mcp.tool()
def a10_disable_vip_nodes(vip_name: str, nodes: str) -> str:
    """
    Disable nodes from A10 load balancer VIP
    
    Args:
        vip_name: VIP name (e.g., LVA1-VDS-VIP.linkedin.biz)
        nodes: Comma-separated list of nodes to disable (e.g., lva1-vds12,lva1-vds13)
    
    Returns:
        Status of the operation
    """
    node_list = [n.strip() for n in nodes.split(',')]
    
    # In production, this would call A10 API
    result = {
        'action': 'disable_nodes',
        'vip': vip_name,
        'nodes': node_list,
        'status': 'simulated_success',
        'message': f'Would disable {len(node_list)} nodes from {vip_name}',
        'next_steps': [
            'Verify nodes are disabled in A10 GUI',
            'Monitor VIP health',
            'Create follow-up ticket to re-enable nodes',
            'Update original ticket with status'
        ],
        'a10_commands': [
            f'# A10 API call would be:',
            f'# POST /axapi/v3/slb/service-group/{vip_name}/member/{node}/disable',
            f'# for each node in: {", ".join(node_list)}'
        ]
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def a10_enable_vip_nodes(vip_name: str, nodes: str) -> str:
    """
    Enable nodes back to A10 load balancer VIP
    
    Args:
        vip_name: VIP name (e.g., LVA1-VDS-VIP.linkedin.biz)
        nodes: Comma-separated list of nodes to enable
    
    Returns:
        Status of the operation
    """
    node_list = [n.strip() for n in nodes.split(',')]
    
    result = {
        'action': 'enable_nodes',
        'vip': vip_name,
        'nodes': node_list,
        'status': 'simulated_success',
        'message': f'Would enable {len(node_list)} nodes on {vip_name}',
        'a10_commands': [
            f'# POST /axapi/v3/slb/service-group/{vip_name}/member/{node}/enable'
        ]
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def validate_nacl_status(source_ip: str, dest_ip: str, port: int, protocol: str = "TCP") -> str:
    """
    Validate NACL/Firewall rule status and connectivity
    
    Args:
        source_ip: Source IP address
        dest_ip: Destination IP address
        port: Destination port
        protocol: TCP or UDP
    
    Returns:
        Validation results with troubleshooting steps
    """
    result = {
        'validation': {
            'source_ip': source_ip,
            'dest_ip': dest_ip,
            'port': port,
            'protocol': protocol,
        },
        'checks_to_perform': [
            f'1. Query Kumo for NACL tickets involving {source_ip} -> {dest_ip}:{port}',
            f'2. Check Palo Alto firewall for matching rule',
            f'3. Test connectivity: telnet {dest_ip} {port}',
            f'4. Check routing table for {dest_ip}',
            f'5. Verify destination service is listening on port {port}',
            f'6. Check for intermediate firewalls or security groups'
        ],
        'palo_alto_commands': [
            f'test security-policy-match from {source_ip} to {dest_ip} protocol {protocol.lower()} destination-port {port}',
            f'show session all filter destination {dest_ip}',
            f'show running security-policy | match {dest_ip}'
        ],
        'common_issues': {
            'approved_not_implemented': 'NACL ticket approved in Kumo but rule not pushed to Palo Alto',
            'timeout': 'Rule exists but destination not responding - check routing or destination',
            'wrong_protocol': f'Rule may be configured for different protocol than {protocol}'
        },
        'resolution_steps': [
            'If NACL not found: Create NACL ticket in Kumo',
            'If approved but not implemented: Escalate to firewall team',
            'If implemented but timeout: Check routing and destination',
            'Update ServiceNow ticket with findings'
        ]
    }
    
    return json.dumps(result, indent=2)


@mcp.tool()
def diagnose_connectivity_issue(description: str) -> str:
    """
    Diagnose network connectivity issues based on error messages
    
    Args:
        description: Ticket description with error details
    
    Returns:
        Diagnostic steps and likely causes
    """
    diagnostics = {
        'description_analyzed': description,
        'detected_issues': [],
        'diagnostic_commands': [],
        'likely_causes': [],
        'resolution_steps': []
    }
    
    # Analyze common error patterns
    if 'ERR_CONNECTION_REFUSED' in description.upper() or 'REFUSED TO CONNECT' in description.upper():
        diagnostics['detected_issues'].append('Connection Refused')
        diagnostics['likely_causes'].extend([
            'Firewall blocking connection',
            'NACL rule not implemented',
            'Destination service not running',
            'Wrong port number'
        ])
        diagnostics['diagnostic_commands'].extend([
            'telnet <destination> <port>',
            'nc -zv <destination> <port>',
            'Check firewall logs in Palo Alto'
        ])
        diagnostics['resolution_steps'].extend([
            '1. Verify NACL ticket status',
            '2. Check if firewall rule exists',
            '3. Verify destination service is running',
            '4. Check if correct port is being used'
        ])
    
    elif 'TIMEOUT' in description.upper():
        diagnostics['detected_issues'].append('Connection Timeout')
        diagnostics['likely_causes'].extend([
            'Routing issue',
            'Destination not responding',
            'Firewall silently dropping packets',
            'MTU mismatch'
        ])
        diagnostics['diagnostic_commands'].extend([
            'traceroute <destination>',
            'ping <destination>',
            'show route <destination>',
            'Check MTU: ping -M do -s 1472 <destination>'
        ])
        diagnostics['resolution_steps'].extend([
            '1. Check if destination is reachable (ping)',
            '2. Trace route to identify where packets stop',
            '3. Verify routing table has path to destination',
            '4. Check for MTU issues if some traffic works'
        ])
    
    elif re.search(r'(?i)(wifi|slow|internet)', description):
        diagnostics['detected_issues'].append('WiFi/Performance Issue')
        diagnostics['likely_causes'].extend([
            'AP overloaded',
            'Interference',
            'Client device issue',
            'Bandwidth congestion'
        ])
        diagnostics['diagnostic_commands'].extend([
            'Check Airwave for AP status',
            'Check client count on AP',
            'Check signal strength',
            'Check for interference'
        ])
        diagnostics['resolution_steps'].extend([
            '1. Identify which AP client is connected to',
            '2. Check AP health in Airwave',
            '3. Check client device WiFi settings',
            '4. Test with different device to isolate issue'
        ])
    
    elif 'DNS' in description.upper():
        diagnostics['detected_issues'].append('DNS Issue')
        diagnostics['likely_causes'].extend([
            'DNS server unreachable',
            'DNS record missing',
            'DNS resolution timeout'
        ])
        diagnostics['diagnostic_commands'].extend([
            'nslookup <hostname>',
            'dig <hostname>',
            'Check DNS server accessibility'
        ])
    
    if not diagnostics['detected_issues']:
        diagnostics['detected_issues'].append('Generic Network Issue')
        diagnostics['diagnostic_commands'].extend([
            'ping <destination>',
            'traceroute <destination>',
            'Check firewall rules',
            'Check routing table'
        ])
    
    return json.dumps(diagnostics, indent=2)


@mcp.tool()
def generate_resolution_template(category: str, subcategory: str = "") -> str:
    """
    Generate resolution template for common ticket categories
    
    Args:
        category: Ticket category (FIREWALL_NACL, LOAD_BALANCER_A10, etc.)
        subcategory: Optional subcategory for more specific templates
    
    Returns:
        Resolution template text
    """
    templates = {
        'FIREWALL_NACL': {
            'default': """
Resolution:
- NACL Ticket: [Kumo ticket number]
- Status: [Approved/Implemented/Validated]
- Firewall Rule: [Rule name or ID]
- Connectivity Test: [Success/Failed]
- Validation Command: test security-policy-match from [source] to [dest] protocol tcp destination-port [port]
- Result: [Working as expected / Additional troubleshooting needed]

Next Steps:
- [Close ticket / Escalate to firewall team / Further investigation needed]
""",
            'nacl_approved_not_implemented': """
Resolution:
- NACL Ticket [number] is Approved in Kumo but not yet implemented
- Escalated to Firewall Team for implementation
- Expected implementation time: 2-4 hours
- Will re-validate connectivity after implementation

Action Taken:
- Verified NACL approval status
- Confirmed rule not present in Palo Alto
- Created escalation to firewall team
- Set reminder to follow up in 2 hours
"""
        },
        'LOAD_BALANCER_A10': {
            'disable_vip_node': """
Resolution:
- Disabled node(s): [node list]
- From VIP: [VIP name]
- Status: Successfully disabled
- Verified in A10 GUI: [timestamp]
- Current VIP health: [status]

Follow-up Action:
- Created reminder ticket to re-enable nodes after maintenance
- Monitoring VIP health during maintenance window
""",
            'enable_vip_node': """
Resolution:
- Enabled node(s): [node list]
- To VIP: [VIP name]
- Status: Successfully enabled
- Node health check: [Passing/Failed]
- Traffic flow confirmed: [Yes/No]
"""
        },
        'WIFI_WIRELESS': {
            'default': """
Resolution:
- Location: [Office, Floor]
- AP Identified: [AP name]
- AP Status: [Up/Down, Client count]
- Issue: [Overloaded/Interference/Hardware failure]
- Action Taken: [Reboot AP / Replace AP / Adjust channels]
- Verified with user: [Connectivity restored]
"""
        },
        'VPN_REMOTE_ACCESS': {
            'default': """
Resolution:
- VPN Account: [Created/Updated]
- Allowlist: [Domains added]
- Tested connectivity: [Success/Failed]
- Credentials sent: [Yes]
- User confirmed access: [Yes/Pending]
"""
        }
    }
    
    template_group = templates.get(category, {})
    template = template_group.get(subcategory, template_group.get('default', 'No template available for this category.'))
    
    return template


@mcp.tool()
def extract_ticket_entities(description: str) -> str:
    """
    Extract key entities from ticket description (IPs, ports, hostnames, VIPs, etc.)
    
    Args:
        description: Ticket description text
    
    Returns:
        JSON with extracted entities
    """
    entities = {
        'ip_addresses': re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', description),
        'ports': re.findall(r'\bport\s+(\d+)\b', description, re.IGNORECASE),
        'protocols': re.findall(r'\b(TCP|UDP|HTTPS?|SSH|RDP)\b', description, re.IGNORECASE),
        'vip_names': re.findall(r'(\w+-vip\.linkedin\.biz)', description, re.IGNORECASE),
        'node_names': re.findall(r'(lva1|ltx1|mln8)-\w+-\d+', description, re.IGNORECASE),
        'hostnames': re.findall(r'([\w-]+\.linkedin\.(biz|com))', description),
        'error_codes': re.findall(r'ERR_[\w_]+', description),
        'datacenter_codes': re.findall(r'\b(lva1|ltx1|mln8|lor1|atk7)\b', description, re.IGNORECASE),
        'azure_resources': re.findall(r'lnkdprod|biz-azure', description, re.IGNORECASE)
    }
    
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return json.dumps(entities, indent=2)


@mcp.tool()
def suggest_automation_tool(ticket_description: str) -> str:
    """
    Suggest which automation tool to use for a given ticket
    
    Args:
        ticket_description: The ticket short description
    
    Returns:
        Suggested tool and usage instructions
    """
    classification = classifier.classify(ticket_description)
    category = classification['category']
    
    suggestions = {
        'LOAD_BALANCER_A10': {
            'tools': ['a10_disable_vip_nodes', 'a10_enable_vip_nodes'],
            'usage': 'Use a10_disable_vip_nodes to disable nodes from VIP for maintenance',
            'example': 'a10_disable_vip_nodes("LVA1-VDS-VIP.linkedin.biz", "lva1-vds12,lva1-vds13")'
        },
        'FIREWALL_NACL': {
            'tools': ['validate_nacl_status', 'diagnose_connectivity_issue'],
            'usage': 'Use validate_nacl_status to check firewall rules and connectivity',
            'example': 'validate_nacl_status("172.20.1.10", "172.30.1.20", 443, "TCP")'
        },
        'WIFI_WIRELESS': {
            'tools': ['diagnose_connectivity_issue'],
            'usage': 'Use diagnose_connectivity_issue to get WiFi troubleshooting steps',
            'example': 'diagnose_connectivity_issue("Slow wifi on 10th floor")'
        }
    }
    
    suggestion = suggestions.get(category, {
        'tools': ['diagnose_connectivity_issue', 'classify_ticket'],
        'usage': 'Use classify_ticket first to categorize, then diagnose_connectivity_issue',
        'example': 'classify_ticket(description)'
    })
    
    result = {
        'ticket_category': category,
        'automation_available': classification['automation_available'],
        'suggested_tools': suggestion['tools'],
        'usage_guide': suggestion['usage'],
        'example_call': suggestion.get('example', 'N/A'),
        'assignment_group': classification['assignment_group']
    }
    
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Run the MCP server
    print("🤖 Starting Oncall Agent MCP Server...")
    print("📋 Available tools:")
    print("  - classify_ticket: Categorize tickets automatically")
    print("  - a10_disable_vip_nodes: Disable A10 load balancer nodes")
    print("  - a10_enable_vip_nodes: Enable A10 load balancer nodes")
    print("  - validate_nacl_status: Check firewall/NACL status")
    print("  - diagnose_connectivity_issue: Diagnose network issues")
    print("  - generate_resolution_template: Get resolution templates")
    print("  - extract_ticket_entities: Extract IPs, ports, hostnames")
    print("  - suggest_automation_tool: Get tool suggestions")
    print("\n✅ Server ready!\n")
    mcp.run()

