
import os

def auto_connect_wsa():
   # print("Connecting to WSA (127.0.0.1:58526)...")
    os.system("adb connect 127.0.0.1:58526")
    result = os.popen("adb devices").read()
    
def simulate_touch(x, y):
   # print(f"Simulating touch at: {x}, {y}")
    os.system(f"adb shell input tap {x} {y}")

def simulate_multiple_taps(x, y, count=2):
   # print(f"Simulating {count} taps at: {x}, {y}")
    for _ in range(count):
        os.system(f"adb shell input tap {x} {y}")

def simulate_scroll(start_x, start_y, end_x, end_y, duration=300):
   # print(f"Simulating scroll from ({start_x}, {start_y}) to ({end_x}, {end_y}) over {duration}ms")
    os.system(f"adb shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}")

def simulate_long_press(x, y, duration=1000):
    #print(f"Simulating long press at: ({x}, {y}) for {duration}ms")
    os.system(f"adb shell input swipe {x} {y} {x} {y} {duration}")

def check_adb_connection(label):
    try:
        result = os.popen("adb devices").read()
        if "127.0.0.1:58526" in result and "device" in result:
            label.config(text="✅ ADB Connected to WSA", fg="green")
        else:
            label.config(text="❌ ADB Not Connected", fg="red")
    except Exception as e:
        label.config(text=f"❌ ADB Check Failed: {e}", fg="red")
    label.after(5000, lambda: check_adb_connection(label))
