from mcp.server.fastmcp import FastMCP
from netmiko import ConnectHandler
from device_inventory import devices

# Create an MCP server
mcp = FastMCP("NetworkDeviceController")

# Load the device inventory
from device_inventory import devices


def get_credentials(hostname):
    return devices[hostname]


def connect_and_run(ip, username, password, command):
    device = {
        "device_type": "cisco_xr",
        "host": ip,
        "username": username,
        "password": password,
        "port": 22,
        "timeout": 30,
        "session_timeout": 60,
        "banner_timeout": 30,
        "conn_timeout": 30
    }
    try:
        with ConnectHandler(**device) as net_connect:
            output = net_connect.send_command(command, read_timeout=60)
            return output
    except Exception as e:
        return f"Error connecting to device {ip}: {str(e)}"



#print(d1)

@mcp.tool()
def show_version(device_name: str) -> str:
    """Show version information for a network device"""
    if device_name not in devices:
        return f"Device '{device_name}' not found in inventory. Available devices: {list(devices.keys())}"
    
    device_info = get_credentials(device_name)
    return connect_and_run(device_info["ip"], device_info["username"], device_info["password"], "show version")

@mcp.tool()
def show_interfaces(device_name: str) -> str:
    """Show interface information for a network device"""
    if device_name not in devices:
        return f"Device '{device_name}' not found in inventory. Available devices: {list(devices.keys())}"
    
    device_info = get_credentials(device_name)
    return connect_and_run(device_info["ip"], device_info["username"], device_info["password"], "show interfaces")

@mcp.tool()
def run_command(device_name: str, command: str) -> str:
    """Run a custom command on a network device"""
    if device_name not in devices:
        return f"Device '{device_name}' not found in inventory. Available devices: {list(devices.keys())}"
    
    device_info = get_credentials(device_name)
    return connect_and_run(device_info["ip"], device_info["username"], device_info["password"], command)

@mcp.tool()
def list_devices() -> str:
    """List all available network devices in the inventory"""
    if not devices:
        return "No devices configured in inventory."
    
    result = []
    for name, info in devices.items():
        result.append(f"Device: {name}")
        result.append(f"  IP: {info['ip']}")
        result.append(f"  Type: {info['device_type']}")
        result.append("")
    
    return "\n".join(result)

if __name__ == "__main__":
    mcp.run()

