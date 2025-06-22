from pynput import mouse, keyboard
from threading import Thread
import gui_helpers
from tkinter import ttk, messagebox
from adb_actions import simulate_touch  # Make sure this import is correct


def on_press(key):
    try:
        if hasattr(key, 'char') and key.char in gui_helpers.key_to_touch:
            action = gui_helpers.key_to_touch[key.char]
        elif hasattr(key, 'name') and key.name in gui_helpers.key_to_touch:
            action = gui_helpers.key_to_touch[key.name]
        else:
            return  # Exit early if not found

       # print(f"🔑 Pressed {key}, executing action: {action}")  # ✅ Now it's safe

        if isinstance(action, tuple) and len(action) == 2:
            from adb_actions import simulate_touch
            simulate_touch(*action)

        elif isinstance(action, dict):
            from adb_actions import simulate_scroll, simulate_long_press, simulate_multiple_taps

            action_type = action.get("type")
            if action_type == "scroll" or action_type == "swipe":
                simulate_scroll(
                    action.get("start_x", 0),
                    action.get("start_y", 0),
                    action.get("end_x", 0),
                    action.get("end_y", 0),
                    action.get("duration", 300),
                )
            elif action_type == "long_press":
                simulate_long_press(
                    action.get("x", 0),
                    action.get("y", 0),
                    action.get("duration", 1000),
                )
            elif action_type == "multiple_taps":
                simulate_multiple_taps(
                    action.get("x", 0),
                    action.get("y", 0),
                    action.get("count", 2)
                )

    except Exception as e:
        messagebox.showerror(f"❌ Error in on_press: {e}")

def on_release(key):
    if key == keyboard.Key.esc:
        return False


def on_mouse_click(x, y, button, pressed):
    if pressed and gui_helpers.current_key:
        gui_helpers.key_to_touch[gui_helpers.current_key] = (x, y)
        #print(f"✅ Set coordinates for {gui_helpers.current_key}: ({x}, {y})")
        gui_helpers.current_key = None
        gui_helpers.update_key_buttons()

def start_listeners():
    keyboard_thread = Thread(target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).start())
    keyboard_thread.daemon = True
    keyboard_thread.start()

    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    mouse_listener.start()
