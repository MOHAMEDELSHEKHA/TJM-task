import time
import sys
import os
from dotenv import load_dotenv
from automation.screenshot import take_screenshot
from automation.mouse import double_click
from automation.notepad import (
    ensure_save_directory,
    write_post_to_notepad,
    is_notepad_open
)
from api.posts import fetch_posts, format_post, get_filename
from grounding.planner import get_candidate_regions_safe
from grounding.grounder import find_element_in_regions
from grounding.visual_fallback import save_icon_reference
from utils.annotate import save_annotated_screenshot

load_dotenv()

MAX_RETRIES = 3
SAVE_ANNOTATIONS = True
NUM_POSTS = 10
GROUNDING_INSTRUCTION = ""


def get_grounding_instruction():
    """
    Asks user what icon to find.
    Returns instruction string and True if Notepad, False otherwise.
    """
    print("\n" + "="*50)
    print("What icon do you want to find?")
    print("="*50)
    choice = input("Find the Notepad desktop shortcut icon? (y/n): ").strip().lower()

    if choice == 'y':
        return "Find the Notepad desktop shortcut icon", True
    else:
        icon_name = input("Enter the name of the icon you want to find: ").strip()
        return f"Find the {icon_name} desktop shortcut icon", False


def ground_icon(screenshot, attempt=1):
    print(f"\n--- Grounding attempt {attempt}/{MAX_RETRIES} ---")
    regions = get_candidate_regions_safe(screenshot, GROUNDING_INSTRUCTION)
    coords, used_region = find_element_in_regions(
        screenshot, regions, GROUNDING_INSTRUCTION
    )
    return coords, used_region


def try_click_and_verify(coords, screenshot, region, label):
    if SAVE_ANNOTATIONS and region is not None:
        try:
            save_annotated_screenshot(screenshot, region, coords, label=label)
        except Exception as e:
            print(f"Warning: Could not save screenshot: {e}")

    double_click(coords[0], coords[1])
    time.sleep(2)

    if is_notepad_open():
        try:
            save_icon_reference(screenshot, coords)
        except Exception as e:
            print(f"Warning: Could not save icon reference: {e}")
        return True
    return False


def find_and_click_icon():
    for attempt in range(1, MAX_RETRIES + 1):
        screenshot = take_screenshot()
        coords, used_region = ground_icon(screenshot, attempt)

        if coords is not None:
            print(f"✓ Icon found at {coords}")

            if try_click_and_verify(
                coords, screenshot, used_region,
                f"Attempt {attempt} - Icon detected"
            ):
                print("✓ Icon launched successfully")
                return True

            offsets = [
                (0, -30), (0, 30), (-30, 0), (30, 0),
                (0, -60), (0, 60), (-60, 0), (60, 0),
                (-30, -30), (30, 30), (-30, 30), (30, -30)
            ]
            for offset_x, offset_y in offsets:
                adjusted = (coords[0] + offset_x, coords[1] + offset_y)
                double_click(adjusted[0], adjusted[1])
                time.sleep(2)
                if is_notepad_open():
                    print(f"✓ Icon launched at {adjusted}")
                    try:
                        save_icon_reference(screenshot, adjusted)
                    except Exception as e:
                        print(f"Warning: Could not save icon reference: {e}")
                    return True

            print(f"✗ All attempts failed on attempt {attempt}")
        else:
            print(f"✗ Grounding failed on attempt {attempt}")

        if attempt < MAX_RETRIES:
            time.sleep(2)

    print("✗ Could not find icon")
    return False


def process_posts(posts):
    successful = 0
    failed = 0

    for i, post in enumerate(posts):
        print(f"\n{'='*50}")
        print(f"Post {i+1}/{len(posts)} (ID: {post['id']})")
        print(f"{'='*50}")

        time.sleep(3)

        if not find_and_click_icon():
            print(f"✗ Could not launch Notepad for post {post['id']}, skipping...")
            failed += 1
            continue

        time.sleep(2)

        content = format_post(post)
        filename = get_filename(post)
        write_post_to_notepad(content, filename)

        successful += 1
        print(f"✓ Saved: {filename}")

    return successful, failed


def run_notepad_workflow():
    ensure_save_directory()

    try:
        posts = fetch_posts(NUM_POSTS)
        print(f"✓ Fetched {len(posts)} posts")
    except Exception as e:
        print(f"✗ Failed to fetch posts: {e}")
        sys.exit(1)

    print("\nMake sure the Notepad shortcut is visible on your desktop.")
    print("Starting in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    successful, failed = process_posts(posts)

    print("\n" + "="*50)
    print("AUTOMATION COMPLETE")
    print("="*50)
    print(f"✓ Successful: {successful}/{NUM_POSTS}")
    print(f"✗ Failed:     {failed}/{NUM_POSTS}")
    print(f"Files saved to: OneDrive/Desktop/tjm-project/")
    print(f"Annotated screenshots: screenshots/")


def run_icon_workflow():
    print(f"\nMake sure the icon is visible on your desktop.")
    print("Starting in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    success = find_and_click_icon()

    print("\n" + "="*50)
    if success:
        print("✓ Icon launched successfully")
    else:
        print("✗ Could not find or launch icon")
    print(f"Annotated screenshots: screenshots/")
    print("="*50)


def main():
    global GROUNDING_INSTRUCTION

    print("="*50)
    print("Desktop Automation - Visual Grounding Pipeline")
    print("="*50)

    GROUNDING_INSTRUCTION, is_notepad = get_grounding_instruction()
    print(f"\nLooking for: {GROUNDING_INSTRUCTION}")

    if is_notepad:
        run_notepad_workflow()
    else:
        run_icon_workflow()


if __name__ == "__main__":
    main()