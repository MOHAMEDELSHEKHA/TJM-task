from google import genai
from PIL import Image
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


def get_candidate_regions(screenshot, instruction="Find the Notepad desktop icon"):
    prompt = f"""You are a GUI analysis assistant. I will give you a screenshot of a Windows desktop.

Your task is to find: "{instruction}"

Analyze the screenshot and identify up to 3 candidate regions where this element is most likely to be found.

Rules:
- Order regions by confidence, most likely first
- Each region should be reasonably sized to contain the target
- Use a 0-1000 coordinate system where:
  * (0, 0) is the TOP-LEFT corner of the screen
  * (1000, 1000) is the BOTTOM-RIGHT corner of the screen
  * (500, 500) is the CENTER of the screen

You MUST respond in this exact JSON format and nothing else:
{{
    "reasoning": "brief explanation of where you think the target is",
    "regions": [
        {{"x1": 0, "y1": 0, "x2": 500, "y2": 500, "confidence": "high"}},
        {{"x1": 0, "y1": 0, "x2": 500, "y2": 500, "confidence": "medium"}}
    ]
}}

All coordinates must be between 0 and 1000."""

    screenshot_resized = screenshot.resize((1280, 720))

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=[prompt, screenshot_resized]
    )

    return parse_response(response.text)


def parse_response(response_text):
    cleaned = re.sub(r"```json|```", "", response_text).strip()
    data = json.loads(cleaned)

    regions = []
    for region in data["regions"]:
        x1 = int((region["x1"] / 1000) * SCREEN_WIDTH)
        y1 = int((region["y1"] / 1000) * SCREEN_HEIGHT)
        x2 = int((region["x2"] / 1000) * SCREEN_WIDTH)
        y2 = int((region["y2"] / 1000) * SCREEN_HEIGHT)

        if x2 - x1 < 200:
            cx = (x1 + x2) // 2
            x1 = max(0, cx - 100)
            x2 = min(SCREEN_WIDTH, cx + 100)

        if y2 - y1 < 200:
            cy = (y1 + y2) // 2
            y1 = max(0, cy - 100)
            y2 = min(SCREEN_HEIGHT, cy + 100)

        x1 = max(0, min(SCREEN_WIDTH, x1))
        y1 = max(0, min(SCREEN_HEIGHT, y1))
        x2 = max(0, min(SCREEN_WIDTH, x2))
        y2 = max(0, min(SCREEN_HEIGHT, y2))

        if x2 <= x1:
            x2 = min(SCREEN_WIDTH, x1 + 300)
        if y2 <= y1:
            y2 = min(SCREEN_HEIGHT, y1 + 300)

        print(f"Planner region: ({x1},{y1},{x2},{y2})")
        regions.append((x1, y1, x2, y2))

    return regions


def get_candidate_regions_safe(screenshot, instruction="Find the Notepad desktop icon"):
    try:
        return get_candidate_regions(screenshot, instruction)
    except Exception as e:
        print(f"Planner failed: {e} — trying BotCity")
        return get_botcity_fallback_regions(screenshot)


def get_botcity_fallback_regions(screenshot):
    from grounding.visual_fallback import botcity_search_screenshot

    coords = botcity_search_screenshot(screenshot)

    if coords is not None:
        x, y = coords
        print(f"BotCity found icon at ({x}, {y})")
        x1 = max(0, x - 150)
        y1 = max(0, y - 150)
        x2 = min(SCREEN_WIDTH, x + 150)
        y2 = min(SCREEN_HEIGHT, y + 150)
        return [(x1, y1, x2, y2)]

    print("BotCity failed — using quadrant fallback")
    return get_quadrant_fallback()


def get_quadrant_fallback():
    return [
        (0,    0,    960,  540),
        (960,  0,    1920, 540),
        (0,    540,  960,  1080),
        (960,  540,  1920, 1080),
    ]