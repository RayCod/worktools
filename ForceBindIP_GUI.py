import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import socket
import psutil

class ForceBindIPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ForceBindIP GUI")
        self.root.geometry("845x430")
        self.root.resizable(False, False)

        # ForceBindIP 路径，默认64位
        default_fbind64 = r"C:/Program Files (x86)/ForceBindIP/ForceBindIP64.exe"
        self.fbind_path_var = tk.StringVar(value=default_fbind64)
        tk.Label(root, text="ForceBindIP 路径:").grid(row=0, column=0, sticky="e")
        tk.Entry(root, textvariable=self.fbind_path_var, width=60).grid(row=0, column=1, padx=5)
        tk.Button(root, text="选择", command=self.select_fbind).grid(row=0, column=2)

        # 32/64位选择
        self.is_64bit = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="64位 ForceBindIP", variable=self.is_64bit, command=self.toggle_fbind).grid(row=0, column=3)

        # IP/GUID
        tk.Label(root, text="IP地址或GUID:").grid(row=1, column=0, sticky="e")
        self.ip_var = tk.StringVar()
        tk.Entry(root, textvariable=self.ip_var, width=40).grid(row=1, column=1, padx=5, sticky="w")
        self.ip_combo = tk.StringVar()
        self.ip_optionmenu = tk.OptionMenu(root, self.ip_combo, *self.get_local_ips(), command=self.set_ip_from_combo)
        self.ip_optionmenu.config(width=18)
        self.ip_optionmenu.grid(row=1, column=2, sticky="w")
        tk.Button(root, text="刷新IP", command=self.refresh_ip_list).grid(row=1, column=3, sticky="w")

        # -i 参数
        self.use_i = tk.BooleanVar()
        tk.Checkbutton(root, text="使用 -i 参数", variable=self.use_i).grid(row=2, column=1, sticky="w")

        # 目标程序
        tk.Label(root, text="目标程序:").grid(row=3, column=0, sticky="e")
        self.target_var = tk.StringVar()
        tk.Entry(root, textvariable=self.target_var, width=60).grid(row=3, column=1, padx=5)
        tk.Button(root, text="选择", command=self.select_target).grid(row=3, column=2)

        # 目标参数
        tk.Label(root, text="目标程序参数:").grid(row=4, column=0, sticky="e")
        self.args_var = tk.StringVar()
        tk.Entry(root, textvariable=self.args_var, width=60).grid(row=4, column=1, padx=5, columnspan=3)

        # Start in 目录
        tk.Label(root, text="Start in 目录:").grid(row=5, column=0, sticky="e")
        self.startin_var = tk.StringVar()
        tk.Entry(root, textvariable=self.startin_var, width=60).grid(row=5, column=1, padx=5)
        tk.Button(root, text="选择", command=self.select_startin).grid(row=5, column=2)

        # 生成命令和运行
        tk.Button(root, text="生成命令", command=self.generate_cmd).grid(row=6, column=1, pady=10)
        tk.Button(root, text="运行", command=self.run_cmd).grid(row=6, column=2, pady=10)

        # 命令显示
        tk.Label(root, text="命令行:").grid(row=7, column=0, sticky="ne")
        self.cmd_text = tk.Text(root, height=2, width=80)
        self.cmd_text.grid(row=7, column=1, columnspan=3, padx=5, pady=5)

        # 日志显示
        tk.Label(root, text="运行日志:").grid(row=8, column=0, sticky="ne")
        self.log_text = tk.Text(root, height=6, width=80)
        self.log_text.grid(row=8, column=1, columnspan=3, padx=5, pady=5)

        # ForceBindIP 下载地址
        self.download_url = "https://r1ch.net/projects/forcebindip"
        link_label = tk.Label(root, text="ForceBindIP 官方下载地址: " + self.download_url, fg="blue", cursor="hand2")
        link_label.grid(row=9, column=0, columnspan=4, sticky="w", padx=10, pady=5)
        link_label.bind("<Button-1>", lambda e: self.open_url())

        # 作者信息
        author_label = tk.Label(root, text="作者：RayCod", fg="gray")
        author_label.grid(row=10, column=0, columnspan=4, sticky="w", padx=10, pady=(0, 8))

    def select_fbind(self):
        path = filedialog.askopenfilename(title="选择 ForceBindIP.exe", filetypes=[("可执行文件", "*.exe")])
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
        path = filedialog.askopenfilename(title="选择目标程序", filetypes=[("可执行文件", "*.exe")])
        if path:
            self.target_var.set(path)
            self.startin_var.set(os.path.dirname(path))

    def select_startin(self):
        path = filedialog.askdirectory(title="选择Start in目录")
        if path:
            self.startin_var.set(path)

    def generate_cmd(self):
        fbind = self.fbind_path_var.get()
        ip = self.ip_var.get()
        target = self.target_var.get()
        args = self.args_var.get()
        use_i = self.use_i.get()
        if not (fbind and ip and target):
            messagebox.showerror("错误", "ForceBindIP路径、IP/GUID、目标程序不能为空")
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
            self.log_text.insert(tk.END, f"运行命令: {cmd}\n")
            self.log_text.see(tk.END)
            subprocess.Popen(cmd, cwd=startin, shell=True)
            self.log_text.insert(tk.END, "已启动目标程序。\n")
            self.log_text.see(tk.END)
        except Exception as e:
            self.log_text.insert(tk.END, f"启动失败: {e}\n")
            self.log_text.see(tk.END)

    def get_local_ips(self):
        ips = set()
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    ips.add(addr.address)
        return sorted(ips)

    def set_ip_from_combo(self, value):
        self.ip_var.set(value)

    def refresh_ip_list(self):
        menu = self.ip_optionmenu['menu']
        menu.delete(0, 'end')
        for ip in self.get_local_ips():
            menu.add_command(label=ip, command=lambda v=ip: self.set_ip_from_combo(v))

    def open_url(self):
        import webbrowser
        webbrowser.open(self.download_url)

if __name__ == "__main__":
    root = tk.Tk()
    app = ForceBindIPGUI(root)
    root.mainloop() 