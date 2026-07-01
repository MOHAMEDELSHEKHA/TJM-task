import pyautogui
import pyperclip
import pygetwindow as gw
import time
import os

SAVE_DIRECTORY = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "tjm-project")


def ensure_save_directory():
    os.makedirs(SAVE_DIRECTORY, exist_ok=True)
    print(f"Save directory ready: {SAVE_DIRECTORY}")


def is_notepad_open():
    windows = gw.getWindowsWithTitle("Notepad")
    return len(windows) > 0


def type_content(content):
    pyperclip.copy(content)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)


def save_file(filename):
    """
    Saves using Ctrl+S which opens Save As dialog on first save.
    Types the full path including directory and filename.
    """
    full_path = os.path.join(SAVE_DIRECTORY, filename)

    pyautogui.hotkey('ctrl', 'shift', 's')
    time.sleep(1.5)


    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyperclip.copy(full_path)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)

    pyautogui.press('enter')
    time.sleep(0.5)


    pyautogui.press('enter')
    time.sleep(0.3)

    print(f"Saved: {full_path}")


def close_notepad():
    pyautogui.click(960, 400)
    time.sleep(0.5)
    pyautogui.keyDown('alt')
    time.sleep(0.1)
    pyautogui.press('f4')
    pyautogui.keyUp('alt')
    time.sleep(1)

    pyautogui.press('n')
    time.sleep(0.5)


    for _ in range(5):
        if not is_notepad_open():
            print("✓ Notepad closed")

            pyautogui.press('escape')
            time.sleep(0.3)

            pyautogui.click(700, 400)
            time.sleep(1)
            return
        time.sleep(0.5)

    print("Warning: Notepad may still be open")


def write_post_to_notepad(post_content, filename):
    type_content(post_content)
    save_file(filename)
    time.sleep(0.3)
    close_notepad()
    time.sleep(0.5)