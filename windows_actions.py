import pyautogui
import time
from threading import Thread, Event

windows_press_threads = {}

def simulate_windows_click(x, y):
    pyautogui.click(x, y)

def simulate_windows_scroll(start_x, start_y, end_x, end_y, duration):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.dragTo(end_x, end_y, duration / 1000.0, button='left')

def simulate_windows_long_press(x, y, duration):
    pyautogui.mouseDown(x, y)
    time.sleep(duration / 1000.0)
    pyautogui.mouseUp()

def simulate_windows_multiple_taps(x, y, count=2):
    pyautogui.moveTo(x, y)
    for _ in range(count):
        pyautogui.click()
        time.sleep(0.05)  # small delay between clicks

def simulate_windows_continuous_press(x, y, key):
    if key in windows_press_threads:
        return

    stop_event = Event()
    windows_press_threads[key] = stop_event

    def press_loop():
        pyautogui.mouseDown(x, y)
        while not stop_event.is_set():
            time.sleep(0.05)
        pyautogui.mouseUp()

    Thread(target=press_loop, daemon=True).start()

def stop_windows_continuous_press(key):
    if key in windows_press_threads:
        windows_press_threads[key].set()
        del windows_press_threads[key]
