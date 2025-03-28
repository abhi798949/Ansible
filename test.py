from flask import Flask, request, jsonify, render_template
import subprocess
import json

app = Flask(__name__)

def run_ansible(playbook, extra_vars):
    cmd = [
        "ansible-playbook", playbook,
        "-e", json.dumps(extra_vars)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else result.stderr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/configure_interface', methods=['POST'])
def configure_interface():
    data = request.json
    extra_vars = {
        "router": data['Router'],
        "interface": data['interface'],
        "ip_address": data['ipAddress'],
        "subnet_mask": data['subnetMask']
    }
    output = run_ansible("interface_config.yml", extra_vars)
    return jsonify({"message": "Interface configured", "output": output})

@app.route('/api/configure_ospf', methods=['POST'])
def configure_ospf():
    data = request.json
    extra_vars = {
        "router": data['Router'],
        "ospf_id": data['OSPF_ID'],
        "router_id": data['Router_ID'],
        "network": data['network'],
        "area": data['area']
    }
    output = run_ansible("ospf_config.yml", extra_vars)
    return jsonify({"message": "OSPF configured", "output": output})

if __name__ == '__main__':
    app.run(debug=True)
