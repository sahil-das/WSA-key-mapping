import json
from tkinter import messagebox, filedialog
from gui_helpers import key_to_touch, update_key_buttons

def save_config():
    filepath = filedialog.asksaveasfilename(
        title="Save Config",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    if filepath:
        try:
            with open(filepath, "w") as f:
                json.dump(key_to_touch, f, indent=2)
            print(f"✅ Config saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config:\n{e}")

def load_config():
    filepath = filedialog.askopenfilename(
        title="Load Config",
        filetypes=[("JSON files", "*.json")]
    )
    if filepath:
        try:
            with open(filepath, 'r') as f:
                key_to_touch.clear()
                data = json.load(f)

                # Convert lists to tuples for single tap actions
                for key, val in data.items():
                    if isinstance(val, list) and len(val) == 2:
                        key_to_touch[key] = tuple(val)
                    else:
                        key_to_touch[key] = val

            print(f"✅ Config loaded from {filepath}")
            update_key_buttons()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config:\n{e}")

def load_default_config(default_path="default_config.json"):
    try:
        with open(default_path, "r") as f:
            key_to_touch.clear()
            data = json.load(f)

            # Convert lists to tuples for consistency
            for key, val in data.items():
                if isinstance(val, list) and len(val) == 2:
                    key_to_touch[key] = tuple(val)
                else:
                    key_to_touch[key] = val

        print("✅ Default config loaded")
        update_key_buttons()
    except FileNotFoundError:
        print("⚠️ Default config not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load default config:\n{e}")
