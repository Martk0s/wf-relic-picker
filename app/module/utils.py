import pyautogui
import cv2
import numpy as np
from playsound import playsound
import sys
import os


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def take_screenshot():
    # Capture a screenshot of the specific window
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot


def print_error(message):
    playsound(resource_path(r"app/assets/sound/UICommonError.mp3"), block=False)
    print(message)
