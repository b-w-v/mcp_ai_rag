# Network Device Health Check Runbook

## Pre-Check Information
- Device Name: [Router/Switch Name]
- Management IP: [IP Address]
- Device Role: [Core/Edge/Access]
- Check Date: [Date]
- Performed By: [Name]

## 1. Basic Connectivity Check
```
ping [device-ip]
```
Expected: 100% reachability

## 2. System Health

### Check System Version
```
show version
```
Verify:
- Software version is current
- System uptime (no unexpected reboots)
- Last reload reason

### Check Memory Usage
```
show memory summary
```
Expected:
- Used memory < 80%
- No memory allocation failures

### Check CPU Usage
```
show processes cpu
```
Expected:
- Average CPU < 75%
- No single process consuming > 50%

## 3. Interface Status

### Check All Interfaces
```
show interfaces summary
show ip interface brief
```
Verify:
- Expected interfaces are up
- No unexpected down interfaces
- IP addresses are correct

### Check Interface Errors
```
show interfaces | include error|drop|CRC
```
Expected:
- No increasing error counters
- CRC errors = 0
- Input/output drops < 0.1%

## 4. Routing Protocol Health

### BGP (if applicable)
```
show bgp summary
show bgp ipv4 unicast summary
```
Verify:
- All expected neighbors are Established
- Route counts are within expected range
- No flapping neighbors (check uptime)

### OSPF (if applicable)
```
show ospf neighbor
show ospf interface brief
```
Verify:
- All neighbors in FULL state
- No stuck neighbors in EXSTART or EXCHANGE

### ISIS (if applicable)
```
show isis neighbors
show isis summary
```
Verify:
- All adjacencies are UP
- Correct level of adjacency

## 5. Configuration Backup

### Verify Last Configuration Save
```
show configuration commit list
```
Check:
- Recent commits are documented
- No uncommitted changes

### Check for Alarms
```
show alarms
```
Expected:
- No critical alarms
- Document any warnings

## 6. Logging Review

### Check Recent Logs
```
show logging last 50
```
Look for:
- Critical or error messages
- Interface flaps
- Protocol state changes
- Authentication failures

## 7. Environmental (if supported)

### Check Temperature and Power
```
show environment temperature
show environment power
```
Verify:
- Temperatures within normal range
- All power supplies operational
- Fan status OK

## Post-Check Actions

### If Issues Found
1. Document all issues in ticket system
2. Escalate critical issues immediately
3. Schedule maintenance for warnings
4. Update device monitoring thresholds if needed

### If All Clear
1. Document successful health check
2. Update device inventory
3. Schedule next health check
4. Archive check results

## Common Issues and Quick Fixes

### High CPU
- Identify offending process: `show processes cpu sorted`
- Check for routing instability
- Review logging level (may need to reduce)

### Interface Flapping
- Check physical connections
- Verify duplex settings
- Review error counters
- Check for bad SFP/cable

### Memory Leak
- Identify process: `show memory compare`
- Check known bugs for software version
- Plan reload during maintenance window if needed

### BGP Neighbor Down
- Verify physical connectivity: `ping [neighbor]`
- Check BGP configuration
- Review logs for reason
- Verify no ACLs blocking port 179
