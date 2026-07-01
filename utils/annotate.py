from PIL import Image, ImageDraw
import os
from datetime import datetime

# Always save to Desktop/screenshots regardless of where script is run from
SCREENSHOTS_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "screenshots")


def draw_detection_box(image, region, coords, label="Detected"):
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    draw_region_box(draw, region)
    draw_crosshair(draw, coords)
    draw_label(draw, coords, label)
    return annotated


def draw_region_box(draw, region):
    x1, y1, x2, y2 = region
    draw.rectangle([x1, y1, x2, y2], outline="blue", width=3)
    draw.rectangle([x1, y1, x1 + 130, y1 + 22], fill="blue")
    draw.text((x1 + 3, y1 + 3), "Planner Region", fill="white")


def draw_crosshair(draw, coords, size=20, color="red"):
    x, y = coords
    draw.line([x - size, y, x + size, y], fill=color, width=3)
    draw.line([x, y - size, x, y + size], fill=color, width=3)
    draw.ellipse([x - 8, y - 8, x + 8, y + 8], outline=color, width=3)


def draw_label(draw, coords, label):
    x, y = coords
    text = f"{label}\n({x}, {y})"
    text_x = x + 15
    text_y = y - 40

    # Keep label on screen
    if text_x + 200 > 1920:
        text_x = x - 215
    if text_y < 0:
        text_y = y + 15

    draw.rectangle(
        [text_x - 5, text_y - 5, text_x + 200, text_y + 45],
        fill="black"
    )
    draw.text((text_x, text_y), text, fill="white")


def save_annotated_screenshot(image, region, coords,
                               label="Notepad detected",
                               prefix="annotated"):
    try:
        annotated = draw_detection_box(image, region, coords, label)
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        annotated.save(filepath)
        print(f"Saved annotated screenshot: {filepath}")
        return filepath
    except PermissionError as e:
        print(f"Permission error saving screenshot: {e}")
        print(f"Attempted path: {SCREENSHOTS_DIR}")
        return None
    except Exception as e:
        print(f"Failed to save screenshot: {e}")
        return None