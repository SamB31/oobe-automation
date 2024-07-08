from flask import Flask, request, jsonify
import threading
import subprocess

app = Flask(__name__)

PICO_1 = "RUN"



def initiate_vnc_connection(ip):
    # Command to start TightVNC Viewer
    command = f'"C:\\Program Files\\TightVNC\\tvnviewer.exe" -host={ip}:5900 -password=Shane2107'
    
    # Start the VNC Viewer process
    subprocess.call(command, shell=True)

    # Example automation script call after VNC connection is established
    run_automation_script()  # Call the function to run the separate script

def run_automation_script(initial_device_name, ip_address, new_device_name, site):
    # Path to your other Python script
    python_executable = r"c:/Users/Sam Blanton/Desktop/OOBE/venv/Scripts/python.exe"
    automation_script_path = r"c:/Users/Sam Blanton/Desktop/OOBE/oobe.py"

    # Call the Python script with arguments
    command = [
        python_executable,
        automation_script_path,
        initial_device_name,
        ip_address,
        new_device_name,
        site
    ]
    
    subprocess.call(command, shell=True)
    
    
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    computer_name = data.get('computer_name')
    ip_address = data.get('ip_address')

    # Log the received data
    print(f"Received registration from {computer_name} with IP {ip_address}")

    
    #run_automation_script(computer_name, ip_address, "comp-test", "SWH")
    PICO_1 = "WAIT"
    
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)