from genie.testbed import load

# Load the testbed
testbed = load('testbed.yaml')

# Define device-specific configurations
device_configs = {
    'R10': {
        'interface_ip': '192.168.9.1',
        'subnet_mask': '255.255.255.0',
        'ospf_id': '1.1.1.1',
    },
    'R11': {
        'interface_ip': '192.168.9.2',
        'subnet_mask': '255.255.255.0',
        'ospf_id': '2.2.2.2',
    },
}


def configure_interface(device, config):
    """Configure the Ethernet interface."""
    commands = [
        f"interface Ethernet0/1",
        f"ip address {config['interface_ip']} {config['subnet_mask']}",
        "no shutdown",
        "exit",
    ]
    device.configure(commands)
    print(f"--- Interface Configuration Complete on {device.name} ---")


def configure_ospf(device, config):
    """Configure OSPF settings."""
    commands = [
        "router ospf 1",
        f"router-id {config['ospf_id']}",
        "network 192.168.9.0 0.0.0.255 area 0",
        "exit",
    ]
    device.configure(commands)
    print(f"--- OSPF Configuration Complete on {device.name} ---")


def verify_configuration(device):
    """Verify configurations using Genie parsers."""
    # Verify interface configuration
    print(f"\n--- Verifying Interface Configuration on {device.name} ---")
    interface_data = device.parse("show ip interface brief")
    for interface, details in interface_data.get("interface", {}).items():
        print(f"{interface}: {details}")

    # Verify OSPF configuration
    print(f"\n--- Verifying OSPF Configuration on {device.name} ---")
    ospf_data = device.parse("show ip ospf database")
    print(ospf_data)


# Main Execution
for device_name, config in device_configs.items():
    device = testbed.devices[device_name]
    print(f"\n--- Connecting to {device_name} ---")
    device.connect()

    # Display version information
    print(f"\n--- Device Information for {device_name} ---")
    version_info = device.parse("show version")
    print(version_info)

    # Apply configurations
    configure_interface(device, config)
    configure_ospf(device, config)

    # Verify configurations
    verify_configuration(device)

    # Disconnect from the device
    device.disconnect()
    print(f"\n--- Disconnected from {device.name} ---")

print("\n--- Configuration and Verification Complete for All Devices ---")

