import os
import pyautogui
from ultralytics import YOLO
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Load the trained model
model = YOLO("runs\\detect\\train7\\weights\\best.pt")

# Capture a screenshot
screenshot = pyautogui.screenshot()

# Convert the screenshot to a format suitable for OpenCV
screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

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

# Print detected elements and their coordinates
for element in detected_elements:
    print(f"Label: {element['label']}, Confidence: {element['confidence']:.2f}, Coordinates: {element['coordinates']}")

# Plot the screenshot with bounding boxes using Matplotlib
fig, ax = plt.subplots(1, figsize=(12, 8))

# Convert screenshot back to RGB for plotting
screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

# Display the image
ax.imshow(screenshot_rgb)

# Add bounding boxes
for element in detected_elements:
    x1, y1, x2, y2 = element['coordinates']
    width, height = x2 - x1, y2 - y1
    rect = patches.Rectangle((x1, y1), width, height, linewidth=2, edgecolor='r', facecolor='none')
    ax.add_patch(rect)
    plt.text(x1, y1, f"{element['label']} ({element['confidence']:.2f})", color='red', fontsize=12, backgroundcolor='white')

# Show the plot
plt.axis('off')
plt.show()
