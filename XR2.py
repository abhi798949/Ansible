import ipaddress
import logging
from flask import Flask, request, jsonify,render_template
from pyats.topology import loader

# Initialize Flask app
app = Flask(__name__)

testbed = loader.load('testbed2.yaml')


@app.route('/')
def index():
    return render_template('input.html')

@app.route('/api/configure_ospf', methods=['POST'])
def configure_ospf():
    try:
        if not testbed:
            return jsonify({"error": "Testbed file is missing or invalid"}), 500

        # Get input data
        data = request.get_json()
        logging.debug(f"Received data: {data}")

        required_fields = ["Router", "interface", "ipAddress", "subnetMask", "OSPF_ID", "Router_ID", "network", "area"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        router_name = data["Router"]
        router = testbed.devices.get(router_name)

        if not router:
            return jsonify({"error": f"Router {router_name} not found"}), 404

        # Connect to the router
        router.connect()
        logging.debug(f"Connected to {router_name}")

        # Prepare OSPF Configuration Commands
        commands = [
            f"interface {data['interface']}",
            f"ipv4 address {data['ipAddress']} {data['subnetMask']}",
            "no shut",
            "exit",
            f"router ospf {data['OSPF_ID']}",
            f"router-id {data['Router_ID']}",
            f"network {data['network']} area {data['area']}",
            "commit replace"
        ]

        logging.debug(f"Executing commands: {commands}")

        # Apply configuration
        router.configure(commands)
        router.disconnect()
        logging.debug("Configuration successful.")

        return jsonify({"message": f"OSPF configured successfully on {router_name}"}), 200

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
