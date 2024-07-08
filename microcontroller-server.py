from flask import Flask, request, jsonify
import os
import sys
import time
import pyautogui
from ultralytics import YOLO
import cv2
import numpy as np

app = Flask(__name__)


if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

# Path to the best.pt file
best_pt_path = os.path.join(base_path, 'runs', 'detect', 'train6', 'weights', 'best.pt')

# Load your model
model = YOLO(best_pt_path)

def click_button(detected_elements, label="button"):
    for button in detected_elements:
        if button['label'] == label: 
            x1, y1, x2, y2 = button['coordinates']
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2

            instruction = {
                "action": "click",
                "coordinates": [x_center, y_center]
            }

            print(f"Clicked {label}")
            
            return instruction
    

def capture_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def run_inference(screenshot):
    screenshot_path = "temp_screenshot.png"
    cv2.imwrite(screenshot_path, screenshot)
    results = model(screenshot_path)
    detected_elements = []

    for result in results:
        for box in result.boxes:
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

@app.route('/instructions', methods=['GET', 'POST'])
def get_coordinates():
    instructions = []
    screenshot = capture_screenshot()
    detected_elements = run_inference(screenshot)
    
    for element in detected_elements:
        x1, y1, x2, y2 = element['coordinates']
        x_center = (x1 + x2) // 2
        y_center = (y1 + y2) // 2
        
        if element['label'] == 'devicetitle':  # Adjust the label name as per your trained model
            title_coordinates = element['coordinates']
            print(f"Detected device name at {title_coordinates}")
            
            instructions.append(click_button(detected_elements, 'input'))
            
            instructions.append({
                "action": "type",
                "text": "Computer-test"  # Replace with actual text as needed
            })
            
            instructions.append(click_button(detected_elements))
            
            
            return jsonify(instructions)
        
        elif element['label'] == 'nametitle':  # Adjust the label name as per your trained model
            title_coordinates = element['coordinates']
            print(f"Detected name title at {title_coordinates}")
            
            instructions.append(click_button(detected_elements, 'input'))
            
            instructions.append({
                "action": "type",
                "text": "icsadmin"  # Replace with actual text as needed
            })
            
            instructions.append(click_button(detected_elements))
            
            
            return jsonify(instructions)
        
        elif element['label'] in ['passwordtitle', 'confirmtitle']:  # Adjust the label name as per your trained model
            title_coordinates = element['coordinates']
            print(f"Detected password title at {title_coordinates}")
            
            instructions.append(click_button(detected_elements, 'input'))
            
            instructions.append({
                "action": "type",
                "text": "Nova5455!"  # Replace with actual text as needed
            })
            
            instructions.append(click_button(detected_elements))
            
            
            return jsonify(instructions)
        
    
    
    
    
    return "no elements detected"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)