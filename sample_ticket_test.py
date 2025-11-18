"""
Sample Ticket Test - Test the oncall agent with real ticket examples
"""

import json
from oncall_agent import (
    classifier,
    classify_ticket,
    validate_nacl_status,
    diagnose_connectivity_issue,
    extract_ticket_entities,
    suggest_automation_tool,
    a10_disable_vip_nodes
)


# Sample tickets from your actual data
SAMPLE_TICKETS = [
    {
        "number": "INC0001",
        "description": "Mac | SSH | Connection to https://phoenix-engtools.linkedin.biz/ failed error",
        "expected_category": "FIREWALL_NACL"
    },
    {
        "number": "INC0002",
        "description": "Disable below nodes from lva1-vds-vip.linkedin.biz (172.29.37.20) VIP: lva1-vds12, lva1-vds13, lva1-vds14",
        "expected_category": "LOAD_BALANCER_A10"
    },
    {
        "number": "INC0003",
        "description": "Slow corpnet wifi speed in Bellevue office",
        "expected_category": "WIFI_WIRELESS"
    },
    {
        "number": "INC0004",
        "description": "New RVPN request for SPHAERA INC (DDR0001042)",
        "expected_category": "VPN_REMOTE_ACCESS"
    },
    {
        "number": "INC0005",
        "description": "Need more IP Space in EASTUS region in lnkdprod tenant",
        "expected_category": "AZURE_CLOUD"
    },
    {
        "number": "INC0006",
        "description": "Need to configure and enable 2 Switch Port mln8-0-masw01. Port No: 25. Vlan: 203",
        "expected_category": "SWITCH_PORT_PHYSICAL"
    },
    {
        "number": "INC0007",
        "description": "Entire site lost all communications. 172.30.226.14, 172.30.228.13",
        "expected_category": "DATACENTER_OUTAGE"
    },
    {
        "number": "INC0008",
        "description": "The NACL is approved, but not implemented",
        "expected_category": "FIREWALL_NACL"
    },
    {
        "number": "INC0009",
        "description": "Connection to linxuat-app.prod.linkedin.com refused (ERR_CONNECTION_REFUSED)",
        "expected_category": "FIREWALL_NACL"
    },
    {
        "number": "INC0010",
        "description": "Please reserve below IP addresses: 172.28.131.50, 172.28.131.51, 172.28.131.52",
        "expected_category": "DNS_DHCP_IP"
    }
]


def test_classification():
    """Test ticket classification"""
    print("="*80)
    print("TEST 1: TICKET CLASSIFICATION")
    print("="*80)
    
    correct = 0
    total = len(SAMPLE_TICKETS)
    
    for ticket in SAMPLE_TICKETS:
        result = json.loads(classify_ticket(ticket["description"]))
        
        is_correct = result["category"] == ticket["expected_category"]
        status = "✅" if is_correct else "❌"
        
        if is_correct:
            correct += 1
        
        print(f"\n{status} {ticket['number']}")
        print(f"   Description: {ticket['description'][:70]}...")
        print(f"   Expected: {ticket['expected_category']}")
        print(f"   Got: {result['category']}")
        print(f"   Assignment: {result['assignment_group']}")
        print(f"   Priority: {result['suggested_priority']}")
        print(f"   Automation: {result['automation_available']}")
    
    print(f"\n{'='*80}")
    print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"{'='*80}\n")


def test_entity_extraction():
    """Test entity extraction"""
    print("\n" + "="*80)
    print("TEST 2: ENTITY EXTRACTION")
    print("="*80)
    
    test_cases = [
        "Disable lva1-vds12 from LVA1-VDS-VIP.linkedin.biz",
        "Connection from 172.20.1.10 to 172.30.1.20 port 443 failed",
        "ERR_CONNECTION_REFUSED to https://phoenix-engtools.linkedin.biz port 443",
        "Need subnet in lnkdprod tenant for 172.28.131.0/24"
    ]
    
    for desc in test_cases:
        print(f"\n📝 {desc}")
        entities = json.loads(extract_ticket_entities(desc))
        
        if entities.get('ip_addresses'):
            print(f"   IPs: {entities['ip_addresses']}")
        if entities.get('ports'):
            print(f"   Ports: {entities['ports']}")
        if entities.get('vip_names'):
            print(f"   VIPs: {entities['vip_names']}")
        if entities.get('node_names'):
            print(f"   Nodes: {entities['node_names']}")
        if entities.get('hostnames'):
            print(f"   Hosts: {entities['hostnames']}")
        if entities.get('error_codes'):
            print(f"   Errors: {entities['error_codes']}")


def test_automation_suggestions():
    """Test automation tool suggestions"""
    print("\n" + "="*80)
    print("TEST 3: AUTOMATION TOOL SUGGESTIONS")
    print("="*80)
    
    test_cases = [
        "Disable lva1-vds12 from LVA1-VDS-VIP.linkedin.biz",
        "Connection timeout to 172.30.1.20 port 443",
        "Slow wifi on 10th floor"
    ]
    
    for desc in test_cases:
        print(f"\n📝 {desc}")
        suggestion = json.loads(suggest_automation_tool(desc))
        print(f"   Category: {suggestion['ticket_category']}")
        print(f"   Tools: {', '.join(suggestion['suggested_tools'])}")
        print(f"   Usage: {suggestion['usage_guide']}")
        if suggestion.get('example_call'):
            print(f"   Example: {suggestion['example_call']}")


def test_diagnostics():
    """Test diagnostic capabilities"""
    print("\n" + "="*80)
    print("TEST 4: DIAGNOSTICS")
    print("="*80)
    
    test_cases = [
        "ERR_CONNECTION_REFUSED when connecting to https://app.linkedin.com",
        "Connection timeout to 172.30.1.20 port 443",
        "Slow wifi on 10th floor",
        "DNS resolution failed for internal.linkedin.com"
    ]
    
    for desc in test_cases:
        print(f"\n🔍 {desc}")
        diag = json.loads(diagnose_connectivity_issue(desc))
        print(f"   Issues: {', '.join(diag['detected_issues'])}")
        print(f"   Likely Causes:")
        for cause in diag['likely_causes'][:3]:
            print(f"     - {cause}")
        print(f"   Diagnostic Commands:")
        for cmd in diag['diagnostic_commands'][:3]:
            print(f"     - {cmd}")


def test_a10_operations():
    """Test A10 load balancer operations"""
    print("\n" + "="*80)
    print("TEST 5: A10 LOAD BALANCER OPERATIONS")
    print("="*80)
    
    print("\n🔧 Disable VIP nodes:")
    result = json.loads(a10_disable_vip_nodes(
        "LVA1-VDS-VIP.linkedin.biz",
        "lva1-vds12,lva1-vds13,lva1-vds14"
    ))
    print(f"   Action: {result['action']}")
    print(f"   VIP: {result['vip']}")
    print(f"   Nodes: {', '.join(result['nodes'])}")
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    print(f"   Next Steps:")
    for step in result['next_steps']:
        print(f"     - {step}")


def test_nacl_validation():
    """Test NACL validation"""
    print("\n" + "="*80)
    print("TEST 6: NACL/FIREWALL VALIDATION")
    print("="*80)
    
    print("\n🔐 Validating NACL:")
    result = json.loads(validate_nacl_status(
        "172.20.1.10",
        "172.30.1.20",
        443,
        "TCP"
    ))
    print(f"   Source: {result['validation']['source_ip']}")
    print(f"   Destination: {result['validation']['dest_ip']}:{result['validation']['port']}")
    print(f"   Protocol: {result['validation']['protocol']}")
    print(f"\n   Checks to perform:")
    for check in result['checks_to_perform'][:4]:
        print(f"     {check}")
    print(f"\n   Palo Alto commands:")
    for cmd in result['palo_alto_commands']:
        print(f"     {cmd}")


def main():
    """Run all tests"""
    print("\n🤖 ONCALL AGENT - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    try:
        test_classification()
        test_entity_extraction()
        test_automation_suggestions()
        test_diagnostics()
        test_a10_operations()
        test_nacl_validation()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nThe oncall agent is ready to use!")
        print("\nNext steps:")
        print("  1. Start the MCP server: python oncall_agent.py")
        print("  2. Configure Claude Desktop with the MCP server")
        print("  3. Test with real tickets!")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

