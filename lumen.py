from pyats.topology import loader

# Load testbed
testbed = loader.load('testbed.yaml')

def configure_device(device_name, config):
    device = testbed.devices[device_name]  # Access one device at a time
    device.connect(log_stdout=True)  # Enable logging for better debugging
    device.configure(config)
    print(f"Configuration applied on {device_name}")

# Device configurations
devices_config = {
    "R1": """
    interface ethernet0/2
    ip address 192.168.5.1 255.255.255.0
    no shutdown
    exit
    interface loopback 1
    ip address 1.1.1.1 255.255.255.255
    exit
    router ospf 1
    router-id 1.1.1.1
    network 1.1.1.1 0.0.0.0 area 0
    network 192.168.5.0 0.0.0.255 area 0
    exit
    router bgp 200
    neighbor 11.11.11.11 remote-as 200
    neighbor 11.11.11.11 update-source loopback 1
    do wr
    """,

    "R2": """
    interface ethernet0/0
    ip address 192.168.5.2 255.255.255.0
    no shutdown
    exit
    interface ethernet0/1
    ip address 192.168.6.2 255.255.255.0
    no shutdown
    exit
    interface e0/2
    no shutdown
    exit
    interface loopback 2
    ip address 2.2.2.2 255.255.255.255
    exit
    router ospf 1
    router-id 2.2.2.2
    network 2.2.2.2 0.0.0.0 area 0
    network 192.168.5.0 0.0.0.255 area 0
    network 192.168.6.0 0.0.0.255 area 0
    do wr
    """,

    "XR1": """
    interface loopback 1
    ipv4 address 11.11.11.11/32
    exit
    interface gi0/0/0/0
    ipv4 address 192.168.6.1/24
    no shutdown
    exit
    interface gi0/0/0/1
    ipv4 address 192.168.7.1/24
    no shutdown
    exit
    route-policy pass
    pass
    end-policy
    commit
    router ospf 1
    router-id 11.11.11.11
    area 0
    interface gi0/0/0/0
    interface loopback 1
    interface gi0/0/0/1
    exit
    router bgp 200
    bgp router-id 11.11.11.11
    address-family ipv4 unicast
    exit
    neighbor 1.1.1.1 remote-as 200
    update-source loopback 1
    address-family ipv4 unicast
    route-policy pass in
    route-policy pass out
    exit
    neighbor 192.168.7.3 remote-as 100
    address-family ipv4 unicast
    route-policy pass in
    route-policy pass out
    exit
    commit
    """,

    "R3": """
    interface ethernet0/0
    ip address 192.168.7.3 255.255.255.0
    no shutdown
    exit
    interface loopback 3
    ip address 3.3.3.3 255.255.255.255
    exit
    router bgp 100
    neighbor 192.168.7.1 remote-as 200
    network 3.3.3.3 mask 255.255.255.255
    do wr
    """
}

# Execute configuration sequentially
for device_name, config in devices_config.items():
    try:
        configure_device(device_name, config)
    except Exception as e:
        print(f"Failed to configure {device_name}: {e}")

print("✅ All configurations applied successfully!")
