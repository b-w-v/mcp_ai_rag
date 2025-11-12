# Network Troubleshooting Tips

## Interface Issues

### Interface Down
1. Check physical layer: `show interfaces [interface-name]`
2. Look for errors, CRC, or collisions in output
3. Verify cable connections
4. Check for shutdown state: `show running-config interface [interface-name]`
5. Review interface counters: `show controllers [interface-name]`

### High Interface Errors
- Check for duplex mismatches
- Verify cable quality
- Look for excessive broadcasts: `show interfaces | include broadcast`
- Check for buffer drops: `show interfaces | include drops`

## Routing Issues

### Routes Not Learning
1. Verify routing protocol is enabled: `show run router [bgp|ospf|isis]`
2. Check neighbor relationships: `show bgp summary` or `show ospf neighbor`
3. Verify network statements and redistribution
4. Check route filters and prefix-lists
5. Verify authentication if configured

### BGP Neighbor Down
1. Check TCP connectivity: `ping [neighbor-ip]`
2. Verify BGP is configured: `show run router bgp`
3. Check neighbor state: `show bgp summary`
4. Review BGP logs: `show logging | include BGP`
5. Verify correct AS numbers
6. Check for route-map or filter-list blocking

## Performance Issues

### High CPU Usage
1. Identify process: `show processes cpu | include CPU`
2. Check for routing instability: `show logging | include ROUTING`
3. Look for excessive logging: `show logging`
4. Verify no loops in network topology

### High Memory Usage
1. Check memory: `show memory summary`
2. Review route table size: `show route summary`
3. Check for memory leaks: `show memory compare start` and `show memory compare end`

## Connectivity Issues

### Cannot Ping Remote Host
1. Verify local interface status: `show ip interface brief`
2. Check routing table: `show route [destination]`
3. Verify ARP entry: `show arp [next-hop-ip]`
4. Check access-lists: `show access-lists`
5. Trace route: `traceroute [destination]`

### Packet Loss
1. Check interface errors: `show interfaces | include error`
2. Review QoS drops: `show policy-map interface [interface-name]`
3. Check for congestion: `show interfaces | include queue`
4. Verify MTU settings: `show interfaces [interface-name] | include MTU`
