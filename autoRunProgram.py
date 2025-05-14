import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import subprocess
import threading
import time
import os


class ProgramTask:
    def __init__(self, file_path, execution_mode, time_settings):
        self.file_path = file_path
        self.execution_mode = execution_mode
        self.time_settings = time_settings
        self.is_counting = False
        self.countdown_thread = None


class ShutdownTask:
    def __init__(self, execution_mode, time_settings):
        self.execution_mode = execution_mode
        self.time_settings = time_settings
        self.is_counting = False
        self.countdown_thread = None


class AutoRunProgramGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("多程序定时执行工具")
        self.root.geometry("800x600")

        # 存储任务列表
        self.tasks = []
        # 存储执行模式
        self.execution_mode = tk.StringVar(value="countdown")
        # 存储关机任务
        self.shutdown_task = None

        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 左侧任务列表框架
        list_frame = ttk.LabelFrame(main_frame, text="任务列表", padding="10")
        list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # 任务列表
        self.task_listbox = tk.Listbox(list_frame, width=40, height=10)
        self.task_listbox.pack(side="left", fill="both", expand=True)

        # 任务列表滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.task_listbox.configure(yscrollcommand=scrollbar.set)

        # 右侧设置框架
        settings_frame = ttk.LabelFrame(main_frame, text="任务设置", padding="10")
        settings_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # 文件选择框架
        file_frame = ttk.Frame(settings_frame)
        file_frame.pack(fill="x", pady=5)

        # 文件路径显示
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=40)
        self.file_entry.pack(side="left", padx=5)

        # 浏览按钮
        browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        browse_btn.pack(side="left", padx=5)

        # 执行模式选择框架
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.pack(fill="x", pady=5)

        # 执行模式单选按钮
        ttk.Radiobutton(mode_frame, text="倒计时执行", variable=self.execution_mode,
                        value="countdown", command=self.update_time_widgets).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="指定时间执行", variable=self.execution_mode,
                        value="scheduled", command=self.update_time_widgets).pack(side="left", padx=5)

        # 时间设置框架
        self.time_frame = ttk.Frame(settings_frame)
        self.time_frame.pack(fill="x", pady=5)

        # 倒计时时间设置
        self.countdown_frame = ttk.Frame(self.time_frame)
        self.countdown_frame.pack(fill="x")

        ttk.Label(self.countdown_frame, text="倒计时时间:").pack(side="left", padx=5)
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        self.second_var = tk.StringVar(value="00")

        # 小时选择
        hour_spin = ttk.Spinbox(self.countdown_frame, from_=0, to=23, width=5, textvariable=self.hour_var)
        hour_spin.pack(side="left", padx=2)
        ttk.Label(self.countdown_frame, text="时").pack(side="left")

        # 分钟选择
        minute_spin = ttk.Spinbox(self.countdown_frame, from_=0, to=59, width=5, textvariable=self.minute_var)
        minute_spin.pack(side="left", padx=2)
        ttk.Label(self.countdown_frame, text="分").pack(side="left")

        # 秒钟选择
        second_spin = ttk.Spinbox(self.countdown_frame, from_=0, to=59, width=5, textvariable=self.second_var)
        second_spin.pack(side="left", padx=2)
        ttk.Label(self.countdown_frame, text="秒").pack(side="left")

        # 指定时间设置
        self.scheduled_frame = ttk.Frame(self.time_frame)

        ttk.Label(self.scheduled_frame, text="执行时间:").pack(side="left", padx=5)
        self.date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.time_var = tk.StringVar(value=datetime.datetime.now().strftime("%H:%M:%S"))

        # 日期选择
        date_entry = ttk.Entry(self.scheduled_frame, textvariable=self.date_var, width=10)
        date_entry.pack(side="left", padx=2)
        ttk.Label(self.scheduled_frame, text="时间:").pack(side="left")

        # 时间选择
        time_entry = ttk.Entry(self.scheduled_frame, textvariable=self.time_var, width=8)
        time_entry.pack(side="left", padx=2)

        # 控制按钮框架
        control_frame = ttk.Frame(settings_frame)
        control_frame.pack(fill="x", pady=5)

        # 添加任务按钮
        add_btn = ttk.Button(control_frame, text="添加任务", command=self.add_task)
        add_btn.pack(side="left", padx=5)

        # 删除任务按钮
        delete_btn = ttk.Button(control_frame, text="删除任务", command=self.delete_task)
        delete_btn.pack(side="left", padx=5)

        # 开始所有任务按钮
        start_all_btn = ttk.Button(control_frame, text="开始所有任务", command=self.start_all_tasks)
        start_all_btn.pack(side="left", padx=5)

        # 停止所有任务按钮
        stop_all_btn = ttk.Button(control_frame, text="停止所有任务", command=self.stop_all_tasks)
        stop_all_btn.pack(side="left", padx=5)

        # 关机设置框架
        shutdown_frame = ttk.LabelFrame(self.root, text="关机设置", padding="10")
        shutdown_frame.pack(fill="x", padx=10, pady=5)

        # 关机模式选择
        shutdown_mode_frame = ttk.Frame(shutdown_frame)
        shutdown_mode_frame.pack(fill="x", pady=5)

        self.shutdown_mode = tk.StringVar(value="countdown")
        ttk.Radiobutton(shutdown_mode_frame, text="倒计时关机", variable=self.shutdown_mode,
                        value="countdown", command=self.update_shutdown_widgets).pack(side="left", padx=5)
        ttk.Radiobutton(shutdown_mode_frame, text="定时关机", variable=self.shutdown_mode,
                        value="scheduled", command=self.update_shutdown_widgets).pack(side="left", padx=5)

        # 关机时间设置框架
        self.shutdown_time_frame = ttk.Frame(shutdown_frame)
        self.shutdown_time_frame.pack(fill="x", pady=5)

        # 倒计时关机设置
        self.shutdown_countdown_frame = ttk.Frame(self.shutdown_time_frame)
        self.shutdown_countdown_frame.pack(fill="x")

        ttk.Label(self.shutdown_countdown_frame, text="倒计时时间:").pack(side="left", padx=5)
        self.shutdown_hour_var = tk.StringVar(value="00")
        self.shutdown_minute_var = tk.StringVar(value="00")
        self.shutdown_second_var = tk.StringVar(value="00")

        # 小时选择
        hour_spin = ttk.Spinbox(self.shutdown_countdown_frame, from_=0, to=23, width=5,
                                textvariable=self.shutdown_hour_var)
        hour_spin.pack(side="left", padx=2)
        ttk.Label(self.shutdown_countdown_frame, text="时").pack(side="left")

        # 分钟选择
        minute_spin = ttk.Spinbox(self.shutdown_countdown_frame, from_=0, to=59, width=5,
                                  textvariable=self.shutdown_minute_var)
        minute_spin.pack(side="left", padx=2)
        ttk.Label(self.shutdown_countdown_frame, text="分").pack(side="left")

        # 秒钟选择
        second_spin = ttk.Spinbox(self.shutdown_countdown_frame, from_=0, to=59, width=5,
                                  textvariable=self.shutdown_second_var)
        second_spin.pack(side="left", padx=2)
        ttk.Label(self.shutdown_countdown_frame, text="秒").pack(side="left")

        # 定时关机设置
        self.shutdown_scheduled_frame = ttk.Frame(self.shutdown_time_frame)

        ttk.Label(self.shutdown_scheduled_frame, text="关机时间:").pack(side="left", padx=5)
        self.shutdown_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.shutdown_time_var = tk.StringVar(value=datetime.datetime.now().strftime("%H:%M:%S"))

        # 日期选择
        date_entry = ttk.Entry(self.shutdown_scheduled_frame, textvariable=self.shutdown_date_var, width=10)
        date_entry.pack(side="left", padx=2)
        ttk.Label(self.shutdown_scheduled_frame, text="时间:").pack(side="left")

        # 时间选择
        time_entry = ttk.Entry(self.shutdown_scheduled_frame, textvariable=self.shutdown_time_var, width=8)
        time_entry.pack(side="left", padx=2)

        # 关机控制按钮
        shutdown_control_frame = ttk.Frame(shutdown_frame)
        shutdown_control_frame.pack(fill="x", pady=5)

        # 设置关机按钮
        set_shutdown_btn = ttk.Button(shutdown_control_frame, text="设置关机", command=self.set_shutdown)
        set_shutdown_btn.pack(side="left", padx=5)

        # 取消关机按钮
        cancel_shutdown_btn = ttk.Button(shutdown_control_frame, text="取消关机", command=self.cancel_shutdown)
        cancel_shutdown_btn.pack(side="left", padx=5)

        # 状态显示框架
        status_frame = ttk.LabelFrame(self.root, text="状态", padding="10")
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 日志显示
        self.log_text = tk.Text(status_frame, height=15, width=80)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # 初始化显示
        self.update_time_widgets()
        self.update_shutdown_widgets()

    def update_time_widgets(self):
        if self.execution_mode.get() == "countdown":
            self.scheduled_frame.pack_forget()
            self.countdown_frame.pack(fill="x")
        else:
            self.countdown_frame.pack_forget()
            self.scheduled_frame.pack(fill="x")
            # 设置默认时间为当前时间后1分钟
            default_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
            self.date_var.set(default_time.strftime("%Y-%m-%d"))
            self.time_var.set(default_time.strftime("%H:%M:%S"))

    def update_shutdown_widgets(self):
        if self.shutdown_mode.get() == "countdown":
            self.shutdown_scheduled_frame.pack_forget()
            self.shutdown_countdown_frame.pack(fill="x")
        else:
            self.shutdown_countdown_frame.pack_forget()
            self.shutdown_scheduled_frame.pack(fill="x")
            # 设置默认时间为当前时间后1分钟
            default_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
            self.shutdown_date_var.set(default_time.strftime("%Y-%m-%d"))
            self.shutdown_time_var.set(default_time.strftime("%H:%M:%S"))

    def browse_file(self):
        filetypes = [
            ("可执行文件", "*.exe"),
            ("批处理文件", "*.bat"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.file_path.set(filename)
            self.log(f"已选择文件: {filename}")

    def log(self, message):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{current_time}] {message}\n")
        self.log_text.see("end")

    def add_task(self):
        if not self.file_path.get():
            messagebox.showerror("错误", "请先选择要执行的程序！")
            return

        try:
            if self.execution_mode.get() == "countdown":
                # 获取倒计时时间
                hours = int(self.hour_var.get())
                minutes = int(self.minute_var.get())
                seconds = int(self.second_var.get())

                if hours == 0 and minutes == 0 and seconds == 0:
                    messagebox.showerror("错误", "请设置倒计时时间！")
                    return

                time_settings = {
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds
                }

            else:
                # 获取指定时间
                try:
                    scheduled_time = datetime.datetime.strptime(
                        f"{self.date_var.get()} {self.time_var.get()}",
                        "%Y-%m-%d %H:%M:%S"
                    )

                    if scheduled_time < datetime.datetime.now():
                        messagebox.showerror("错误", "指定的时间已经过去！")
                        return

                    time_settings = {
                        "scheduled_time": scheduled_time
                    }

                except ValueError:
                    messagebox.showerror("错误", "请输入正确的时间格式！(YYYY-MM-DD HH:MM:SS)")
                    return

            # 创建新任务
            task = ProgramTask(
                self.file_path.get(),
                self.execution_mode.get(),
                time_settings
            )

            # 添加到任务列表
            self.tasks.append(task)
            self.task_listbox.insert(tk.END, f"{os.path.basename(task.file_path)} - {self.get_time_display(task)}")

            self.log(f"已添加任务: {os.path.basename(task.file_path)}")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的时间！")

    def get_time_display(self, task):
        if task.execution_mode == "countdown":
            return f"倒计时: {task.time_settings['hours']:02d}:{task.time_settings['minutes']:02d}:{task.time_settings['seconds']:02d}"
        else:
            return f"执行时间: {task.time_settings['scheduled_time'].strftime('%Y-%m-%d %H:%M:%S')}"

    def delete_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请先选择要删除的任务！")
            return

        index = selection[0]
        task = self.tasks[index]

        # 如果任务正在运行，先停止
        if task.is_counting:
            task.is_counting = False

        # 从列表中删除
        self.tasks.pop(index)
        self.task_listbox.delete(index)

        self.log(f"已删除任务: {os.path.basename(task.file_path)}")

    def start_all_tasks(self):
        for task in self.tasks:
            if not task.is_counting:
                self.start_task(task)

    def stop_all_tasks(self):
        for task in self.tasks:
            if task.is_counting:
                task.is_counting = False
                self.log(f"已停止任务: {os.path.basename(task.file_path)}")

    def start_task(self, task):
        if task.is_counting:
            return

        try:
            if task.execution_mode == "countdown":
                # 计算总秒数
                total_seconds = (task.time_settings['hours'] * 3600 +
                                 task.time_settings['minutes'] * 60 +
                                 task.time_settings['seconds'])

            else:
                # 计算等待时间
                wait_seconds = (task.time_settings['scheduled_time'] -
                                datetime.datetime.now()).total_seconds()
                total_seconds = int(wait_seconds)

            task.is_counting = True

            # 开始倒计时
            task.countdown_thread = threading.Thread(
                target=self.countdown,
                args=(task, total_seconds)
            )
            task.countdown_thread.daemon = True
            task.countdown_thread.start()

            self.log(f"开始任务: {os.path.basename(task.file_path)}")

        except Exception as e:
            self.log(f"启动任务时出错: {str(e)}")
            task.is_counting = False

    def countdown(self, task, total_seconds):
        while total_seconds > 0 and task.is_counting:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            self.log(f"{os.path.basename(task.file_path)} 剩余时间: {hours:02d}:{minutes:02d}:{seconds:02d}")

            time.sleep(1)
            total_seconds -= 1

        if task.is_counting:
            self.execute_program(task)

    def execute_program(self, task):
        try:
            self.log(f"开始执行程序: {task.file_path}")
            # 执行程序
            subprocess.Popen(task.file_path, shell=True)
            self.log(f"程序已启动: {os.path.basename(task.file_path)}")

        except Exception as e:
            self.log(f"执行程序时出错: {str(e)}")
            messagebox.showerror("错误", f"执行程序时出错: {str(e)}")

        finally:
            task.is_counting = False

    def set_shutdown(self):
        try:
            if self.shutdown_mode.get() == "countdown":
                # 获取倒计时时间
                hours = int(self.shutdown_hour_var.get())
                minutes = int(self.shutdown_minute_var.get())
                seconds = int(self.shutdown_second_var.get())

                if hours == 0 and minutes == 0 and seconds == 0:
                    messagebox.showerror("错误", "请设置倒计时时间！")
                    return

                time_settings = {
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds
                }

            else:
                # 获取指定时间
                try:
                    scheduled_time = datetime.datetime.strptime(
                        f"{self.shutdown_date_var.get()} {self.shutdown_time_var.get()}",
                        "%Y-%m-%d %H:%M:%S"
                    )

                    if scheduled_time < datetime.datetime.now():
                        messagebox.showerror("错误", "指定的时间已经过去！")
                        return

                    time_settings = {
                        "scheduled_time": scheduled_time
                    }

                except ValueError:
                    messagebox.showerror("错误", "请输入正确的时间格式！(YYYY-MM-DD HH:MM:SS)")
                    return

            # 创建关机任务
            self.shutdown_task = ShutdownTask(
                self.shutdown_mode.get(),
                time_settings
            )

            # 开始关机倒计时
            self.start_shutdown()

        except ValueError:
            messagebox.showerror("错误", "请输入有效的时间！")

    def cancel_shutdown(self):
        if self.shutdown_task and self.shutdown_task.is_counting:
            self.shutdown_task.is_counting = False
            self.log("已取消关机")
            # 取消系统关机
            os.system("shutdown /a")

    def start_shutdown(self):
        if not self.shutdown_task:
            return

        try:
            if self.shutdown_task.execution_mode == "countdown":
                # 计算总秒数
                total_seconds = (self.shutdown_task.time_settings['hours'] * 3600 +
                                 self.shutdown_task.time_settings['minutes'] * 60 +
                                 self.shutdown_task.time_settings['seconds'])

            else:
                # 计算等待时间
                wait_seconds = (self.shutdown_task.time_settings['scheduled_time'] -
                                datetime.datetime.now()).total_seconds()
                total_seconds = int(wait_seconds)

            self.shutdown_task.is_counting = True

            # 开始倒计时
            self.shutdown_task.countdown_thread = threading.Thread(
                target=self.shutdown_countdown,
                args=(total_seconds,)
            )
            self.shutdown_task.countdown_thread.daemon = True
            self.shutdown_task.countdown_thread.start()

            self.log("开始关机倒计时")

        except Exception as e:
            self.log(f"设置关机时出错: {str(e)}")
            self.shutdown_task.is_counting = False

    def shutdown_countdown(self, total_seconds):
        while total_seconds > 0 and self.shutdown_task.is_counting:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            self.log(f"关机倒计时: {hours:02d}:{minutes:02d}:{seconds:02d}")

            time.sleep(1)
            total_seconds -= 1

        if self.shutdown_task.is_counting:
            self.execute_shutdown()

    def execute_shutdown(self):
        try:
            self.log("准备关机...")
            # 执行关机命令
            os.system("shutdown /s /f /t 0")

        except Exception as e:
            self.log(f"关机时出错: {str(e)}")
            messagebox.showerror("错误", f"关机时出错: {str(e)}")

        finally:
            self.shutdown_task.is_counting = False


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoRunProgramGUI(root)
    root.mainloop()
