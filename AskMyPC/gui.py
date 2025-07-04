import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import subprocess
from datetime import datetime
import json
import threading

# Import the function from gemini.py
# Note: Ensure gemini.py is in the same directory or in Python's path
try:
    from gemini import get_powershell_command
except ImportError:
    messagebox.showerror("Error", "Could not import 'get_powershell_command' from gemini.py.\nMake sure the file exists and there are no errors in it.")
    exit()

# --- Constants ---
DANGEROUS_KEYWORDS = [
    "shutdown", "restart", "format", "del", "remove-item", "rd /s", "diskpart"
]
LOG_FILE = "command_log.txt"

# --- Main Application Class ---
class AskMyPCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AskMyPC - AI Assistant")
        self.root.geometry("700x600")

        # --- Variables ---
        self.safe_mode = tk.BooleanVar(value=True)
        self.generated_command = ""

        # --- UI Layout ---
        self.create_widgets()

    def create_widgets(self):
        # --- Main Frame ---
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input Frame ---
        input_frame = tk.LabelFrame(main_frame, text="What do you want your PC to do?", padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.input_entry = tk.Entry(input_frame, width=60, font=("Arial", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        self.submit_button = tk.Button(input_frame, text="Submit", command=self.get_ai_command)
        self.submit_button.pack(side=tk.RIGHT, padx=(10, 0))

        # --- Response Frame ---
        response_frame = tk.LabelFrame(main_frame, text="💬 AI Response", padx=10, pady=10)
        response_frame.pack(fill=tk.X, pady=(0, 10))

        self.response_text = tk.Text(response_frame, height=4, wrap=tk.WORD, state=tk.DISABLED, bg="#f0f0f0")
        self.response_text.pack(fill=tk.X, expand=True)

        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        # --- Actions Frame ---
        actions_frame = tk.Frame(main_frame)
        actions_frame.pack(fill=tk.X, pady=(0, 10))

        self.confirm_button = tk.Button(actions_frame, text="✓ Confirm & Run", command=self.run_command, state=tk.DISABLED)
        self.confirm_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.dry_run_button = tk.Button(actions_frame, text="🧪 Dry Run", command=self.dry_run_command, state=tk.DISABLED)
        self.dry_run_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.cancel_button = tk.Button(actions_frame, text="❌ Cancel", command=self.cancel_action, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # --- Settings Frame ---
        settings_frame = tk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.safe_mode_check = tk.Checkbutton(settings_frame, text="⚙️ Safe Mode", variable=self.safe_mode)
        self.safe_mode_check.pack(side=tk.LEFT)

        # --- Logs Frame ---
        logs_frame = tk.LabelFrame(main_frame, text="📜 Logs", padx=10, pady=10)
        logs_frame.pack(fill=tk.BOTH, expand=True)

        self.log_display = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, state=tk.DISABLED, height=10)
        self.log_display.pack(fill=tk.BOTH, expand=True)

    # --- Core Functions ---
    def get_ai_command(self):
        user_input = self.input_entry.get()
        if not user_input:
            messagebox.showwarning("Input Error", "Please enter a command request.")
            return

        self.clear_response()
        self.set_ui_state("loading")
        
        # Run the AI call in a separate thread
        thread = threading.Thread(target=self.threaded_get_ai_command, args=(user_input,))
        thread.start()

    def threaded_get_ai_command(self, user_input):
        response_data = get_powershell_command(user_input)
        
        # Since this is running in a thread, we need to schedule the GUI update
        # on the main thread using `root.after()`
        self.root.after(0, self.update_gui_with_response, response_data)

    def update_gui_with_response(self, response_data):
        if response_data and 'command' in response_data:
            self.generated_command = response_data.get('command', '')
            explanation = response_data.get('explanation', 'No explanation provided.')
            
            self.response_text.config(state=tk.NORMAL)
            self.response_text.insert(tk.END, f"Command:\n{self.generated_command}\n\n")
            self.response_text.insert(tk.END, f"Explanation:\n{explanation}")
            self.response_text.config(state=tk.DISABLED)
            
            self.set_ui_state("ready")
        else:
            messagebox.showerror("API Error", "Failed to get a valid command from the AI.")
            self.set_ui_state("idle")

    def run_command(self):
        if not self.generated_command:
            return

        if self.safe_mode.get() and self.is_dangerous(self.generated_command):
            messagebox.showerror("Safe Mode Block", "This command is blocked in Safe Mode.")
            return

        try:
            # Execute the command using PowerShell
            process = subprocess.run(
                ["powershell", "-Command", self.generated_command],
                capture_output=True, text=True, check=True
            )
            self.log_command(self.generated_command, "Success")
            messagebox.showinfo("Execution Success", f"Command executed successfully.\n\nOutput:\n{process.stdout}")
        except subprocess.CalledProcessError as e:
            self.log_command(self.generated_command, f"Failed (stderr: {e.stderr.strip()})")
            messagebox.showerror("Execution Failed", f"Command failed with error:\n\n{e.stderr}")
        except Exception as e:
            self.log_command(self.generated_command, f"Failed (Exception: {e})")
            messagebox.showerror("Execution Error", f"An unexpected error occurred:\n\n{e}")
        
        self.clear_response()
        self.set_ui_state("idle")

    def dry_run_command(self):
        messagebox.showinfo("Dry Run", f"Dry run: Command not actually executed.\n\nCommand:\n{self.generated_command}")

    def cancel_action(self):
        self.input_entry.delete(0, tk.END)
        self.clear_response()
        self.set_ui_state("idle")

    def log_command(self, command, status):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {command}"
        
        # Log to file
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_entry + "\n")
        except IOError as e:
            messagebox.showwarning("Log Error", f"Could not write to log file: {e}")

        # Log to GUI
        self.log_display.config(state=tk.NORMAL)
        self.log_display.insert(tk.END, log_entry + "\n")
        self.log_display.see(tk.END) # Scroll to the bottom
        self.log_display.config(state=tk.DISABLED)

    # --- Helper Functions ---
    def is_dangerous(self, command):
        lower_command = command.lower()
        return any(keyword in lower_command for keyword in DANGEROUS_KEYWORDS)

    def clear_response(self):
        self.generated_command = ""
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.config(state=tk.DISABLED)

    def set_ui_state(self, state):
        if state == "loading":
            self.submit_button.config(state=tk.DISABLED, text="Loading...")
            self.confirm_button.config(state=tk.DISABLED)
            self.dry_run_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.DISABLED)
            self.progress_bar.start(10)
        elif state == "ready":
            self.submit_button.config(state=tk.NORMAL, text="Submit")
            self.confirm_button.config(state=tk.NORMAL)
            self.dry_run_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)
            self.progress_bar.stop()
        elif state == "idle":
            self.submit_button.config(state=tk.NORMAL, text="Submit")
            self.confirm_button.config(state=tk.DISABLED)
            self.dry_run_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.DISABLED)
            self.progress_bar.stop()


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AskMyPCApp(root)
    root.mainloop()
