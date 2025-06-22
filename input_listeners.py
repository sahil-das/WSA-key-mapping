from pynput import mouse, keyboard
from threading import Thread
import gui_helpers
from adb_actions import simulate_touch, simulate_scroll, simulate_long_press, simulate_multiple_taps, simulate_continuous_press
from windows_actions import simulate_windows_click, simulate_windows_scroll, simulate_windows_long_press, simulate_windows_multiple_taps, simulate_windows_continuous_press, stop_windows_continuous_press
from gui_helpers import key_to_touch

def on_press(key):
    try:
        from gui import selected_platform
        key_str = getattr(key, 'char', None) or getattr(key, 'name', None)
        if not key_str or key_str not in gui_helpers.key_to_touch:
            return

        action = gui_helpers.key_to_touch[key_str]
        print(f"🔑 Pressed '{key_str}', executing action: {action}")

        if isinstance(action, tuple) and len(action) == 2:
            if selected_platform.get() == "ADB":
                simulate_touch(*action)
            else:
                simulate_windows_click(*action)

        elif isinstance(action, dict):
            action_type = action.get("type")
            if selected_platform.get() == "ADB":
                if action_type in ["scroll", "swipe"]:
                    simulate_scroll(
                        action.get("start_x", 0), action.get("start_y", 0),
                        action.get("end_x", 0), action.get("end_y", 0),
                        action.get("duration", 300)
                    )
                elif action_type == "long_press":
                    simulate_long_press(
                        action.get("x", 0), action.get("y", 0),
                        action.get("duration", 1000)
                    )
                elif action_type == "multiple_taps":
                    simulate_multiple_taps(
                        action.get("x", 0), action.get("y", 0),
                        action.get("count", 2)
                    )
                elif action_type == "continuous_press":
                    simulate_continuous_press(
                        action.get("x", 0), action.get("y", 0),
                        key_str
                    )
            else:
                if action_type in ["scroll", "swipe"]:
                    simulate_windows_scroll(
                        action.get("start_x", 0), action.get("start_y", 0),
                        action.get("end_x", 0), action.get("end_y", 0),
                        action.get("duration", 300)
                    )
                elif action_type == "long_press":
                    simulate_windows_long_press(
                        action.get("x", 0), action.get("y", 0),
                        action.get("duration", 1000)
                    )
                elif action_type == "multiple_taps":
                    simulate_windows_multiple_taps(
                        action.get("x", 0), action.get("y", 0),
                        action.get("count", 2)
                    )
                elif action_type == "continuous_press":
                    simulate_windows_continuous_press(
                        action.get("x", 0), action.get("y", 0),
                        key_str
                    )
    except Exception as e:
        print(f"❌ Error in on_press: {e}")

def on_release(key):
    try:
        from gui import selected_platform
        key_str = getattr(key, 'char', None) or getattr(key, 'name', None)

        if selected_platform.get() == "ADB":
            from adb_actions import stop_continuous_press
            if key_str:
                stop_continuous_press(key_str)
        else:
            if key_str:
                stop_windows_continuous_press(key_str)

        if key == keyboard.Key.esc:
            return False
    except Exception as e:
        print(f"❌ Error in on_release: {e}")

def on_mouse_click(x, y, button, pressed):
    if pressed and gui_helpers.current_key:
        gui_helpers.key_to_touch[gui_helpers.current_key] = (x, y)
        print(f"✅ Set coordinates for {gui_helpers.current_key}: ({x}, {y})")
        gui_helpers.current_key = None
        gui_helpers.update_key_buttons()

def start_listeners():
    keyboard_thread = Thread(target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).start())
    keyboard_thread.daemon = True
    keyboard_thread.start()

    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    mouse_listener.start()
