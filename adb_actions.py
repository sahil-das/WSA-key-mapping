import subprocess
import time
import os

# Suppress command prompt window when using subprocess in Windows GUI app
CREATE_NO_WINDOW = 0x08000000

def simulate_touch(x, y):
    """Simulates a single tap at (x, y)."""
    subprocess.run(
        ["adb", "shell", "input", "tap", str(x), str(y)],
        creationflags=CREATE_NO_WINDOW
    )

def simulate_long_press(x, y, duration=1000):
    """Simulates a long press at (x, y) for a given duration (in ms)."""
    end_time = int(time.time() * 1000) + duration
    while int(time.time() * 1000) < end_time:
        subprocess.run(
            ["adb", "shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration)],
            creationflags=CREATE_NO_WINDOW
        )
        break

def simulate_multiple_taps(x, y, count=2):
    """Simulates multiple taps at (x, y)."""
    for _ in range(count):
        subprocess.run(
            ["adb", "shell", "input", "tap", str(x), str(y)],
            creationflags=CREATE_NO_WINDOW
        )
        time.sleep(0.1)

def simulate_scroll(start_x, start_y, end_x, end_y, duration=300):
    """Simulates a scroll or swipe gesture."""
    subprocess.run(
        ["adb", "shell", "input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration)],
        creationflags=CREATE_NO_WINDOW
    )
