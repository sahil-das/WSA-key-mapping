import os
import json
from pynput import keyboard, mouse
import tkinter as tk
from tkinter import filedialog
from threading import Thread
from PyQt5.QtWidgets import QApplication, QFileDialog

def auto_connect_wsa():
    """Automatically connect to WSA and verify connection."""
    print("Connecting to WSA (127.0.0.1:58526)...")
    os.system("adb connect 127.0.0.1:58526")

    # Check if device is listed
    result = os.popen("adb devices").read()
    if "127.0.0.1:58526" in result and "device" in result:
        print("✅ ADB successfully connected to WSA.")
    else:
        print("❌ ADB failed to connect to WSA. Is WSA running?")

# Default path for configuration files
CONFIG_DIR = "configs"
os.makedirs(CONFIG_DIR, exist_ok=True)  # Ensure the directory exists

# Define key-to-touch mapping (initially empty, loaded from the config file)
key_to_touch = {}

# Mapping of key names to descriptive labels
KEY_DESCRIPTIONS = {
    "right_click": "Mouse Right Click",
    "left_click": "Mouse Left Click",
    "middle_click": "Mouse Middle Click",
    "up": "Up Arrow",
    "down": "Down Arrow",
    "left": "Left Arrow",
    "right": "Right Arrow",
}

# Variable to track which key is being updated
current_key = None

# Global flag to track if the GUI needs an update
gui_needs_update = False

# Global variable to hold the QApplication instance
qt_app = None

def load_config(filepath=None):
    """
    Load key-to-touch mapping from a configuration file.
    If no filepath is provided, a file dialog is opened to select the file.
    """
    global key_to_touch

    if filepath is None:
        # Use tkinter's filedialog for file selection
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.update_idletasks()  # Ensure proper scaling
        filepath = filedialog.askopenfilename(
            title="Select Configuration File",  # Dialog title
            initialdir=CONFIG_DIR,  # Initial directory
            filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))  # File type filters
        )
        root.destroy()  # Destroy the root window after the dialog is closed

    if filepath and os.path.exists(filepath):
        with open(filepath, "r") as file:
            try:
                loaded_config = json.load(file)
                # Normalize keys to match keyboard.Key names
                key_to_touch.clear()
                for key, action in loaded_config.items():
                    if isinstance(action, list) and len(action) == 2:
                        # Convert single-tap actions from lists to tuples
                        key_to_touch[key] = tuple(action)
                    elif key in keyboard.Key.__members__:
                        key_to_touch[keyboard.Key[key].name] = action
                    else:
                        key_to_touch[key] = action
                print(f"Configuration loaded from {filepath}: {key_to_touch}")
                update_key_buttons()  # Refresh the GUI with the loaded data
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the configuration file.")
    else:
        print("No configuration file selected or file does not exist.")

def load_default_config():
    """
    Load the default configuration file on startup.
    The default configuration is stored in 'configs/default.json'.
    """
    global key_to_touch
    filepath = os.path.join(CONFIG_DIR, "default.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            try:
                key_to_touch = json.load(file)
                print(f"Default configuration loaded from {filepath}: {key_to_touch}")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in the default configuration file.")

def save_config(filepath=None):
    """
    Save the current key-to-touch mapping to a configuration file.
    If no filepath is provided, a file dialog is opened to select the save location.
    """
    global key_to_touch
    if filepath is None:
        filepath = filedialog.asksaveasfilename(initialdir=CONFIG_DIR, title="Save Configuration File",
                                                defaultextension=".json",
                                                filetypes=(("JSON Files", "*.json"), ("All Files", "*.*")))
    if filepath:
        with open(filepath, "w") as file:
            json.dump(key_to_touch, file)
            print(f"Configuration saved to {filepath}: {key_to_touch}")

def simulate_touch(x, y):
    """
    Simulate a single touch event at the specified (x, y) coordinates using ADB.
    """
    print(f"Simulating touch at: {x}, {y}")
    os.system(f"adb shell input tap {x} {y}")

def simulate_multiple_taps(x, y, count=2):
    """
    Simulate multiple taps at the same location using ADB.
    :param x: X-coordinate of the tap.
    :param y: Y-coordinate of the tap.
    :param count: Number of taps to simulate.
    """
    print(f"Simulating {count} taps at: {x}, {y}")
    for _ in range(count):
        os.system(f"adb shell input tap {x} {y}")

def simulate_scroll(start_x, start_y, end_x, end_y, duration=300):
    """
    Simulate a scroll/swipe gesture using ADB.
    :param start_x: Starting X-coordinate of the swipe.
    :param start_y: Starting Y-coordinate of the swipe.
    :param end_x: Ending X-coordinate of the swipe.
    :param end_y: Ending Y-coordinate of the swipe.
    :param duration: Duration of the swipe in milliseconds.
    """
    print(f"Simulating scroll from ({start_x}, {start_y}) to ({end_x}, {end_y}) over {duration}ms")
    os.system(f"adb shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}")

def simulate_long_press(x, y, duration=1000):
    """
    Simulate a long press at the specified (x, y) coordinates using ADB.
    :param x: X-coordinate of the long press.
    :param y: Y-coordinate of the long press.
    :param duration: Duration of the long press in milliseconds.
    """
    print(f"Simulating long press at: ({x}, {y}) for {duration}ms")
    os.system(f"adb shell input swipe {x} {y} {x} {y} {duration}")

def on_press(key):
    """
    Handle key press events.
    Perform the action associated with the pressed key.
    """
    global gui_needs_update
    try:
        # Normalize the key name
        if hasattr(key, 'char') and key.char in key_to_touch:
            action = key_to_touch[key.char]
        elif hasattr(key, 'name') and key.name in key_to_touch:
            action = key_to_touch[key.name]
        else:
            # Silently ignore keys without configured actions
            return

        # Perform the action
        if isinstance(action, tuple) and len(action) == 2:
            # Single touch
            simulate_touch(*action)
        elif isinstance(action, dict):
            # Handle advanced actions
            if action.get("type") == "multiple_taps":
                simulate_multiple_taps(action["x"], action["y"], action.get("count", 2))
            elif action.get("type") == "scroll":
                simulate_scroll(action["start_x"], action["start_y"], action["end_x"], action["end_y"], action.get("duration", 300))
            elif action.get("type") == "long_press":
                simulate_long_press(action["x"], action["y"], action.get("duration", 1000))
            elif action.get("type") == "swipe":
                simulate_scroll(action["start_x"], action["start_y"], action["end_x"], action["end_y"], action.get("duration", 300))

        # Update the GUI only if needed
        if gui_needs_update:
            update_key_buttons()
            gui_needs_update = False  # Reset the flag
    except Exception as e:
        print(f"Error: {e}")

def on_release(key):
    """
    Handle key release events.
    Stop the listener if the 'esc' key is released.
    """
    if key == keyboard.Key.esc:
        return False

def on_mouse_click(x, y, button, pressed):
    """
    Handle mouse click events to set coordinates or trigger actions.
    """
    global current_key, gui_needs_update
    if pressed and current_key:
        # Set coordinates for the current key as a tuple
        key_to_touch[current_key] = (x, y)
        print(f"Updated {current_key} to coordinates: ({x}, {y})")
        current_key = None  # Reset after updating
        gui_needs_update = True  # Mark GUI for update

def set_coordinates(key):
    """Enable coordinate setting for the selected key."""
    global current_key
    action = key_to_touch.get(key)

    # Check if the action is "Single Tap"
    if isinstance(action, tuple) and len(action) == 2:
        current_key = key
        print(f"Click on the screen to set coordinates for {key.upper()}")
    else:
        # Show a warning window for non-"Single Tap" actions
        warning_window = tk.Toplevel()
        warning_window.title("Warning")
        tk.Label(warning_window, text="You can configure this action with the Edit button.").pack(padx=20, pady=10)
        tk.Button(warning_window, text="OK", command=warning_window.destroy).pack(pady=10)

def edit_key_action(key):
    """Edit the action for a specific key."""
    action = key_to_touch[key]

    # Create a new window for editing the action
    edit_window = tk.Toplevel()
    edit_window.title(f"Edit Action for {key.upper()}")

    # Action type dropdown
    tk.Label(edit_window, text="Action Type:").grid(row=0, column=0, padx=5, pady=5)
    action_type_var = tk.StringVar(value="Single Tap")
    if isinstance(action, dict) and "type" in action:
        action_type_var.set(action["type"].capitalize())
    action_type_dropdown = tk.OptionMenu(edit_window, action_type_var, "Single Tap", "Multiple Taps", "Scroll", "Long Press", "Swipe")
    action_type_dropdown.grid(row=0, column=1, padx=5, pady=5)

    # Input fields for start coordinates
    tk.Label(edit_window, text="Start (X, Y):").grid(row=1, column=0, padx=5, pady=5)
    start_entry = tk.Entry(edit_window, width=20)
    start_entry.grid(row=1, column=1, padx=5, pady=5)

    # Input fields for end coordinates (initially hidden)
    end_label = tk.Label(edit_window, text="End (X, Y):")
    end_entry = tk.Entry(edit_window, width=20)

    # Duration field (initially hidden)
    duration_label = tk.Label(edit_window, text="Duration (ms):")
    duration_entry = tk.Entry(edit_window, width=10)

    # Pre-fill parameters based on the current action
    if isinstance(action, dict):
        if action.get("type") in ["swipe", "scroll"]:
            start_entry.insert(0, f"{action.get('start_x', 0)}, {action.get('start_y', 0)}")
            end_entry.insert(0, f"{action.get('end_x', 0)}, {action.get('end_y', 0)}")
            duration_entry.insert(0, action.get("duration", 300))
            end_label.grid(row=2, column=0, padx=5, pady=5)
            end_entry.grid(row=2, column=1, padx=5, pady=5)
            duration_label.grid(row=3, column=0, padx=5, pady=5)
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
        elif action.get("type") == "long_press":
            start_entry.insert(0, f"{action.get('x', 0)}, {action.get('y', 0)}")
            duration_entry.insert(0, action.get("duration", 1000))
            duration_label.grid(row=3, column=0, padx=5, pady=5)
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
        elif action.get("type") == "multiple_taps":
            start_entry.insert(0, f"{action.get('x', 0)}, {action.get('y', 0)}")
            duration_entry.insert(0, action.get("count", 2))
            duration_label.grid(row=3, column=0, padx=5, pady=5)
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
        elif action.get("type") == "single_tap":
            start_entry.insert(0, f"{action[0]}, {action[1]}")

    # Function to toggle visibility of end coordinates and duration based on action type
    def toggle_fields(*args):
        action_type = action_type_var.get().lower()
        if action_type in ["swipe", "scroll"]:
            end_label.grid(row=2, column=0, padx=5, pady=5)
            end_entry.grid(row=2, column=1, padx=5, pady=5)
            duration_label.grid(row=3, column=0, padx=5, pady=5)
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
            capture_end_button.grid(row=2, column=2, padx=5, pady=5)
        elif action_type in ["long press", "multiple taps"]:
            end_label.grid_remove()
            end_entry.grid_remove()
            capture_end_button.grid_remove()
            duration_label.grid(row=3, column=0, padx=5, pady=5)
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
        elif action_type == "single tap":
            end_label.grid_remove()
            end_entry.grid_remove()
            capture_end_button.grid_remove()
            duration_label.grid_remove()
            duration_entry.grid_remove()

    # Bind the dropdown menu to toggle the visibility of fields
    action_type_var.trace("w", toggle_fields)

    # Capture buttons for start and end coordinates
    def capture_start():
        """Capture the start coordinates using mouse click."""
        def on_click(x, y, button, pressed):
            if pressed:
                start_entry.delete(0, tk.END)
                start_entry.insert(0, f"{x}, {y}")
                mouse_listener.stop()

        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

    def capture_end():
        """Capture the end coordinates using mouse click."""
        def on_click(x, y, button, pressed):
            if pressed:
                end_entry.delete(0, tk.END)
                end_entry.insert(0, f"{x}, {y}")
                mouse_listener.stop()

        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

    tk.Button(edit_window, text="Capture Start", command=capture_start).grid(row=1, column=2, padx=5, pady=5)
    capture_end_button = tk.Button(edit_window, text="Capture End", command=capture_end)
    capture_end_button.grid(row=2, column=2, padx=5, pady=5)

    # Save button
    def save_action():
        new_action_type = action_type_var.get().lower()
        try:
            if new_action_type in ["swipe", "scroll"]:
                start_coords = start_entry.get().split(",")
                end_coords = end_entry.get().split(",")
                start_x, start_y = int(start_coords[0].strip()), int(start_coords[1].strip())
                end_x, end_y = int(end_coords[0].strip()), int(end_coords[1].strip())
                duration = int(duration_entry.get())
                key_to_touch[key] = {
                    "type": new_action_type,
                    "start_x": start_x,
                    "start_y": start_y,
                    "end_x": end_x,
                    "end_y": end_y,
                    "duration": duration,
                }
            elif new_action_type == "long press":
                start_coords = start_entry.get().split(",")
                x, y = int(start_coords[0].strip()), int(start_coords[1].strip())
                duration = int(duration_entry.get())
                key_to_touch[key] = {
                    "type": "long_press",
                    "x": x,
                    "y": y,
                    "duration": duration,
                }
            elif new_action_type == "single tap":
                start_coords = start_entry.get().split(",")
                x, y = int(start_coords[0].strip()), int(start_coords[1].strip())
                key_to_touch[key] = (x, y)
            elif new_action_type == "multiple taps":
                start_coords = start_entry.get().split(",")
                x, y = int(start_coords[0].strip()), int(start_coords[1].strip())
                count = int(duration_entry.get())  # Use duration field for tap count
                key_to_touch[key] = {
                    "type": "multiple_taps",
                    "x": x,
                    "y": y,
                    "count": count,
                }
            print(f"Updated action for {key}: {key_to_touch[key]}")
            update_key_buttons()
            edit_window.destroy()
        except ValueError:
            print("Invalid input. Please enter valid numbers for coordinates and duration.")

    tk.Button(edit_window, text="Save", command=save_action).grid(row=4, column=0, columnspan=3, pady=10)

    # Initialize the visibility of fields
    toggle_fields()

def update_key_buttons():
    """Update the key buttons dynamically."""
    for widget in key_frame.winfo_children():
        widget.destroy()  # Clear existing buttons

    for idx, (key, action) in enumerate(key_to_touch.items()):
        if isinstance(action, tuple) and len(action) == 2:
            # Single Tap
            action_text = f"Single Tap ({action[0]}, {action[1]})"
        elif isinstance(action, dict):
            # Advanced actions
            action_type = action.get("type", "Unknown").capitalize()
            if action_type == "Multiple_taps":
                action_text = f"Multiple Taps ({action['x']}, {action['y']}, Count: {action.get('count', 2)})"
            elif action_type == "Scroll":
                action_text = f"Scroll (Start: {action['start_x']}, {action['start_y']} -> End: {action['end_x']}, {action['end_y']}, Duration: {action.get('duration', 300)}ms)"
            elif action_type == "Long_press":
                action_text = f"Long Press ({action['x']}, {action['y']}, Duration: {action.get('duration', 1000)}ms)"
            elif action_type == "Swipe":
                action_text = f"Swipe (Start: {action['start_x']}, {action['start_y']} -> End: {action['end_x']}, {action['end_y']}, Duration: {action.get('duration', 300)}ms)"
            else:
                action_text = f"Unknown Action ({action})"
        else:
            # Unknown action type
            action_text = "Unknown Action"

        # Add the key and action to the GUI
        tk.Label(key_frame, text=f"{key.upper()} - {action_text}").grid(row=idx, column=0, padx=5, pady=5, sticky="w")
        tk.Button(key_frame, text="Set", command=lambda k=key: set_coordinates(k)).grid(row=idx, column=1, padx=5, pady=5, sticky="e")
        tk.Button(key_frame, text="Edit", command=lambda k=key: edit_key_action(k)).grid(row=idx, column=2, padx=5, pady=5, sticky="e")
        tk.Button(key_frame, text="Remove", command=lambda k=key: remove_key(k)).grid(row=idx, column=3, padx=5, pady=5, sticky="e")

def add_key_mapping():
    """Add a new key mapping with the selected action."""
    global gui_needs_update
    key = key_entry.get().strip()  # Get the key from the input field
    action_type = action_type_var.get()  # Get the selected action type

    if key and key not in key_to_touch:  # Ensure the key is not already in the dictionary
        if action_type == "Single Tap":
            key_to_touch[key] = (0, 0)  # Default coordinates for single tap
        elif action_type == "Multiple Taps":
            key_to_touch[key] = {"type": "multiple_taps", "x": 0, "y": 0, "count": 2}
        elif action_type == "Scroll":
            key_to_touch[key] = {"type": "scroll", "start_x": 0, "start_y": 0, "end_x": 0, "end_y": 0, "duration": 300}
        elif action_type == "Long Press":
            key_to_touch[key] = {"type": "long_press", "x": 0, "y": 0, "duration": 1000}
        elif action_type == "Swipe":
            key_to_touch[key] = {"type": "swipe", "start_x": 500, "start_y": 1000, "end_x": 500, "end_y": 500, "duration": 300}
        print(f"Added key: {key} with action: {action_type}")
        gui_needs_update = True  # Mark GUI for update
        update_key_buttons()  # Refresh the GUI to show the new key
    else:
        print("Invalid or duplicate key.")

def remove_key(key):
    """Remove a specific key from the key-to-touch mapping."""
    if key in key_to_touch:
        del key_to_touch[key]
        print(f"Removed key: {key}")
        update_key_buttons()  # Refresh the GUI
    else:
        print(f"Key {key} not found.")

def check_adb_connection():
    """Check if ADB is connected to WSA and update the label."""
    global adb_status_label

    try:
        result = os.popen("adb devices").read()
        if "127.0.0.1:58526" in result and "device" in result:
            adb_status_label.config(text="✅ ADB Connected to WSA", fg="green")
        else:
            adb_status_label.config(text="❌ ADB Not Connected", fg="red")
    except Exception as e:
        adb_status_label.config(text=f"❌ ADB Check Failed: {e}", fg="red")

    # Schedule to check again in 5 seconds
    adb_status_label.after(5000, check_adb_connection)


def create_controller():
    """Create an on-screen game controller with adjustable coordinates."""
    root = tk.Tk()
    root.title("On-Screen Game Controller")
    root.geometry("400x400")
    root.minsize(400, 400)  # Set a minimum size for the window

    global adb_status_label
    adb_status_label = tk.Label(root, text="Checking ADB connection...", fg="orange", font=("Arial", 10, "bold"))
    adb_status_label.pack(pady=5)

    # ✅ Call this AFTER the label is defined
    check_adb_connection()
    global key_frame  # Declare key_frame as global so it can be accessed in update_key_buttons

    # Input field and button to add new keys
    input_frame = tk.Frame(root)
    input_frame.pack(fill="x", padx=10, pady=5)

    # Key input field
    tk.Label(input_frame, text="Add Key:").pack(side="left")
    global key_entry  # Declare key_entry as global so it can be accessed in add_key_mapping
    key_entry = tk.Entry(input_frame, width=10)
    key_entry.pack(side="left", padx=5)

    # Bind the "Enter" key to the add_key_mapping function
    key_entry.bind("<Return>", lambda event: add_key_mapping())

    # Action type dropdown
    tk.Label(input_frame, text="Action:").pack(side="left")
    global action_type_var  # Declare action_type_var as global so it can be accessed in add_key_mapping
    action_type_var = tk.StringVar(value="Single Tap")  # Default value for the dropdown
    action_type_dropdown = tk.OptionMenu(
        input_frame,
        action_type_var,
        "Single Tap",
        "Multiple Taps",
        "Scroll",
        "Long Press",
        "Swipe"  # Only include "Swipe" instead of individual directions
    )
    action_type_dropdown.pack(side="left", padx=5)

    # Add another dropdown menu for key descriptions
    tk.Label(input_frame, text="Key Description:").pack(side="left", padx=5)
    global key_description_var  # Declare key_description_var as global so it can be accessed
    key_description_var = tk.StringVar(value="Select Key")  # Default value for the dropdown
    key_description_dropdown = tk.OptionMenu(
        input_frame,
        key_description_var,
        "right_click -> Mouse Right Click",
        "middle_click -> Mouse Middle Click",
        "up -> Up Arrow",
        "down -> Down Arrow",
        "left -> Left Arrow",
        "right -> Right Arrow"
    )
    key_description_dropdown.pack(side="left", padx=5)

    # Add button
    tk.Button(input_frame, text="Add", command=add_key_mapping).pack(side="left", padx=5)

    # Frame to hold key buttons with scrollbar
    canvas_frame = tk.Frame(root)
    canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(canvas_frame)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Bind mouse wheel scrolling to the canvas
    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    key_frame = scrollable_frame  # Set the scrollable frame as the key_frame

    # Save and Load buttons
    control_frame = tk.Frame(root)
    control_frame.pack(fill="x", padx=10, pady=5)
    tk.Button(control_frame, text="Save Config", command=save_config).pack(side="left", padx=5)
    tk.Button(control_frame, text="Load Config", command=load_config).pack(side="left", padx=5)
    
    # ✅ Reconnect button (place this AFTER control_frame is created)
    tk.Button(control_frame, text="Reconnect ADB", command=auto_connect_wsa).pack(side="left", padx=5)
   
    # Load the initial key buttons
    load_default_config()  # Load the default configuration
    update_key_buttons()

    # Run the tkinter main loop
    root.mainloop()

# Automatically connect to WSA
auto_connect_wsa()

# Start the keyboard listener in a separate thread
listener_thread = Thread(target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).start())
listener_thread.daemon = True
listener_thread.start()

# Start the mouse listener in a separate thread
mouse_listener = mouse.Listener(on_click=on_mouse_click)
mouse_listener.start()

# Start checking ADB connection
#check_adb_connection()

# Launch the on-screen controller
create_controller()