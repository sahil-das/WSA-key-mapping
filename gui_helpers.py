import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from pynput import mouse

key_to_touch = {}
current_key = None
conditional_mappings = {}

def remove_key(key):
    if key in key_to_touch:
        del key_to_touch[key]
        print(f"❌ Removed key: {key}")
        if hasattr(update_key_buttons, "frame"):
            update_key_buttons()
        else:
            print("⚠️ update_key_buttons.frame not set. GUI can't be updated yet.")

def set_coordinates(key):
    global current_key
    action = key_to_touch.get(key)
    if isinstance(action, dict):
        messagebox.showwarning("Edit Required", "⚠️ Only 'Single Tap' actions can use Set.\nUse Edit instead.")
        return
    current_key = key
    print(f"🖱️ Click on screen to set coordinates for key: {key.upper()}")

    def on_click(x, y, button, pressed):
        global current_key
        if pressed and current_key:
            key_to_touch[current_key] = (x, y)
            print(f"✅ Set coordinates for {current_key}: ({x}, {y})")
            current_key = None
            if hasattr(update_key_buttons, "frame"):
                update_key_buttons()
            listener.stop()

    listener = mouse.Listener(on_click=on_click)
    listener.start()

def edit_key_action(key):
    action = key_to_touch[key]
    win = Toplevel()
    win.title(f"Edit Action for {key.upper()}")

    ttk.Label(win, text="Action Type:").grid(row=0, column=0, padx=5, pady=5)
    action_type_var = tk.StringVar(value="Single Tap")
    if isinstance(action, dict) and "type" in action:
        action_type_var.set(action["type"].replace("_", " ").title())

    action_type_menu = ttk.Combobox(
        win, textvariable=action_type_var,
        values=["Single Tap", "Multiple Taps", "Scroll", "Long Press", "Swipe", "Continuous press"],
        state="readonly"
    )
    action_type_menu.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(win, text="Start (X, Y):").grid(row=1, column=0, padx=5, pady=5)
    start_entry = ttk.Entry(win)
    start_entry.grid(row=1, column=1, padx=5, pady=5)

    capture_start_btn = ttk.Button(win, text="Capture Start", command=lambda: capture_click(start_entry))
    capture_start_btn.grid(row=1, column=2, padx=5, pady=5)

    end_label = ttk.Label(win, text="End (X, Y):")
    end_entry = ttk.Entry(win)
    capture_end_btn = ttk.Button(win, text="Capture End", command=lambda: capture_click(end_entry))

    duration_label = ttk.Label(win, text="Duration / Count:")
    duration_entry = ttk.Entry(win)

    def toggle_fields(*args):
        t = action_type_var.get().lower().replace(" ", "_")
        for widget in [end_label, end_entry, capture_end_btn, duration_label, duration_entry]:
            widget.grid_remove()

        if t in ["scroll", "swipe"]:
            end_label.grid(row=2, column=0, padx=5, pady=5)
            end_entry.grid(row=2, column=1, padx=5, pady=5)
            capture_end_btn.grid(row=2, column=2, padx=5, pady=5)
            duration_label.grid(row=3, column=0, padx=5, pady=5)
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
        elif t in ["long_press", "multiple_taps"]:
            duration_label.grid(row=3, column=0, padx=5, pady=5)
            duration_entry.grid(row=3, column=1, padx=5, pady=5)
        elif t == "continuous_click":
            # No extra fields needed
            pass

    action_type_var.trace_add("write", toggle_fields)

    # Pre-fill values safely
    if isinstance(action, dict):
        t = action.get("type", "single_tap").lower()
        if t in ["scroll", "swipe"]:
            start_entry.insert(0, f"{action.get('start_x', 0)}, {action.get('start_y', 0)}")
            end_entry.insert(0, f"{action.get('end_x', 0)}, {action.get('end_y', 0)}")
            duration_entry.insert(0, str(action.get("duration", 300)))
        elif t == "long_press":
            start_entry.insert(0, f"{action.get('x', 0)}, {action.get('y', 0)}")
            duration_entry.insert(0, str(action.get("duration", 1000)))
        elif t == "multiple_taps":
            start_entry.insert(0, f"{action.get('x', 0)}, {action.get('y', 0)}")
            duration_entry.insert(0, str(action.get("count", 2)))
        elif t == "continuous_click":
            x = action.get("x", 0)
            y = action.get("y", 0)
            if isinstance(x, int) and isinstance(y, int):
                start_entry.insert(0, f"{x}, {y}")
    elif isinstance(action, tuple):
        start_entry.insert(0, f"{action[0]}, {action[1]}")

    def capture_click(entry):
        def on_click(x, y, button, pressed):
            if pressed:
                entry.after(0, lambda: entry.delete(0, tk.END))
                entry.after(0, lambda: entry.insert(0, f"{x}, {y}"))
                listener.stop()
        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def save_action():
        try:
            t = action_type_var.get().lower().replace(" ", "_")
            coords = start_entry.get().split(",")
            if len(coords) != 2:
                raise ValueError("Invalid coordinates format. Use 'x, y'")
            x, y = map(int, coords)

            if t in ["swipe", "scroll"]:
                ex, ey = map(int, end_entry.get().split(","))
                duration = int(duration_entry.get())
                key_to_touch[key] = {
                    "type": t,
                    "start_x": x, "start_y": y,
                    "end_x": ex, "end_y": ey,
                    "duration": duration
                }
            elif t == "long_press":
                duration = int(duration_entry.get())
                key_to_touch[key] = {"type": t, "x": x, "y": y, "duration": duration}
            elif t == "multiple_taps":
                count = int(duration_entry.get())
                key_to_touch[key] = {"type": t, "x": x, "y": y, "count": count}
            elif t == "continuous_press":
                key_to_touch[key] = {"type": t, "x": x, "y": y}
            elif t == "single_tap":
                key_to_touch[key] = (x, y)
            else:
                raise ValueError("Unknown action type selected.")
            print(f"✅ Updated action for {key}: {key_to_touch[key]}")
            update_key_buttons()
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    ttk.Button(win, text="Save", command=save_action).grid(row=5, column=0, columnspan=3, pady=10)
    toggle_fields()


def update_key_buttons():
    if not hasattr(update_key_buttons, "frame"):
        print("⚠️ update_key_buttons.frame not set. GUI can't be updated yet.")
        return

    frame = update_key_buttons.frame
    for widget in frame.winfo_children():
        widget.destroy()

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    for idx, (key, action) in enumerate(key_to_touch.items()):
        row_frame = ttk.Frame(scrollable_frame)
        row_frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=4)
        row_frame.columnconfigure(0, weight=3)
        row_frame.columnconfigure(1, weight=1)
        row_frame.columnconfigure(2, weight=1)
        row_frame.columnconfigure(3, weight=1)

        ttk.Label(row_frame, text=f"{key.upper()}: {action}", wraplength=600, anchor="w", justify="left")\
            .grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(row_frame, text="Set", command=lambda k=key: set_coordinates(k)).grid(row=0, column=1, padx=2, sticky="ew")
        ttk.Button(row_frame, text="Edit", command=lambda k=key: edit_key_action(k)).grid(row=0, column=2, padx=2, sticky="ew")
        ttk.Button(row_frame, text="Remove", command=lambda k=key: remove_key(k)).grid(row=0, column=3, padx=2, sticky="ew")
