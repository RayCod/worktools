import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import socket
import psutil
import json
import datetime # Import datetime for timestamps

class ForceBindIPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ForceBindIP GUI")
        self.root.geometry("880x440")
        self.root.resizable(False, False)
        self.config_file = "forcebindip_configs.json" # Use a distinct config file name
        self.max_configs = 10 # Maximum number of configurations to store

        # ForceBindIP 路径
        tk.Label(root, text="ForceBindIP Path:").grid(row=0, column=0, sticky="e")
        self.fbind_path_var = tk.StringVar(value=r"C:/Program Files (x86)/ForceBindIP/ForceBindIP64.exe")
        tk.Entry(root, textvariable=self.fbind_path_var, width=60).grid(row=0, column=1, padx=5)
        tk.Button(root, text="Select", command=self.select_fbind).grid(row=0, column=2)

        # 32/64位选择
        self.is_64bit = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="64-bit ForceBindIP", variable=self.is_64bit, command=self.toggle_fbind).grid(row=0, column=3)

        # IP/GUID
        tk.Label(root, text="IP Address or GUID:").grid(row=1, column=0, sticky="e")
        self.ip_var = tk.StringVar()
        tk.Entry(root, textvariable=self.ip_var, width=40).grid(row=1, column=1, padx=5, sticky="w")
        self.ip_combo = tk.StringVar()
        # 初始化下拉框内容
        ip_choices = [f"{iface} ({ip})" for iface, ip in self.get_local_ips()]
        self.ip_optionmenu = tk.OptionMenu(root, self.ip_combo, *ip_choices, command=self.set_ip_from_combo)
        self.ip_optionmenu.config(width=18)
        self.ip_optionmenu.grid(row=1, column=2, sticky="w")
        tk.Button(root, text="Refresh IP", command=self.refresh_ip_list).grid(row=1, column=3, sticky="w")

        # -i 参数
        self.use_i = tk.BooleanVar()
        tk.Checkbutton(root, text="Use -i parameter", variable=self.use_i).grid(row=2, column=1, sticky="w")

        # 目标程序
        tk.Label(root, text="Target Program Path:").grid(row=3, column=0, sticky="e")
        self.target_var = tk.StringVar()
        tk.Entry(root, textvariable=self.target_var, width=60).grid(row=3, column=1, padx=5)
        tk.Button(root, text="Select", command=self.select_target).grid(row=3, column=2)

        # 目标参数
        tk.Label(root, text="Target Arguments:").grid(row=4, column=0, sticky="e")
        self.args_var = tk.StringVar()
        tk.Entry(root, textvariable=self.args_var, width=60).grid(row=4, column=1, padx=5, columnspan=3)

        # Start in 目录
        tk.Label(root, text="Start in Directory:").grid(row=5, column=0, sticky="e")
        self.startin_var = tk.StringVar()
        tk.Entry(root, textvariable=self.startin_var, width=60).grid(row=5, column=1, padx=5)
        tk.Button(root, text="Select", command=self.select_startin).grid(row=5, column=2, padx=5, pady=2)

        # --- Button Frame for Generate, Run, Save, Load ---
        button_frame = tk.Frame(root)
        # Place this frame in row 6, spanning across available columns
        # We'll use columnspan=5 to give maximum horizontal space
        button_frame.grid(row=6, column=0, columnspan=5, pady=5, sticky="w")

        # Buttons placed inside the frame using pack()
        tk.Button(button_frame, text="Generate Command", command=self.generate_cmd).pack(side="left", padx=(5, 2))
        tk.Button(button_frame, text="Run", command=self.run_cmd).pack(side="left", padx=(2, 5))
        tk.Button(button_frame, text="Save Config", command=self.save_config).pack(side="left", padx=(5, 2))
        tk.Button(button_frame, text="Load Config", command=self.show_load_dialog).pack(side="left", padx=(2, 5))
        # --- End Button Frame ---

        # Command Display (shifted up by 1 row)
        tk.Label(root, text="Command Line:").grid(row=7, column=0, sticky="ne", padx=5, pady=(10, 2))
        self.cmd_text = tk.Text(root, height=2, width=80)
        # Span across columns 1 to 4 (matching the frame's columnspan) in row 7
        self.cmd_text.grid(row=7, column=1, columnspan=4, padx=5, pady=(10, 2))

        # Log Display (shifted up by 1 row)
        tk.Label(root, text="Run Log:").grid(row=8, column=0, sticky="ne", padx=5, pady=5)
        self.log_text = tk.Text(root, height=6, width=80)
        # Span across columns 1 to 4 in row 8
        self.log_text.grid(row=8, column=1, columnspan=4, padx=5, pady=5)

        # ForceBindIP Download URL (shifted up by 1 row)
        self.download_url = "https://r1ch.net/projects/forcebindip"
        link_label = tk.Label(root, text="ForceBindIP Official Download: " + self.download_url, fg="blue", cursor="hand2")
        # Span across columns 0 to 4 in row 9
        link_label.grid(row=9, column=0, columnspan=5, sticky="w", padx=10, pady=5)

        # 作者信息 (shifted up by 1 row)
        author_label = tk.Label(root, text="Author: RayCod", fg="gray")
        # Span across columns 0 to 4 in row 10
        author_label.grid(row=10, column=0, columnspan=5, sticky="w", padx=10, pady=(0, 8))

        link_label.bind("<Button-1>", lambda e: self.open_url())

        self._load_configs_on_start()

    def select_fbind(self):
        path = filedialog.askopenfilename(title="Select ForceBindIP.exe", filetypes=[("Executable files", "*.exe")])
        if path:
            self.fbind_path_var.set(path)
            self.is_64bit.set("ForceBindIP64" in os.path.basename(path))

    def toggle_fbind(self):
        path = self.fbind_path_var.get()
        if path:
            dirname = os.path.dirname(path)
            if self.is_64bit.get():
                new_path = os.path.join(dirname, "ForceBindIP64.exe")
            else:
                new_path = os.path.join(dirname, "ForceBindIP.exe")
            if os.path.exists(new_path):
                self.fbind_path_var.set(new_path)

    def select_target(self):
        path = filedialog.askopenfilename(title="Select Target Program", filetypes=[("Executable files", "*.exe")])
        if path:
            self.target_var.set(path)
            self.startin_var.set(os.path.dirname(path))

    def select_startin(self):
        path = filedialog.askdirectory(title="Select Start in Directory")
        if path:
            self.startin_var.set(path)

    def generate_cmd(self):
        fbind = self.fbind_path_var.get()
        ip = self.ip_var.get()
        target = self.target_var.get()
        args = self.args_var.get()
        use_i = self.use_i.get()
        if not (fbind and ip and target):
            messagebox.showerror("Error", "ForceBindIP path, IP/GUID, and target program cannot be empty!")
            return
        cmd = f'"{fbind}"'
        if use_i:
            cmd += " -i"
        cmd += f' {ip} "{target}"'
        if args.strip():
            cmd += f' {args.strip()}'
        self.cmd_text.delete(1.0, tk.END)
        self.cmd_text.insert(tk.END, cmd)
        return cmd

    def run_cmd(self):
        cmd = self.generate_cmd()
        if not cmd:
            return
        startin = self.startin_var.get() or os.path.dirname(self.target_var.get())
        try:
            self.log_text.insert(tk.END, f"Running command: {cmd}\n")
            self.log_text.see(tk.END)
            subprocess.Popen(cmd, cwd=startin, shell=True)
            self.log_text.insert(tk.END, "Target program started.\n")
            self.log_text.see(tk.END)
        except Exception as e:
            self.log_text.insert(tk.END, f"Start failed: {e}\n")
            self.log_text.see(tk.END)

    def get_local_ips(self):
        # 返回 [(iface, ip), ...]
        ip_list = []
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    ip_list.append((iface, addr.address))
        return ip_list

    def set_ip_from_combo(self, value):
        # value 形如 "网卡名称 (IP地址)"
        if value.endswith(")") and "(" in value:
            ip = value.split("(")[-1].rstrip(")")
            self.ip_var.set(ip)
        else:
            self.ip_var.set(value)

    def refresh_ip_list(self):
        menu = self.ip_optionmenu['menu']
        menu.delete(0, 'end')
        for iface, ip in self.get_local_ips():
            label = f"{iface} ({ip})"
            menu.add_command(label=label, command=lambda v=label: self.set_ip_from_combo(v))

    def open_url(self):
        import webbrowser
        webbrowser.open(self.download_url)

    def save_config(self):
        fbind = self.fbind_path_var.get()
        ip_display = self.ip_combo.get() # Use the text from the OptionMenu
        target = self.target_var.get()
        args = self.args_var.get()
        startin = self.startin_var.get()
        use_i = self.use_i.get()

        if not (fbind and ip_display and target):
            messagebox.showerror("Error", "ForceBindIP path, IP/GUID, and target program cannot be empty!")
            return

        # Generate unique config name
        ip_part = ip_display.split(" (")[0] if " (" in ip_display else ip_display # Extract interface name if available
        program_name = os.path.basename(target)
        config_name = f"{ip_part} - {program_name}"

        # Load existing configs
        configs = self._read_configs_from_file()

        # Add/Update current config with timestamp
        configs[config_name] = {
            "fbind_path": fbind,
            "is_64bit": self.is_64bit.get(),
            "ip": self.ip_var.get(), # Save the actual IP/GUID string
            "ip_display": ip_display, # Save the display string for loading dropdown
            "target": target,
            "args": args,
            "startin": startin,
            "use_i": use_i,
            "timestamp": datetime.datetime.now().isoformat() # Add timestamp for recency
        }

        # Keep only the latest max_configs, sorted by timestamp
        sorted_configs = sorted(configs.items(), key=lambda item: item[1].get("timestamp", ""), reverse=True)
        if len(sorted_configs) > self.max_configs:
            configs = dict(sorted_configs[:self.max_configs])
        else:
            configs = dict(sorted_configs)

        # Save updated configs back to file
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            self.log_text.insert(tk.END, f"Config \'{config_name}\' saved!\n")
            self.log_text.see(tk.END)
        except Exception as e:
            self.log_text.insert(tk.END, f"Save config failed: {e}\n")
            self.log_text.see(tk.END)

    def _read_configs_from_file(self):
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            self.log_text.insert(tk.END, f"Failed to read config file: {e}\n")
            self.log_text.see(tk.END)
            return {}

    def _load_configs_on_start(self):
        # This function is called once on startup to load the latest config if available
        configs = self._read_configs_from_file()
        if not configs:
            return
        # Find the most recent config by timestamp
        latest_config_name = None
        latest_timestamp = ""
        for name, config in configs.items():
            timestamp = config.get("timestamp", "")
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_config_name = name

        if latest_config_name:
            self._apply_config(configs[latest_config_name])
            self.log_text.insert(tk.END, f"Loaded latest config: \'{latest_config_name}\'\n")
            self.log_text.see(tk.END)

    def show_load_dialog(self):
        configs = self._read_configs_from_file()
        if not configs:
            messagebox.showinfo("Load Configuration", "No saved configurations found.")
            return

        # Sort configurations by timestamp (most recent first)
        sorted_configs = sorted(configs.items(), key=lambda item: item[1].get("timestamp", ""), reverse=True)

        # Extract config names for the dialog
        config_names = [name for name, _ in sorted_configs]

        # Create a simple dialog to select config
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Configuration to Load")
        dialog.transient(self.root) # Keep dialog on top of the main window
        dialog.grab_set() # Modal dialog

        listbox_frame = tk.Frame(dialog)
        listbox_frame.pack(padx=10, pady=5, fill="both", expand=True)

        listbox = tk.Listbox(listbox_frame, width=50, height=min(len(config_names), 10))
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)

        for name in config_names:
            listbox.insert(tk.END, name)

        def on_select():
            selection_index = listbox.curselection()
            if selection_index:
                selected_name = listbox.get(selection_index[0])
                # Find the full config data by name
                selected_config_data = configs.get(selected_name)
                if selected_config_data:
                    self._apply_config(selected_config_data)
                    self.log_text.insert(tk.END, f"Loaded config: \'{selected_name}\'\n")
                    self.log_text.see(tk.END)
                else:
                    self.log_text.insert(tk.END, f"Error: Configuration \'{selected_name}\' details not found\n")
                    self.log_text.see(tk.END)
                    messagebox.showerror("Error", f"Configuration \'{selected_name}\' details not found")
                dialog.destroy()
            else:
                messagebox.showwarning("Select Configuration", "Please select a configuration to load.")

        def on_cancel():
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Load", command=on_select).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)

        # Center the dialog window
        dialog.update_idletasks()  # Update to get accurate widget sizes
        main_window_x = self.root.winfo_x()
        main_window_y = self.root.winfo_y()
        main_window_width = self.root.winfo_width()
        main_window_height = self.root.winfo_height()

        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        # Calculate position for centering relative to the main window
        center_x = main_window_x + main_window_width // 2
        center_y = main_window_y + main_window_height // 2

        # Calculate top-left corner position for the dialog
        dialog_x = center_x - dialog_width // 2
        dialog_y = center_y - dialog_height // 2

        dialog.geometry(f'+{dialog_x}+{dialog_y}')

        self.root.wait_window(dialog) # Wait for the dialog to close

    def _apply_config(self, config_data):
        # Apply loaded configuration data to the GUI elements
        self.fbind_path_var.set(config_data.get("fbind_path", ""))
        is_64bit = config_data.get("is_64bit", True)
        self.is_64bit.set(is_64bit)
        # Manually call toggle_fbind to update path based on bitness if needed
        # self.toggle_fbind() # This might prompt user, maybe only update var
        # Re-set fbind path after toggle to ensure it's the saved one if exists
        loaded_fbind_path = config_data.get("fbind_path", "")
        if os.path.exists(loaded_fbind_path):
             self.fbind_path_var.set(loaded_fbind_path)
        else:
             # If saved path doesn't exist, fall back to default based on bitness
             dirname = os.path.dirname(self.fbind_path_var.get()) # Get current dirname
             if is_64bit:
                 default_path = os.path.join(dirname, "ForceBindIP64.exe")
             else:
                 default_path = os.path.join(dirname, "ForceBindIP.exe")
             if os.path.exists(default_path):
                  self.fbind_path_var.set(default_path)
             else:
                  self.fbind_path_var.set("") # Clear if neither exists

        # Set IP, target, args, startin, use_i
        self.ip_var.set(config_data.get("ip", ""))
        # Set the display string in the dropdown if it exists in the current list
        loaded_ip_display = config_data.get("ip_display", "")
        current_ips = [f"{iface} ({ip})" for iface, ip in self.get_local_ips()]
        if loaded_ip_display in current_ips:
             self.ip_combo.set(loaded_ip_display)
        else:
            # If saved IP display is not in current list, clear it or try to find by IP
             saved_ip_address = config_data.get("ip", "")
             found_display = ""
             for display in current_ips:
                 if saved_ip_address in display:
                     found_display = display
                     break
             if found_display:
                 self.ip_combo.set(found_display)
             else:
                  self.ip_combo.set("") # Clear dropdown if IP not found

        self.target_var.set(config_data.get("target", ""))
        self.args_var.set(config_data.get("args", ""))
        self.startin_var.set(config_data.get("startin", ""))
        self.use_i.set(config_data.get("use_i", False))

if __name__ == "__main__":
    root = tk.Tk()
    app = ForceBindIPGUI(root)
    root.mainloop() 
