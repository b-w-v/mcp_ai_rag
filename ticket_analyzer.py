"""
ServiceNow Ticket Analyzer for Oncall Agent
Analyzes 6 months of ticket data to categorize and build automation tools
"""

import pandas as pd
import json
import re
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path


class TicketAnalyzer:
    def __init__(self, excel_path: str):
        """
        Initialize ticket analyzer with Excel file path
        
        Args:
            excel_path: Path to Excel file with columns: 
                       ['Number', 'Short Description', 'Category', 'Assignment Group', 'Priority', 'Created', 'Resolved']
        """
        self.excel_path = excel_path
        self.df = None
        self.categories = defaultdict(list)
        self.patterns = {}
        
    def load_data(self):
        """Load ticket data from Excel or CSV"""
        try:
            # Try CSV first, then Excel
            if self.excel_path.endswith('.csv'):
                self.df = pd.read_csv(self.excel_path)
            else:
                self.df = pd.read_excel(self.excel_path)
            
            print(f"✓ Loaded {len(self.df)} tickets from {self.excel_path}")
            print(f"✓ Columns: {list(self.df.columns)}")
            return True
        except FileNotFoundError:
            print(f"✗ File not found: {self.excel_path}")
            print("\nPlease place your file in one of these locations:")
            print(f"  1. {Path.cwd()}/servicenow_tickets.xlsx")
            print(f"  2. {Path.cwd()}/servicenow_tickets.csv")
            print(f"  3. {Path.cwd()}/tickets.xlsx")
            return False
        except Exception as e:
            print(f"✗ Error loading file: {e}")
            return False
    
    def categorize_tickets(self):
        """Categorize tickets based on description patterns"""
        
        # Define categorization patterns based on your sample data
        patterns = {
            'FIREWALL_NACL': {
                'keywords': r'(?i)(NACL|firewall|allow (TCP|UDP)|port \d+|connection refused|timeout|ERR_CONNECTION|address group)',
                'subcategories': {
                    'nacl_approved_not_implemented': r'(?i)(approved|NACL).*(?:not implemented|timeout)',
                    'connection_refused': r'(?i)(ERR_CONNECTION_REFUSED|refused to connect)',
                    'connection_timeout': r'(?i)(timeout|telnet failed)',
                    'address_group': r'(?i)(address group|update.*group)',
                }
            },
            'LOAD_BALANCER_A10': {
                'keywords': r'(?i)(disable.*nodes?|enable.*nodes?|VIP|load.*balancer|\w+-vip\.linkedin\.biz)',
                'subcategories': {
                    'disable_vip_node': r'(?i)disable.*nodes?.*from.*VIP',
                    'enable_vip_node': r'(?i)enable.*nodes?.*to.*VIP',
                }
            },
            'VPN_REMOTE_ACCESS': {
                'keywords': r'(?i)(VPN|RVPN|remote access|force tunnel|vpn gateway)',
                'subcategories': {
                    'vpn_new_request': r'(?i)new (R)?VPN request',
                    'vpn_connectivity': r'(?i)unable to connect.*VPN|VPN.*not working',
                    'vpn_allowlist': r'(?i)(allowlist|whitelist).*VPN',
                }
            },
            'WIFI_WIRELESS': {
                'keywords': r'(?i)(wifi|wireless|corpnet|slow internet|cannot connect.*wifi)',
                'subcategories': {
                    'slow_wifi': r'(?i)(slow|patchy).*wifi|slow.*internet',
                    'cannot_connect': r'(?i)cannot connect.*wifi|wifi.*not working',
                    'guest_wifi': r'(?i)guest.*(internet|wifi)',
                }
            },
            'AZURE_CLOUD': {
                'keywords': r'(?i)(azure|lnkdprod|blob storage|subnet.*expand|address.*azure)',
                'subcategories': {
                    'subnet_expansion': r'(?i)subnet.*expand|need.*IP space',
                    'azure_connectivity': r'(?i)azure.*(?:deployment|connection|communication)',
                    'azure_networking': r'(?i)azure.*(NACL|firewall|private endpoint)',
                }
            },
            'SWITCH_PORT_PHYSICAL': {
                'keywords': r'(?i)(switch port|configure.*port|VLAN|fiber.*port|MAC.*add|printer)',
                'subcategories': {
                    'port_activation': r'(?i)(configure|enable|activate).*port',
                    'vlan_config': r'(?i)VLAN.*\d+',
                    'printer_mac': r'(?i)printer.*MAC|whitelist.*MAC',
                }
            },
            'DNS_DHCP_IP': {
                'keywords': r'(?i)(DNS|DHCP|IP.*reserv|subnet.*expand)',
                'subcategories': {
                    'ip_reservation': r'(?i)reserv.*IP|IP.*address.*reserv',
                    'dns_issue': r'(?i)DNS.*(?:not working|issue|resolv)',
                }
            },
            'ACCESS_PERMISSIONS': {
                'keywords': r'(?i)(access|permission|Airwave|monitor)',
                'subcategories': {
                    'tool_access': r'(?i)need access to (Airwave|monitoring)',
                }
            },
            'DATACENTER_SITE_DOWN': {
                'keywords': r'(?i)(entire site.*lost|site.*down|outage|all.*communications)',
                'subcategories': {
                    'site_outage': r'(?i)entire site|site.*down',
                }
            }
        }
        
        self.patterns = patterns
        
        # Categorize each ticket
        for idx, row in self.df.iterrows():
            # Handle different column name variations
            description = str(row.get('Short Description', row.get('Short description', row.get('Description', ''))))
            
            matched = False
            for category, config in patterns.items():
                if re.search(config['keywords'], description):
                    # Find subcategory
                    subcategory = 'other'
                    for subcat, pattern in config.get('subcategories', {}).items():
                        if re.search(pattern, description):
                            subcategory = subcat
                            break
                    
                    self.categories[category].append({
                        'ticket_number': row.get('ID', row.get('Number', row.get('Incident', 'N/A'))),
                        'description': description,
                        'subcategory': subcategory,
                        'priority': row.get('Priority', 'N/A'),
                        'assignment_group': row.get('Assignment Group', 'N/A'),
                        'created': row.get('Created', 'N/A'),
                        'resolved': row.get('Resolved', row.get('Closed', 'N/A')),
                    })
                    matched = True
                    break
            
            if not matched:
                self.categories['UNCATEGORIZED'].append({
                    'ticket_number': row.get('ID', row.get('Number', row.get('Incident', 'N/A'))),
                    'description': description,
                    'subcategory': 'unknown',
                    'priority': row.get('Priority', 'N/A'),
                    'assignment_group': row.get('Assignment Group', 'N/A'),
                })
        
        return self.categories
    
    def generate_statistics(self):
        """Generate ticket statistics by domain"""
        stats = {
            'total_tickets': len(self.df),
            'by_category': {},
            'by_priority': Counter(),
            'by_assignment_group': Counter(),
            'automation_potential': {},
        }
        
        for category, tickets in self.categories.items():
            stats['by_category'][category] = {
                'count': len(tickets),
                'percentage': round(len(tickets) / len(self.df) * 100, 2),
                'subcategories': Counter([t['subcategory'] for t in tickets])
            }
            
            # Count priorities and assignment groups
            for ticket in tickets:
                stats['by_priority'][ticket.get('priority', 'N/A')] += 1
                stats['by_assignment_group'][ticket.get('assignment_group', 'N/A')] += 1
        
        # Determine automation potential
        automation_high = ['LOAD_BALANCER_A10', 'SWITCH_PORT_PHYSICAL', 'DNS_DHCP_IP']
        automation_medium = ['FIREWALL_NACL', 'VPN_REMOTE_ACCESS', 'AZURE_CLOUD']
        
        for category in self.categories.keys():
            if category in automation_high:
                stats['automation_potential'][category] = 'HIGH - Fully automatable'
            elif category in automation_medium:
                stats['automation_potential'][category] = 'MEDIUM - Semi-automatable with validation'
            else:
                stats['automation_potential'][category] = 'LOW - Requires manual intervention'
        
        return stats
    
    def generate_report(self, output_path='ticket_analysis_report.json'):
        """Generate comprehensive analysis report"""
        stats = self.generate_statistics()
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'data_source': self.excel_path,
            'summary': {
                'total_tickets': stats['total_tickets'],
                'categories_found': len(self.categories),
                'top_categories': sorted(
                    stats['by_category'].items(), 
                    key=lambda x: x[1]['count'], 
                    reverse=True
                )[:5]
            },
            'category_breakdown': stats['by_category'],
            'priority_distribution': dict(stats['by_priority']),
            'assignment_groups': dict(stats['by_assignment_group']),
            'automation_potential': stats['automation_potential'],
            'sample_tickets_by_category': {
                cat: tickets[:3] for cat, tickets in self.categories.items()
            }
        }
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n✓ Report saved to: {output_path}")
        return report
    
    def print_summary(self):
        """Print summary to console"""
        stats = self.generate_statistics()
        
        print("\n" + "="*80)
        print("SERVICENOW TICKET ANALYSIS - ONCALL AGENT")
        print("="*80)
        
        print(f"\n📊 TOTAL TICKETS: {stats['total_tickets']}")
        
        print("\n📁 BREAKDOWN BY CATEGORY:")
        print("-" * 80)
        for category, data in sorted(stats['by_category'].items(), key=lambda x: x[1]['count'], reverse=True):
            count = data['count']
            pct = data['percentage']
            print(f"  {category:30s} {count:5d} tickets ({pct:5.1f}%)")
            
            # Print subcategories
            for subcat, subcount in data['subcategories'].most_common(3):
                print(f"    ├─ {subcat:35s} {subcount:4d} tickets")
        
        print("\n🔧 AUTOMATION POTENTIAL:")
        print("-" * 80)
        for category, potential in stats['automation_potential'].items():
            if category in stats['by_category']:
                count = stats['by_category'][category]['count']
                print(f"  {category:30s} {count:5d} tickets - {potential}")
        
        print("\n⚡ PRIORITY DISTRIBUTION:")
        print("-" * 80)
        for priority, count in stats['by_priority'].most_common():
            pct = round(count / stats['total_tickets'] * 100, 1)
            print(f"  {str(priority):15s} {count:5d} tickets ({pct:5.1f}%)")
        
        print("\n👥 TOP ASSIGNMENT GROUPS:")
        print("-" * 80)
        for group, count in stats['by_assignment_group'].most_common(10):
            pct = round(count / stats['total_tickets'] * 100, 1)
            print(f"  {str(group):40s} {count:5d} tickets ({pct:5.1f}%)")
        
        print("\n" + "="*80)
    
    def generate_knowledge_base(self, output_dir='knowledge_base'):
        """Generate knowledge base files for oncall agent"""
        kb_path = Path(output_dir)
        kb_path.mkdir(exist_ok=True)
        
        # Generate category-specific knowledge bases
        for category, tickets in self.categories.items():
            category_file = kb_path / f"{category.lower()}_patterns.json"
            
            # Extract common patterns
            descriptions = [t['description'] for t in tickets]
            subcategories = Counter([t['subcategory'] for t in tickets])
            
            kb_data = {
                'category': category,
                'total_tickets': len(tickets),
                'subcategories': dict(subcategories),
                'common_keywords': self._extract_keywords(descriptions),
                'sample_descriptions': descriptions[:10],
                'automation_tools': self._suggest_tools(category),
                'resolution_steps': self._generate_resolution_steps(category)
            }
            
            with open(category_file, 'w') as f:
                json.dump(kb_data, f, indent=2)
        
        print(f"\n✓ Knowledge base generated in: {output_dir}/")
        
    def _extract_keywords(self, descriptions):
        """Extract common keywords from descriptions"""
        # Simple keyword extraction
        common_words = ['the', 'to', 'from', 'and', 'for', 'in', 'on', 'is', 'are', 'a', 'an']
        words = []
        for desc in descriptions:
            words.extend(re.findall(r'\b\w+\b', desc.lower()))
        
        word_freq = Counter([w for w in words if w not in common_words and len(w) > 3])
        return dict(word_freq.most_common(20))
    
    def _suggest_tools(self, category):
        """Suggest automation tools for each category"""
        tools = {
            'FIREWALL_NACL': [
                'nacl_validator - Validate NACL ticket status',
                'palo_alto_policy_checker - Check firewall rules',
                'connectivity_tester - Test TCP/UDP connectivity',
                'kumo_api_integration - Query NACL status'
            ],
            'LOAD_BALANCER_A10': [
                'a10_vip_manager - Enable/disable VIP nodes',
                'a10_health_checker - Check node health',
                'a10_config_backup - Backup before changes',
                'vip_status_monitor - Monitor VIP status'
            ],
            'VPN_REMOTE_ACCESS': [
                'vpn_provisioner - Create VPN accounts',
                'vpn_allowlist_manager - Manage allowed domains',
                'vpn_connectivity_tester - Test VPN connectivity'
            ],
            'WIFI_WIRELESS': [
                'airwave_ap_checker - Check AP status',
                'wifi_signal_analyzer - Analyze signal strength',
                'client_troubleshooter - Diagnose client issues'
            ],
            'AZURE_CLOUD': [
                'azure_subnet_expander - Expand subnets',
                'azure_address_group_manager - Manage address groups',
                'azure_connectivity_tester - Test Azure connectivity'
            ],
            'SWITCH_PORT_PHYSICAL': [
                'port_configurator - Configure switch ports',
                'vlan_manager - Manage VLAN assignments',
                'mac_whitelist_manager - Whitelist MAC addresses'
            ],
            'DNS_DHCP_IP': [
                'ip_reservator - Reserve IP addresses',
                'dns_manager - Manage DNS records',
                'dhcp_scope_manager - Manage DHCP scopes'
            ]
        }
        return tools.get(category, ['Manual intervention required'])
    
    def _generate_resolution_steps(self, category):
        """Generate resolution steps for each category"""
        steps = {
            'FIREWALL_NACL': [
                '1. Extract source IP, destination IP, port, protocol',
                '2. Query Kumo for NACL ticket status',
                '3. Check Palo Alto for implemented rule',
                '4. Test connectivity with telnet/nc',
                '5. If timeout, check routing and destination',
                '6. Update ticket with findings'
            ],
            'LOAD_BALANCER_A10': [
                '1. Parse VIP name and node list',
                '2. Validate VIP exists in A10',
                '3. Execute disable/enable via A10 API',
                '4. Verify node status',
                '5. Update ticket with confirmation',
                '6. Create reminder for re-enable if needed'
            ],
            'VPN_REMOTE_ACCESS': [
                '1. Validate requester authorization',
                '2. Create VPN account in system',
                '3. Add domains to allowlist if needed',
                '4. Test VPN connectivity',
                '5. Send credentials to user',
                '6. Close ticket'
            ],
            'WIFI_WIRELESS': [
                '1. Identify location (office, floor)',
                '2. Check AP status in Airwave',
                '3. Check client device logs',
                '4. Test signal strength at location',
                '5. Escalate if AP issue found',
                '6. Provide workaround to user'
            ]
        }
        return steps.get(category, ['Manual troubleshooting required'])


def main():
    """Main function to run ticket analysis"""
    
    # Try multiple possible file locations (CSV and Excel)
    possible_paths = [
        'servicenow_tickets.csv',
        'servicenow_tickets.xlsx',
        'tickets.xlsx',
        'tickets.csv',
        'snow_export.xlsx',
        '../servicenow_tickets.csv',
        '../servicenow_tickets.xlsx',
        '../tickets.xlsx',
    ]
    
    excel_path = None
    for path in possible_paths:
        if Path(path).exists():
            excel_path = path
            break
    
    if not excel_path:
        print("📋 ServiceNow Ticket Analyzer - Oncall Agent")
        print("="*80)
        print("\n⚠️  No Excel file found!")
        print("\nTo use this analyzer:")
        print("1. Export your ServiceNow tickets to Excel")
        print("2. Required columns: Number, Short Description, Category, Priority, Assignment Group, Created, Resolved")
        print("3. Save the file as 'servicenow_tickets.xlsx' in this directory:")
        print(f"   {Path.cwd()}")
        print("\n4. Run this script again: python ticket_analyzer.py")
        print("\n" + "="*80)
        return
    
    # Analyze tickets
    analyzer = TicketAnalyzer(excel_path)
    
    if not analyzer.load_data():
        return
    
    print("\n🔍 Analyzing tickets...")
    analyzer.categorize_tickets()
    
    print("\n📊 Generating statistics...")
    analyzer.print_summary()
    
    print("\n💾 Generating reports...")
    analyzer.generate_report()
    analyzer.generate_knowledge_base()
    
    print("\n✅ Analysis complete!")
    print("\nNext steps:")
    print("1. Review: ticket_analysis_report.json")
    print("2. Review: knowledge_base/ directory")
    print("3. Use generated knowledge bases to build MCP tools")
    print("4. Deploy oncall agent with automation capabilities")


if __name__ == "__main__":
    main()

