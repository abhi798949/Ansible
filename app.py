import ipaddress
from flask import Flask, request, jsonify, render_template
from pyats.topology import loader

app = Flask(__name__)

testbed = loader.load('testbed.yaml')

def calculate_masks(ip_address):
    try:
        ip_network = ipaddress.ip_network(ip_address, strict=False)
        subnet_mask = str(ip_network.netmask)
        wildcard_mask = str(ip_network.hostmask)

        # Validate wildcard mask format
        if not wildcard_mask.count('.') == 3:
            raise ValueError(f"Invalid wildcard mask: {wildcard_mask} for {ip_address}")

        return subnet_mask, wildcard_mask
    except ValueError as e:
        raise ValueError(f"Invalid IP address: {ip_address}. {e}")

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/api/configure_ospf', methods=['POST'])
def configure_ospf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. No JSON data provided"}), 400

        router_name = data.get("Router")
        interface = data.get("interface")
        ip_address = data.get("ipAddress", "")  
        subnet_mask = data.get("subnetMask")  
        ospf_id = data.get("OSPF_ID")
        router_id = data.get("Router_ID")
        network = data.get("network")  # This might be missing CIDR notation
        area = data.get("area")
        ASN = data.get("ASN")
        router_id = data.get("router-id")
        neighbor_ip = data.get("neighbor_IP")
        remote_as = data.get("remote_as")

        if not all([router_name, interface, ospf_id, router_id, network, area]):
            return jsonify({"error": "All fields except IP and subnet are required for OSPF configuration"}), 400

        router = testbed.devices.get(router_name)
        if not router:
            return jsonify({"error": f"Router {router_name} not found in the testbed"}), 404

        router.connect()

        if "/" not in network:
            if subnet_mask:
                prefix_length = ipaddress.IPv4Network(f"0.0.0.0/{subnet_mask}").prefixlen
                network_with_cidr = f"{network}/{prefix_length}"
            else:
                return jsonify({"error": "Subnet mask required when network lacks prefix length"}), 400
        else:
            network_with_cidr = network

        _, wildcard_mask = calculate_masks(network_with_cidr)

        commands = [
            f"interface {interface}",
            f"ip address {ip_address} {subnet_mask}",
            f"no shut",
            f"exit",
            f"router ospf {ospf_id}",
            f"router-id {router_id}",
            f"network {network} {wildcard_mask} area {area}",
            f"exit",
            f"router bgp {ASN}",
            f"bgp router-id {router_id}",
            f"neighbor {neighbor_ip} remote-as {remote_as}",
        ]

        router.configure(commands)
        router.disconnect()

        return jsonify({"message": f"OSPF configuration applied successfully on {router_name}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

