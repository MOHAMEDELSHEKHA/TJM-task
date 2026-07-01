import pyautogui
from PIL import Image
import os
from datetime import datetime

def take_screenshot():
    screenshot = pyautogui.screenshot()
    return screenshot

def save_screenshot(image, folder="screenshots", prefix="screenshot"):
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(folder, filename)

    image.save(filepath)
    return filepath

def crop_region(image, region):
    x1, y1, x2, y2 = region
    cropped = image.crop((x1, y1, x2, y2))
    return cropped