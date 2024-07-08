# OOBE Automation with Computer Vision

## Overview

This project automates the Out-Of-Box Experience (OOBE) using computer vision to detect and interact with elements on the screen. The automation process involves a client-server architecture where a loaded microcontroller is connected to a host device. The microcontroller communicates with an automation server, which initiates a VNC connection and runs a script to perform automated tasks on the host device by scanning the screen and clicking elements accordingly.

## Project Structure

### Automation Web Server: `automation-server.py`

The automation server is built using Flask and handles registration requests from the client. Upon receiving a request, it initiates a TightVNC Viewer connection to the specified IP address and runs the automation script. 

- **Key Functions:**
  - `initiate_vnc_connection(ip)`: Starts TightVNC Viewer with the provided IP address and password.
  - `run_automation_script(initial_device_name, ip_address, new_device_name, site)`: Executes a separate Python script for further automation.
  - `register()`: Handles incoming registration requests and triggers the VNC connection and automation script.

### Automation Script: `oobe.py`

This script is responsible for performing the actual automation tasks on the host device. It uses computer vision (YOLO model) to detect elements on the screen and interacts with them using `pyautogui`.

- **Key Functions:**
  - `ping_host(ip_address)`: Checks if the host is reachable via ping.
  - `run_vnc_viewer(ip_address)`: Starts the VNC Viewer process to control the remote device.
  - `monitor_connection(ip_address, process)`: Monitors the VNC connection and restarts it if lost.
  - `click_button(detected_elements, label)`: Clicks a button detected by the YOLO model.
  - `click_input(detected_elements, label, text)`: Clicks an input field and types the specified text.
  - `click_security(detected_elements)`: Handles interactions with security dropdowns.
  - `capture_screenshot()`: Captures a screenshot of the current screen.
  - `run_inference(screenshot)`: Runs the YOLO model to detect elements on the screen.
  - `process_elements(detected_elements)`: Processes detected elements and performs actions such as clicking buttons or entering text.

## Workflow

1. **Microcontroller Setup**: A microcontroller is connected to the host device, pre-loaded with a script to communicate with the automation server.
2. **Registration**: The microcontroller sends a POST request to the automation server, registering the host device and providing its IP address.
3. **VNC Connection**: The automation server initiates a TightVNC Viewer connection to the host device.
4. **Automation Script Execution**: The server runs the `oobe.py` script, which uses computer vision to detect and interact with UI elements on the host device.
5. **Screen Interaction**: The script continuously captures screenshots, runs inference to detect elements, and performs the necessary interactions, such as clicking buttons, entering text, or navigating menus.

## Technologies Used

- **Flask**: For creating the automation server and handling registration requests.
- **TightVNC Viewer**: To remotely control the host device.
- **YOLO (You Only Look Once)**: A state-of-the-art, real-time object detection system used for detecting UI elements on the screen.
- **pyautogui**: For automating mouse and keyboard interactions based on detected elements.
- **OpenCV**: For image processing and handling screenshots.

## Conclusion

This project demonstrates a powerful application of computer vision and automation to streamline the OOBE for new devices. By leveraging a client-server architecture and advanced detection models, it provides a robust and scalable solution for automating device setup tasks.
