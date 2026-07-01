import pyautogui
import time

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1


def move_to(x, y, duration=0.5):
    pyautogui.moveTo(x, y, duration=duration)


def single_click(x, y):
    move_to(x, y)
    time.sleep(0.2)
    pyautogui.click(x, y)


def double_click(x, y):
    move_to(x, y)
    time.sleep(0.2)
    pyautogui.doubleClick(x, y)
    time.sleep(1.5)


def right_click(x, y):
    move_to(x, y)
    time.sleep(0.2)
    pyautogui.rightClick(x, y)


def press_key(key):
    pyautogui.press(key)
    time.sleep(0.1)


def hotkey(*keys):
    pyautogui.hotkey(*keys)
    time.sleep(0.3)


def click_at_coordinates(coords):
    if coords is None:
        raise ValueError("Cannot click — no coordinates provided.")
    x, y = coords
    double_click(x, y)