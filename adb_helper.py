import subprocess
from tkinter import messagebox
from gui_helpers import key_to_touch, update_key_buttons
from tkinter import filedialog

adb_status_var = None
adb_status_label = None

def auto_connect_wsa():
    try:
        #print("Connecting to WSA (127.0.0.1:58526)...")
        result = subprocess.run(["adb", "connect", "127.0.0.1:58526"], capture_output=True, text=True, timeout=5)
        output = result.stdout.strip() + result.stderr.strip()

        if "connected" in output or "already connected" in output:
          #  print("✅ ADB successfully connected to WSA.")
            if adb_status_var and adb_status_label:
                adb_status_var.set("✅ ADB Connected")
                adb_status_label.configure(foreground="green")
        else:
           # print(f"❌ ADB connect failed: {output}")
            if adb_status_var and adb_status_label:
                adb_status_var.set("❌ ADB Failed")
                adb_status_label.configure(foreground="red")
    except Exception as e:
        #print(f"❌ ADB connection error: {e}")
        if adb_status_var and adb_status_label:
            adb_status_var.set("⚠️ ADB Error")
            adb_status_label.configure(foreground="orange")