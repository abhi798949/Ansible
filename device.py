import ipaddress
import logging
from flask import Flask, request, jsonify, render_template
from pyats.topology import loader

# Load testbed
testbed = loader.load('testbed.yaml')

app = Flask(__name__)

# Configure Logging
logging.basicConfig(level=logging.INFO)

def configure_interface(device, config):
    """Configure the interface with IP settings."""
    commands = [
        f"interface {config['interface']}",
        f"ip address {config['interface_ip']} {config['subnet_mask']}",
        "no shutdown",
        "exit",
        "do write",  # Persist changes
    ]
    device.configure(commands)
    return f"Interface {config['interface']} configured successfully on {device.name}."

def configure_ospf(device, config):
    """Configure OSPF settings."""
    commands = [
        f"router ospf {config['ospf_id']}",
        f"router-id {config['router_id']}",
        f"network {config['network']} {config['wildcard_mask']} area {config['area']}",
        "exit",
        "do write",  # Persist changes
    ]
    device.configure(commands)
    return f"OSPF {config['ospf_id']} configured successfully on {device.name}."

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/configure', methods=['POST'])
def configure():
    try:
        data = request.form
        router_name = data.get("Router")
        interface = data.get("interface")
        interface_ip = data.get("interface_ip")
        subnet_mask = data.get("subnet_mask")
        ospf_id = data.get("OSPF-ID")
        router_id = data.get("ROUTER-ID")
        network = data.get("network")
        wildcard_mask = data.get("wildcardMask")
        area = data.get("area")

        if not all([router_name, interface, interface_ip, subnet_mask, ospf_id, router_id, network, wildcard_mask, area]):
            return jsonify({"error": "All fields are required"}), 400

        device = testbed.devices.get(router_name)
        if not device:
            return jsonify({"error": f"Router {router_name} not found"}), 404

        device.connect()
        response = []

        # Configure Interface
        interface_config = {
            "interface": interface,
            "interface_ip": interface_ip,
            "subnet_mask": subnet_mask
        }
        response.append(configure_interface(device, interface_config))

        # Configure OSPF
        ospf_config = {
            "ospf_id": ospf_id,  # Use the correct variable name
            "router_id": router_id,  # Use the correct variable name
            "network": network,
            "wildcard_mask": wildcard_mask,
            "area": area
        }
        response.append(configure_ospf(device, ospf_config))

        device.disconnect()
        return jsonify({"message": "Configuration applied successfully", "details": response}), 200

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
