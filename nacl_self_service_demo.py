#!/usr/bin/env python3
"""
NACL/Firewall Self-Service Tool - Demo Prototype
Demonstrates how users can self-diagnose connectivity issues
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple


class NACLSelfServiceTool:
    """Self-service tool for NACL/Firewall diagnostics"""
    
    def __init__(self):
        # Load patterns from analysis
        self.nacl_patterns = self._load_patterns()
        
    def _load_patterns(self):
        """Load NACL patterns from analysis"""
        return {
            'connection_refused': r'(?i)(refused|ERR_CONNECTION_REFUSED)',
            'timeout': r'(?i)(timeout|timed out)',
            'cannot_reach': r'(?i)(cannot reach|can\'t reach)',
            'nacl_missing': r'(?i)(NACL.*not.*found|no.*NACL)',
        }
    
    def check_connectivity(self, source_ip: str, destination: str, port: int, 
                          protocol: str = "TCP") -> Dict:
        """
        Main self-service function: Check connectivity and diagnose issues
        
        This is what users interact with via web/CLI/Slack
        """
        
        print(f"\n{'='*70}")
        print(f"🔍 NACL/FIREWALL CONNECTIVITY CHECK")
        print(f"{'='*70}\n")
        
        print(f"Checking connectivity from {source_ip} to {destination}:{port}/{protocol}")
        print()
        
        # Step 1: DNS Resolution
        dns_result = self._check_dns(destination)
        self._print_check("DNS Resolution", dns_result['status'], dns_result['message'])
        
        # Step 2: Routing
        routing_result = self._check_routing(source_ip, dns_result.get('resolved_ip', destination))
        self._print_check("Routing Check", routing_result['status'], routing_result['message'])
        
        # Step 3: NACL Status
        nacl_result = self._check_nacl(source_ip, destination, port, protocol)
        self._print_check("NACL Status", nacl_result['status'], nacl_result['message'])
        
        # Step 4: Firewall Rule
        firewall_result = self._check_firewall(source_ip, destination, port, protocol)
        self._print_check("Firewall Rule", firewall_result['status'], firewall_result['message'])
        
        # Step 5: Port Test
        port_result = self._test_port(destination, port)
        self._print_check("Port Test", port_result['status'], port_result['message'])
        
        # Diagnosis
        diagnosis = self._diagnose(dns_result, routing_result, nacl_result, 
                                   firewall_result, port_result)
        
        # Print results
        print(f"\n{'='*70}")
        print(f"📊 DIAGNOSIS RESULTS")
        print(f"{'='*70}\n")
        
        status_icon = {
            'working': '✅',
            'blocked': '❌',
            'warning': '⚠️'
        }.get(diagnosis['status'], '❓')
        
        print(f"Overall Status: {status_icon} {diagnosis['status'].upper()}")
        print(f"\nRoot Cause: {diagnosis['root_cause']}")
        print(f"\n{diagnosis['explanation']}")
        
        # Recommendations
        print(f"\n{'='*70}")
        print(f"💡 RECOMMENDED ACTIONS")
        print(f"{'='*70}\n")
        
        for i, action in enumerate(diagnosis['recommended_actions'], 1):
            print(f"{i}. {action}")
        
        # Self-service options
        print(f"\n{'='*70}")
        print(f"🛠️  SELF-SERVICE OPTIONS")
        print(f"{'='*70}\n")
        
        for option in diagnosis['self_service_options']:
            print(f"  • {option}")
        
        print(f"\n{'='*70}\n")
        
        return diagnosis
    
    def _check_dns(self, destination: str) -> Dict:
        """Check DNS resolution"""
        # In real implementation, this would do actual DNS lookup
        if destination.replace('.', '').replace('-', '').isalnum():
            # Looks like hostname
            return {
                'status': 'pass',
                'message': f'Resolved to 172.30.1.20',
                'resolved_ip': '172.30.1.20'
            }
        else:
            return {
                'status': 'pass',
                'message': 'IP address provided, no DNS needed',
                'resolved_ip': destination
            }
    
    def _check_routing(self, source: str, destination: str) -> Dict:
        """Check if routing exists"""
        # In real implementation, this would check routing tables
        return {
            'status': 'pass',
            'message': f'Route exists via 10.0.0.1',
            'next_hop': '10.0.0.1'
        }
    
    def _check_nacl(self, source: str, destination: str, port: int, 
                    protocol: str) -> Dict:
        """Check NACL ticket status in Kumo"""
        # In real implementation, this would query Kumo API
        # For demo, simulate different scenarios
        
        # Simulate: NACL not found
        return {
            'status': 'fail',
            'message': 'No NACL ticket found for this connection',
            'kumo_ticket': None
        }
        
        # Other scenarios:
        # return {'status': 'pass', 'message': 'NACL exists: KUMO-12345', 'kumo_ticket': 'KUMO-12345'}
        # return {'status': 'warning', 'message': 'NACL approved but not implemented', 'kumo_ticket': 'KUMO-12345'}
    
    def _check_firewall(self, source: str, destination: str, port: int, 
                       protocol: str) -> Dict:
        """Check Palo Alto firewall rule"""
        # In real implementation, this would query Palo Alto API
        return {
            'status': 'fail',
            'message': 'No firewall rule found',
            'rule_name': None
        }
    
    def _test_port(self, destination: str, port: int) -> Dict:
        """Test if port is reachable"""
        # In real implementation, this would do telnet/nc test
        return {
            'status': 'fail',
            'message': f'Connection to port {port} failed',
            'error': 'Connection refused'
        }
    
    def _diagnose(self, dns, routing, nacl, firewall, port_test) -> Dict:
        """Diagnose the issue based on check results"""
        
        # All checks passed
        if all(check['status'] == 'pass' for check in [dns, routing, nacl, firewall, port_test]):
            return {
                'status': 'working',
                'root_cause': 'Connection is working',
                'explanation': 'All checks passed. The connection should be functional.',
                'recommended_actions': [
                    'Connection is working properly',
                    'If you\'re still experiencing issues, check application layer'
                ],
                'self_service_options': [
                    'No action needed - connectivity is OK'
                ]
            }
        
        # NACL missing - most common issue (from your 79 ticket analysis)
        if nacl['status'] == 'fail':
            return {
                'status': 'blocked',
                'root_cause': 'NACL ticket missing',
                'explanation': (
                    'No NACL ticket exists for this connection. '
                    'This is the most common cause of connectivity issues (found in 37% of cases). '
                    'You need to create a NACL request in Kumo system.'
                ),
                'recommended_actions': [
                    'Create NACL request (can be done immediately)',
                    'Expected resolution time: 2-4 hours',
                    'For urgent issues: Contact #network-ops on Slack'
                ],
                'self_service_options': [
                    '🚀 Create NACL Request Now (Auto-generated form)',
                    '📊 Check existing NACL tickets',
                    '💬 Get help in Slack: #network-ops',
                    '📧 Email: network-ops@linkedin.com'
                ],
                'create_nacl_url': 'https://kumo.corp.linkedin.com/nacl-request/new',
                'estimated_resolution': '2-4 hours'
            }
        
        # NACL approved but not implemented
        if nacl['status'] == 'warning':
            return {
                'status': 'warning',
                'root_cause': 'NACL approved but not implemented',
                'explanation': (
                    f'NACL ticket {nacl.get("kumo_ticket")} is approved but not yet '
                    'implemented in Palo Alto firewall. This represents a process gap '
                    'between Kumo and firewall implementation (found in 8% of cases).'
                ),
                'recommended_actions': [
                    f'Check implementation status: {nacl.get("kumo_ticket")}',
                    'Escalate to firewall team if delayed >4 hours',
                    'Typical implementation time: 30 minutes after approval'
                ],
                'self_service_options': [
                    f'📊 Track NACL status: {nacl.get("kumo_ticket")}',
                    '⚡ Escalate if delayed (automated)',
                    '🔔 Enable notifications for updates'
                ]
            }
        
        # Firewall blocking
        if firewall['status'] == 'fail' and nacl['status'] == 'pass':
            return {
                'status': 'blocked',
                'root_cause': 'Firewall rule missing or misconfigured',
                'explanation': (
                    f'NACL exists ({nacl.get("kumo_ticket")}) but firewall rule is missing. '
                    'This indicates implementation issue.'
                ),
                'recommended_actions': [
                    'Verify NACL implementation in Palo Alto',
                    'Check if rule was recently added (may need time to propagate)',
                    'Contact firewall team if NACL is old'
                ],
                'self_service_options': [
                    '🔍 Verify firewall rule implementation',
                    '📞 Auto-escalate to firewall team',
                    '⏱️  Check implementation timeline'
                ]
            }
        
        # Destination not responding
        if all(check['status'] in ['pass', 'warning'] for check in [dns, routing, nacl, firewall]) and port_test['status'] == 'fail':
            return {
                'status': 'warning',
                'root_cause': 'Destination service not responding',
                'explanation': (
                    'Network connectivity is OK (NACL and firewall rules exist), '
                    'but the destination service is not responding. '
                    'This is an application-layer issue, not network.'
                ),
                'recommended_actions': [
                    'Verify the destination service is running',
                    'Check if correct port number',
                    'Contact application team for destination service'
                ],
                'self_service_options': [
                    '🔍 Check service status (if monitoring available)',
                    '📧 Contact service owner',
                    '📝 Create application support ticket'
                ]
            }
        
        # Generic failure
        return {
            'status': 'blocked',
            'root_cause': 'Multiple issues detected',
            'explanation': 'Multiple checks failed. Manual investigation needed.',
            'recommended_actions': [
                'Create ServiceNow ticket with diagnostic details',
                'Contact network operations team'
            ],
            'self_service_options': [
                '🎫 Create ServiceNow ticket (auto-filled)',
                '💬 Chat with network ops'
            ]
        }
    
    def _print_check(self, check_name: str, status: str, message: str):
        """Print check result with formatting"""
        icons = {
            'pass': '✅',
            'fail': '❌',
            'warning': '⚠️'
        }
        icon = icons.get(status, '❓')
        print(f"{icon} {check_name:20s} {message}")
    
    def check_nacl_status(self, kumo_ticket: str) -> Dict:
        """Check status of existing NACL ticket"""
        print(f"\n{'='*70}")
        print(f"📊 NACL TICKET STATUS")
        print(f"{'='*70}\n")
        
        print(f"Kumo Ticket: {kumo_ticket}")
        print()
        
        # Simulate Kumo API response
        # In real implementation, this would query Kumo API
        status = {
            'kumo_ticket': kumo_ticket,
            'status': 'implemented',
            'created': '2024-11-15T10:00:00Z',
            'approved': '2024-11-15T14:30:00Z',
            'implemented': '2024-11-15T16:15:00Z',
            'tested': '2024-11-15T16:20:00Z',
            'details': {
                'source': '172.20.0.0/16',
                'destination': '172.30.1.20',
                'port': 443,
                'protocol': 'TCP',
                'firewall_rule': 'FW-BIZ-PROD-443'
            },
            'ready_to_use': True
        }
        
        # Print timeline
        print("Timeline:")
        print(f"  ✅ Created:      {status['created']}")
        print(f"  ✅ Approved:     {status['approved']}")
        print(f"  ✅ Implemented:  {status['implemented']}")
        print(f"  ✅ Tested:       {status['tested']}")
        print()
        
        # Print details
        print("Details:")
        print(f"  Source:      {status['details']['source']}")
        print(f"  Destination: {status['details']['destination']}")
        print(f"  Port:        {status['details']['port']}")
        print(f"  Protocol:    {status['details']['protocol']}")
        print(f"  FW Rule:     {status['details']['firewall_rule']}")
        print()
        
        if status['ready_to_use']:
            print("✅ Status: READY TO USE")
        else:
            print("⏳ Status: IN PROGRESS")
        
        print(f"\n{'='*70}\n")
        
        return status
    
    def create_nacl_request(self, source: str, destination: str, port: int,
                           protocol: str, justification: str) -> Dict:
        """Create new NACL request"""
        print(f"\n{'='*70}")
        print(f"🚀 CREATING NACL REQUEST")
        print(f"{'='*70}\n")
        
        # Validation
        print("Validating request...")
        print("  ✅ Source IP format: OK")
        print("  ✅ Destination format: OK")
        print("  ✅ Port number: OK")
        print("  ✅ Protocol: OK")
        print()
        
        # Check auto-approval eligibility
        auto_approve = self._check_auto_approval(port, protocol)
        
        if auto_approve:
            print("✅ Request qualifies for AUTO-APPROVAL")
            approval_status = "auto_approved"
            estimated_time = "15-30 minutes"
        else:
            print("⏳ Request requires MANAGER APPROVAL")
            approval_status = "pending_approval"
            estimated_time = "2-4 hours"
        
        print()
        
        # Create Kumo ticket (simulated)
        kumo_ticket = f"KUMO-{hash(datetime.now()) % 100000}"
        
        result = {
            'status': 'created',
            'kumo_ticket': kumo_ticket,
            'approval_status': approval_status,
            'estimated_time': estimated_time,
            'details': {
                'source': source,
                'destination': destination,
                'port': port,
                'protocol': protocol,
                'justification': justification
            }
        }
        
        print(f"✅ NACL Request Created Successfully!")
        print()
        print(f"Kumo Ticket: {kumo_ticket}")
        print(f"Status: {approval_status}")
        print(f"Estimated Implementation: {estimated_time}")
        print()
        print(f"Track status: nacl-cli status {kumo_ticket}")
        print(f"Or visit: https://kumo.corp.linkedin.com/nacl-request/{kumo_ticket}")
        
        print(f"\n{'='*70}\n")
        
        return result
    
    def _check_auto_approval(self, port: int, protocol: str) -> bool:
        """Check if request qualifies for auto-approval"""
        # Standard ports that can be auto-approved
        auto_approve_ports = {
            'web': [80, 443, 8080, 8443],
            'database': [3306, 5432, 1433, 27017],
            'api': [8000, 9000, 5000]
        }
        
        all_auto_ports = []
        for ports in auto_approve_ports.values():
            all_auto_ports.extend(ports)
        
        return port in all_auto_ports


def demo_scenario_1():
    """Demo: User can't connect to API"""
    tool = NACLSelfServiceTool()
    
    print("\n" + "="*70)
    print("DEMO SCENARIO 1: Developer Can't Connect to Production API")
    print("="*70)
    
    result = tool.check_connectivity(
        source_ip="172.20.1.10",
        destination="api.linkedin.com",
        port=443,
        protocol="TCP"
    )
    
    # If NACL missing, offer to create request
    if 'create_nacl_url' in result:
        print("Would you like to create NACL request now? (In real tool: click button)")
        print()
        input("Press Enter to create NACL request...")
        
        tool.create_nacl_request(
            source="172.20.1.10",
            destination="api.linkedin.com",
            port=443,
            protocol="TCP",
            justification="Production API access for new microservice"
        )


def demo_scenario_2():
    """Demo: Check NACL status"""
    tool = NACLSelfServiceTool()
    
    print("\n" + "="*70)
    print("DEMO SCENARIO 2: Check Status of Existing NACL Request")
    print("="*70)
    
    tool.check_nacl_status("KUMO-12345")


def main():
    """Run demo scenarios"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        NACL/FIREWALL SELF-SERVICE TOOL - DEMO                   ║
║                                                                  ║
║  This demonstrates how users can self-diagnose and resolve      ║
║  connectivity issues WITHOUT filing ServiceNow tickets          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print("\nSelect demo scenario:")
    print("1. Check connectivity (connection blocked - need NACL)")
    print("2. Check NACL status (already requested)")
    print("3. Both scenarios")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        demo_scenario_1()
    elif choice == "2":
        demo_scenario_2()
    elif choice == "3":
        demo_scenario_1()
        input("\nPress Enter for next scenario...")
        demo_scenario_2()
    else:
        print("Running all scenarios...")
        demo_scenario_1()
        demo_scenario_2()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print()
    print("In production, this would be available as:")
    print("  • Web portal: https://go/nacl-check")
    print("  • Slack bot: @nacl-helper")
    print("  • CLI: nacl-cli check ...")
    print("  • API: POST /api/v1/check-connectivity")
    print()
    print("Based on your 79 NACL tickets with 100% categorization!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

