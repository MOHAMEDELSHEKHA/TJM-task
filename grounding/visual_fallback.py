from botcity.core import DesktopBot
from PIL import Image
import os
import time

SCREENSHOTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "screenshots"
)

ICON_REFERENCE_PATH = os.path.join(SCREENSHOTS_DIR, "notepad_icon.png")
ICON_LABEL = "notepad_icon"


def save_icon_reference(screenshot, coords, size=80):

    x, y = coords
    x1 = max(0, x - size // 2)
    y1 = max(0, y - size // 2)
    x2 = min(screenshot.width, x + size // 2)
    y2 = min(screenshot.height, y + size // 2)

    icon_crop = screenshot.crop((x1, y1, x2, y2))
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    icon_crop.save(ICON_REFERENCE_PATH)
    print(f"✓ Clean icon reference saved: {ICON_REFERENCE_PATH}")


def botcity_search_screenshot(screenshot):

    if not os.path.exists(ICON_REFERENCE_PATH):
        print("Icon will be saved automatically after first successful grounding.")
        return None

    bot = DesktopBot()

    bot.add_image(ICON_LABEL, ICON_REFERENCE_PATH)

    for matching in [0.9, 0.8, 0.7]:
        print(f"BotCity searching live screen at matching: {matching}")

        try:
            result = bot.find(
                label=ICON_LABEL,
                matching=matching,
                waiting_time=3000,  
                best=True
            )

            if result is not None:
                center_x = result.left + result.width // 2
                center_y = result.top + result.height // 2
                print(f"✓ BotCity found icon at: ({center_x}, {center_y})")
                return (center_x, center_y)
            else:
                print(f"BotCity: not found at matching {matching}")

        except Exception as e:
            print(f"BotCity error at matching {matching}: {e}")

        time.sleep(0.3)

    return None