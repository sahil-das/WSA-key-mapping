import json
import subprocess
from ttkbootstrap import Window
from tkinter import filedialog
from tkinter import ttk, messagebox, StringVar
from gui_helpers import set_coordinates, edit_key_action, key_to_touch, update_key_buttons, remove_key  # Importing from gui_helpers
from config_manager import save_config, load_config  # Import save and load config functions
import tkinter as tk

adb_status_var = None
adb_status_label = None
window_alive = True
adb_connected_once = False

def connect_adb(force=False):
    global window_alive, adb_connected_once

    if not window_alive:
        return

    if not force and adb_connected_once:
        return  # Skip if already auto-connected

    adb_connected_once = True

    try:
       # print("Connecting to WSA (127.0.0.1:58526)...")
        result = subprocess.run(["adb", "connect", "127.0.0.1:58526"], capture_output=True, text=True, timeout=5)
        output = result.stdout.strip() + result.stderr.strip()

        if "connected" in output or "already connected" in output:
            adb_status_var.set("✅ ADB Connected")
            adb_status_label.configure(foreground="green")
           # print("✅ ADB successfully connected to WSA.")
        else:
            adb_status_var.set("❌ ADB Failed")
            adb_status_label.configure(foreground="red")
            #print(f"❌ ADB connect failed: {output}")
    except Exception as e:
        if window_alive:
            adb_status_var.set("⚠️ ADB Error")
            adb_status_label.configure(foreground="orange")
       # print(f"❌ ADB failed to connect to WSA. Is WSA running?\n{e}")

def create_controller():
    global adb_status_var, adb_status_label  # Declare as global before use
    
    # Your code continues...
    root = Window(themename="superhero")
    root.title("Key Mapping Controller")
    root.minsize(800, 600)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    # Frame for top section
    frame_top = ttk.Frame(root, padding=10)
    frame_top.grid(row=0, column=0, sticky="ew")
    frame_top.columnconfigure(1, weight=1)
    frame_top.columnconfigure(3, weight=1)

    ttk.Label(frame_top, text="Key:").grid(row=0, column=0, padx=5, pady=5)
    key_var = StringVar()
    key_entry = ttk.Entry(frame_top, textvariable=key_var, width=10)
    key_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(frame_top, text="Action Type:").grid(row=0, column=2, padx=5, pady=5)
    action_type_var = StringVar(value="Single Tap")
    action_menu = ttk.Combobox(
        frame_top,
        textvariable=action_type_var,
        values=["Single Tap", "Multiple Taps", "Scroll", "Long Press", "Swipe"],
        state="readonly"
    )
    action_menu.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    def add_key():
        key = key_var.get().strip().lower()
        if not key:
            return
        if key in key_to_touch:
            messagebox.showinfo("Duplicate Key", f"Key '{key.upper()}' is already mapped.")
            return
        selected_type = action_type_var.get().lower()
        if selected_type == "single tap":
            key_to_touch[key] = (0, 0)
        elif selected_type == "long press":
            key_to_touch[key] = {"type": "long_press", "x": 0, "y": 0, "duration": 1000}
        elif selected_type == "multiple taps":
            key_to_touch[key] = {"type": "multiple_taps", "x": 0, "y": 0, "count": 2}
        elif selected_type in ["swipe", "scroll"]:
            key_to_touch[key] = {
                "type": selected_type,
                "start_x": 0, "start_y": 0,
                "end_x": 0, "end_y": 0,
                "duration": 300
            }
       # print(f"✅ Added mapping: {key} -> {key_to_touch[key]}")
        update_key_buttons()
        key_var.set("")
        action_type_var.set("Single Tap")

    def reset_fields():
        key_to_touch.clear()
        update_key_buttons()
        key_var.set("")
        action_type_var.set("Single Tap")

    ttk.Button(frame_top, text="Add", command=add_key).grid(row=0, column=4, padx=5)
    ttk.Button(frame_top, text="Reset", command=reset_fields).grid(row=0, column=5, padx=5)
    root.bind("<Return>", lambda event: add_key())

    # Frame for the key list and buttons
    outer_frame = ttk.Frame(root, padding=10)
    outer_frame.grid(row=1, column=0, sticky="nsew")
    outer_frame.columnconfigure(0, weight=1)
    outer_frame.rowconfigure(0, weight=1)

    # Initialize the frame for update_key_buttons
    update_key_buttons.frame = outer_frame

    update_key_buttons()

    # Bottom section for saving/loading
    frame_bottom = ttk.Frame(root, padding=10)
    frame_bottom.grid(row=2, column=0, sticky="ew")

    ttk.Button(frame_bottom, text="Save Config", command=save_config).grid(row=0, column=0, padx=5)
    ttk.Button(frame_bottom, text="Load Config", command=load_config).grid(row=0, column=1, padx=5)

    adb_status_var = StringVar(value="ADB: Not Connected")
    ttk.Button(frame_bottom, text="Connect ADB", command=lambda: connect_adb(force=True)).grid(row=1, column=0, padx=5, pady=(10, 0))
    adb_status_label = ttk.Label(frame_bottom, textvariable=adb_status_var)
    adb_status_label.grid(row=1, column=1, padx=5, pady=(10, 0))

    root.after(300, connect_adb)

    def on_close():
        global window_alive
        window_alive = False
        try:
            root.destroy()
        except:
            pass

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
