import ipaddress
from flask import Flask, request, jsonify, render_template
from pyats.topology import loader

app = Flask(__name__)

# Load the testbed once at the start
testbed = loader.load('testbed.yaml')

def calculate_masks(ip_address):
    """Calculate subnet mask and wildcard mask from an IP address with prefix length."""
    try:
        ip_network = ipaddress.ip_network(ip_address, strict=False)
        return str(ip_network.netmask), str(ip_network.hostmask)
    except ValueError as e:
        raise ValueError(f"Invalid IP address: {ip_address}. {e}")

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/api/configure_interface', methods=['POST'])
def configure_interface():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        interface = data.get("interface")
        ip_type = data.get("ipType")
        ip_address = data.get("ipAddress", "")
        subnet_mask = data.get("subnetMask", "")
        router_name = data.get("Router")

        if not router_name or not interface or not ip_type:
            return jsonify({"error": "Router, interface, and IP type are required"}), 400

        router = testbed.devices.get(router_name)
        if not router:
            return jsonify({"error": f"Router {router_name} not found"}), 404

        router.connect()

        commands = [f"interface {interface}"]
        if ip_type == "static":
            if not ip_address or not subnet_mask:
                return jsonify({"error": "IP address and subnet mask are required for static configuration"}), 400
            commands.append(f"ip address {ip_address} {subnet_mask}")
        elif ip_type == "dhcp":
            commands.append("ip address dhcp")
        else:
            return jsonify({"error": "Invalid IP type"}), 400

        commands.append("no shutdown")
        router.configure(commands)
        verification = router.execute(f"show running-config interface {interface}")
        router.disconnect()

        return jsonify({"message": "Configuration applied successfully", "details": verification}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/configure_ospf', methods=['POST'])
def configure_ospf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        router_name = data.get("Router")
        interface = data.get("interface")
        ospf_id = data.get("OSPF_ID")
        router_id = data.get("Router_ID")
        network = data.get("network")
        area = data.get("area")

        if not all([router_name, interface, ospf_id, router_id, network, area]):
            return jsonify({"error": "All fields are required for OSPF configuration"}), 400

        router = testbed.devices.get(router_name)
        if not router:
            return jsonify({"error": f"Router {router_name} not found"}), 404

        router.connect()
        _, wildcard_mask = calculate_masks(network)

        commands = [
            f"interface {interface}",
            f"ip address {data.get('ipAddress')} {data.get('subnetMask')}",
            "exit",
            f"router ospf {ospf_id}",
            f"router-id {router_id}",
            f"network {network} {wildcard_mask} area {area}",
        ]

        router.configure(commands)
        router.disconnect()

        return jsonify({"message": "OSPF configuration applied successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

