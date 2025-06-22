import subprocess
import time
from threading import Thread, Event

press_threads = {}

def simulate_touch(x, y):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])

def simulate_scroll(start_x, start_y, end_x, end_y, duration):
    subprocess.run([
        "adb", "shell", "input", "swipe",
        str(start_x), str(start_y),
        str(end_x), str(end_y),
        str(duration)
    ])

def simulate_long_press(x, y, duration):
    subprocess.run([
        "adb", "shell", "input", "swipe",
        str(x), str(y),
        str(x), str(y),
        str(duration)
    ])

def simulate_multiple_taps(x, y, count):
    for _ in range(count):
        simulate_touch(x, y)
        time.sleep(0.05)  # slight delay between taps

def simulate_continuous_press(x, y, key):
    if key in press_threads:
        return

    stop_event = Event()
    press_threads[key] = stop_event

    def press_loop():
        while not stop_event.is_set():
            print(f"👉 Long press {key} starting")
            subprocess.run([
                "adb", "shell", "input", "swipe",
                str(x), str(y), str(x), str(y),
                "30000"
            ])
            print(f"🕒 Long press {key} done, looping again if not released")
            time.sleep(0.05)  # brief pause before repeating

    Thread(target=press_loop, daemon=True).start()

def stop_continuous_press(key):
    if key in press_threads:
        press_threads[key].set()
        del press_threads[key]
        print(f"🛑 Stopped continuous press for key: {key}")
        subprocess.run(["adb", "shell", "input", "tap", "10", "10"])  # optional cleanup
