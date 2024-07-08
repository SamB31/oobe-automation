import os
import sys
import time
import pyautogui
from ultralytics import YOLO
import cv2
import numpy as np
import argparse
from subprocess import Popen
import threading
import subprocess


if getattr(sys, 'frozen', False):

    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")
    
    
# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process some inputs for automation.')
parser.add_argument('initial_device_name', type=str, help='Initial name of the device')
parser.add_argument('ip_address', type=str, help='IP Address of machine')
parser.add_argument('new_device_name', type=str, help='New name of device')
parser.add_argument('site', type=str, help='Which site is the computer being set up for')

args = parser.parse_args()

initial_device_name = args.initial_device_name
ip_address = args.ip_address
new_device_name = args.new_device_name
site = args.site

# Path to the best.pt file
best_pt_path = os.path.join(base_path, 'runs', 'detect', 'train6', 'weights', 'best.pt')

# Load your model
model = YOLO(best_pt_path)



#def ping_host(ip_address):
#    response = os.system(f"ping -n 1 {ip_address} >nul 2>&1")
#    return response == 0

def ping_host(ip_address):
    # Execute the ping command and capture the output
    result = subprocess.run(f"ping -n 1 {ip_address}", capture_output=True, text=True, shell=True)
    output = result.stdout
    # Check if the output contains "bytes=" indicating the host is reachable
    if "bytes=" in output:
        return True
    return False

def run_vnc_viewer(ip_address):
    command = f'"C:\\Program Files\\TightVNC\\tvnviewer.exe" -host={ip_address} -password=Shane2107'
    process = subprocess.Popen(command, shell=True)
    return process

def monitor_connection(ip_address, process):
    while True:
        if not ping_host(ip_address):
            print("Connection lost. Killing VNC Viewer process...")
            subprocess.Popen(f"TASKKILL /F /PID {process.pid} /T", shell=True)
            while not ping_host(ip_address):
                print("Waiting for connection to be restored...")
                time.sleep(8)
            print("Connection restored. Restarting VNC Viewer...")
            time.sleep(25)
            process = run_vnc_viewer(ip_address)
        time.sleep(8)  # Check the connection status every 10 seconds

def click_button(detected_elements, label='button'):
    
    for button in detected_elements:
        if button['label'] == label: 
            x1, y1, x2, y2 = button['coordinates']
            x_center = round((x1 + x2) // 2)
            y_center = round((y1 + y2) // 2)
            pyautogui.moveTo(x_center, y_center)
            pyautogui.click()
            print(f"Clicked {label}")
            return

def click_input(detected_elements, label, text, offset=0):
    
    for input_field in detected_elements:
        if input_field['label'] == label:  # Adjust the label name as per your trained model
            x1, y1, x2, y2 = input_field['coordinates']
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2
            pyautogui.moveTo(x_center, y_center)
            pyautogui.click()
            time.sleep(2)
            # Send keystrokes
            pyautogui.write(text)  # Adjust the input text as needed
            time.sleep(2)
            return  # Exit after finding and clicking the input field
        
def click_security(detected_elements):
    
    for security_field in detected_elements:
        
        if security_field['label'] == 'securityinput':  # Adjust the label name as per your trained model
            x1, y1, x2, y2 = security_field['coordinates']
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2
            pyautogui.moveTo(x_center, y_center)
            pyautogui.click()
            print(f"Clicked drop down")
            
            time.sleep(2)
            
            pyautogui.moveTo(x_center, y_center+40)
            time.sleep(1)
            pyautogui.click()
            print(f"Clicked option")
            
            time.sleep(2)

            return  

def capture_screenshot():
    # Capture a screenshot
    screenshot = pyautogui.screenshot()
    # Convert the screenshot to a format suitable for OpenCV
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def run_inference(screenshot):
    # Save the screenshot to a temporary file
    screenshot_path = "temp_screenshot.png"
    cv2.imwrite(screenshot_path, screenshot)

    # Run inference on the screenshot
    results = model(screenshot_path)

    # Extract detected elements and their coordinates
    detected_elements = []

    for result in results:
        for box in result.boxes:
            # Get coordinates
            x1, y1, x2, y2 = box.xyxy.tolist()[0]
            label = result.names[int(box.cls)]
            confidence = box.conf.item()
            detected_elements.append({
                "label": label,
                "confidence": confidence,
                "coordinates": (x1, y1, x2, y2)
            })
    
    if not detected_elements:
        print("No elements detected")
    
    return detected_elements

def process_elements(detected_elements):
    # Print detected elements and their coordinates
    for element in detected_elements:
        print(f"Label: {element['label']}, Confidence: {element['confidence']:.2f}, Coordinates: {element['coordinates']}")
        
    

    for element in detected_elements:
        
        if element['label'] == 'devicetitle':  # Adjust the label name as per your trained model
            title_coordinates = element['coordinates']
            print(f"Detected device name at {title_coordinates}")
            
            # Wait for a few seconds before clicking the input
            time.sleep(2)

            click_input(detected_elements, "input", "Computer-test")
            
            time.sleep(2)
        
        if element['label'] == 'nametitle':  # Adjust the label name as per your trained model
            title_coordinates = element['coordinates']
            print(f"Detected nametitle at {title_coordinates}")
            
            # Wait for a few seconds before clicking the input
            time.sleep(2)

            click_input(detected_elements, "input", "icsadmin")

                
        elif element['label'] in ['passwordtitle', 'confirmtitle']:
            title_coordinates = element['coordinates']
            print(f"Detected passwordtitle at {title_coordinates}")
            
            # Wait for a few seconds before clicking the input
            time.sleep(2)
            
            
            click_input(detected_elements, "input", "Nova5455!")

                
        elif element['label'] == 'securitytitle':
            title_coordinates = element['coordinates']
            print(f"Detected securitytitle at {title_coordinates}")
            
            # Wait for a few seconds before clicking the input
            time.sleep(2)
            
            click_security(detected_elements)
  
            click_input(detected_elements, 'input', 'ics')
            
            
        elif element['label'] == 'setuptitle':
            title_coordinates = element['coordinates']
            print(f"Detected setuptitle at {title_coordinates}")
            
            time.sleep(2)
            
            click_button(detected_elements, label='schooltitle')
            
            time.sleep(2)
            
        elif element['label'] == 'workschooltitle':
            for element in detected_elements:
                if element['label'] == 'domainjoin':
                    click_button(detected_elements, label='domainjoin')
                    time.sleep(2)
                elif element['label'] == 'input':
                    pyautogui.press('tab')
                    time.sleep(1)
                    
                    pyautogui.press('enter')                    
                    time.sleep(2)
                    
                detected_elements = [element for element in detected_elements if element['label'] != 'button']
                
    click_button(detected_elements)


process = run_vnc_viewer(ip_address)
time.sleep(7)  # Initial wait time

monitor_thread = threading.Thread(target=monitor_connection, args=(ip_address, process))
monitor_thread.start()

print("testing")

# Continuously check for titles and click the associated buttons

while True:
    
    screenshot = capture_screenshot()
    detected_elements = run_inference(screenshot)
    if detected_elements:
        process_elements(detected_elements)
    time.sleep(8)  # Wait for 5 seconds before taking the next screenshot (adjust as needed)

