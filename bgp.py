from pyats.topology import loader

# Load the testbed
tb = loader.load('testbed.yaml')

# Define device-specific configurations
device_configs = {
    'R2': {
        'interface_ip': '192.168.1.1',
        'subnet_mask': '255.255.255.0',
        'ospf_id': '2.2.2.2',
        'bgp_router_id': '10.1.1.1',
    },
    'R3': {
        'interface_ip': '192.168.1.2',
        'subnet_mask': '255.255.255.0',
        'ospf_id': '1.1.1.1',
        'bgp_router_id': '10.1.1.2',
    },
}


def configure_segment_routing(device):
    """Enable Segment Routing globally."""
    commands = [
        "segment-routing",
        "commit",
    ]
    device.configure(commands)
    print(f"\n--- Segment Routing Enabled on {device.name} ---")


def configure_interface(device, config):
    """Configure the interface."""
    commands = [
        "interface Ethernet0/3",
        f"ipv4 address {config['interface_ip']} {config['subnet_mask']}",
        "no shutdown",
        "exit",
        "commit",
    ]
    device.configure(commands)
    print(f"\n--- Interface Configuration Complete on {device.name} ---")


def configure_control_plane(device):
    """Configure control-plane and management-plane."""
    commands = [
        "control-plane",
        "management-plane",
        "inband interface all allow all",
        "exit",
        "exit",
        "commit",
    ]
    device.configure(commands)
    print(f"\n--- Control Plane Configuration Complete on {device.name} ---")


def configure_ospf(device, config):
    """Configure OSPF settings."""
    commands = [
        "router ospf 1",
        f"router-id {config['ospf_id']}",
        "address-family ipv4 unicast",
        "area 0",
        "interface GigabitEthernet0/0/0/2",
        "network point-to-point",
        "exit",
        "segment-routing mpls",
        "area 0",
        "interface loopback 0",
        "prefix-sid index 1",
        "exit",
        "commit",
    ]
    device.configure(commands)
    print(f"\n--- OSPF Configuration Complete on {device.name} ---")


def configure_bgp(device, config):
    """Configure BGP settings."""
    commands = [
        "router bgp 1",
        f"bgp router-id {config['bgp_router_id']}",
        "address-family ipv4 unicast",
        f"neighbor {config['interface_ip']} remote-as 1",
        "address-family ipv4 unicast",
        "commit",
    ]
    device.configure(commands)
    print(f"\n--- BGP Configuration Complete on {device.name} ---")


#def configure_SRPolicy(device, config):
#    """Configure Segment Routing Policy."""
#   commands = [
#       "mpls traffic-eng",
#       "policy my-sr-te-policy",
 #       "color 10",
  #      "end-point ipv4 3.3.3.3",
   #     "candidate-paths",
    #    "preference 100",
     #   f"explicit index 10 next-hop ipv4 {config['interface_ip']}",
      #  "commit",
    #]
    #try:
     #   device.configure(commands)
      #  print(f"\n--- SR-TE Policy Configuration Complete on {device.name} ---")
    #except Exception as e:
     #   print(f"Failed to configure SR-TE Policy on {device.name}: {e}")


def verify_configuration(device):
    """Verify the applied configurations."""
    print(f"\n--- Verifying Interface Configuration on {device.name} ---")
    print(device.execute("show ip interface brief"))

    print(f"\n--- Verifying OSPF Configuration on {device.name} ---")
    print(device.execute("show ospf neighbor"))

    print(f"\n--- Verifying BGP Configuration on {device.name} ---")
    print(device.execute("show bgp summary"))

    print(f"\n--- Verifying SR-TE Policy on {device.name} ---")
    print(device.execute("show mpls traffic-eng policy brief"))


# Main Execution
for device_name, config in device_configs.items():
    device = tb.devices[device_name]
    print(f"\n--- Connecting to {device_name} ---")

    try:
        device.connect()
    except Exception as e:
        print(f"Failed to connect to {device.name}: {e}")
        continue

    # Show version for validation
    print(f"\n--- Device Information for {device_name} ---")
    try:
        print(device.execute("show version"))
    except Exception as e:
        print(f"Failed to execute 'show version' on {device.name}: {e}")
        continue

    # Apply configurations
    try:
        configure_segment_routing(device)
        configure_interface(device, config)
        configure_control_plane(device)
        configure_ospf(device, config)
        configure_bgp(device, config)
        #configure_SRPolicy(device, config)
        # Verify configurations
        verify_configuration(device)
    except Exception as e:
        print(f"Configuration failed on {device.name}: {e}")

    # Disconnect from the device
    device.disconnect()
    print(f"\n--- Disconnected from {device_name} ---")

print("\n--- Configuration and Verification Complete for All Devices ---")
