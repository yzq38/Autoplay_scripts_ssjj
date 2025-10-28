import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import threading
import time
import re


class SimpleScriptManager:
    def __init__(self, root):
        self.root = root
        self.root.title("脚本管理器")
        self.root.geometry("400x500")  # 增加窗口大小

        # 使用英文文件夹名
        self.script_folder = "test"

        # 如果scripts文件夹不存在，尝试使用测试文件夹
        if not os.path.exists(self.script_folder) and os.path.exists("测试"):
            self.script_folder = "测试"

        # 存储当前运行的脚本信息
        self.current_script = None
        self.current_chapter = None
        self.current_number = None

        self.setup_ui()
        self.load_scripts()

    def setup_ui(self):
        # 主标题
        title_label = tk.Label(self.root, text="Script Manager", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 创建一个框架用于容纳Canvas和Scrollbar
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        # 创建Canvas和Scrollbar
        self.canvas = tk.Canvas(container, bg="white")
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        # 创建可滚动的框架
        self.scrollable_frame = tk.Frame(self.canvas)

        # 绑定框架尺寸变化事件
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # 将可滚动框架添加到Canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 布局Canvas和Scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)

        # 状态显示
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 10))
        status_label.pack(pady=5)

        # 添加停止按钮
        self.stop_button = tk.Button(self.root, text="Stop Auto-Run", command=self.stop_auto_run,
                                     width=15, height=1, font=("Arial", 10), state="disabled")
        self.stop_button.pack(pady=5)

    def _on_mousewheel(self, event):
        """处理鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def load_scripts(self):
        try:
            if not os.path.exists(self.script_folder):
                messagebox.showerror("Error", f"Folder '{self.script_folder}' not found!")
                return

            scripts = [f for f in os.listdir(self.script_folder) if f.endswith('.py')]

            if not scripts:
                messagebox.showwarning("Warning", "No Python scripts found in the folder!")
                return

            # 创建按钮
            for i, script in enumerate(scripts):
                btn = tk.Button(self.scrollable_frame,
                                text=script[:-3],
                                command=lambda s=script: self.run_script(s),
                                width=25,
                                height=2,
                                font=("Arial", 10))
                btn.grid(row=i, column=0, pady=5, padx=10, sticky="ew")

            # 配置列权重使按钮扩展
            self.scrollable_frame.columnconfigure(0, weight=1)

        except Exception as e:
            messagebox.showerror("Error", f"Load error: {str(e)}")

    def parse_script_name(self, script_file):
        """解析脚本文件名，提取章节名和编号"""
        # 移除.py扩展名
        name = script_file[:-3]

        # 使用正则表达式匹配章节名和编号
        # 假设格式为：章节名+数字，例如：海岛2、森林3等
        match = re.match(r'([^\d]+)(\d+)', name)
        if match:
            chapter = match.group(1)  # 章节名
            number = int(match.group(2))  # 编号
            return chapter, number
        return None, None

    def find_next_script(self, chapter, current_number):
        """查找同一章节中编号更大的下一个脚本"""
        try:
            scripts = [f for f in os.listdir(self.script_folder) if f.endswith('.py')]
            next_script = None
            next_number = float('inf')  # 初始化为无穷大

            for script in scripts:
                script_chapter, script_number = self.parse_script_name(script)
                if (script_chapter == chapter and
                        script_number > current_number and
                        script_number < next_number):
                    next_script = script
                    next_number = script_number

            return next_script
        except Exception as e:
            print(f"Error finding next script: {str(e)}")
            return None

    def run_script(self, script_file):
        result = messagebox.askyesno("Confirm", f"Run {script_file}?\nWill start in 10 seconds")
        if not result:
            return

        # 解析当前脚本信息
        chapter, number = self.parse_script_name(script_file)
        if chapter and number is not None:
            self.current_script = script_file
            self.current_chapter = chapter
            self.current_number = number
            self.stop_button.config(state="normal")

        thread = threading.Thread(target=self.execute_with_countdown, args=(script_file,))
        thread.daemon = True
        thread.start()

    def execute_with_countdown(self, script_file):
        try:
            # 倒计时
            for i in range(10, 0, -1):
                self.root.after(0, lambda x=i: self.status_var.set(f"Starting in {x}s..."))
                time.sleep(1)

            self.root.after(0, lambda: self.status_var.set("Running..."))

            # 使用相对路径运行，指定UTF-8编码
            result = subprocess.run(["python", script_file],
                                    cwd=self.script_folder,
                                    capture_output=True,
                                    text=True,
                                    encoding='utf-8')

            if result.returncode == 0:
                self.root.after(0, lambda: self.status_var.set("Completed"))

                # 查找并运行下一关
                if self.current_chapter and self.current_number is not None:
                    next_script = self.find_next_script(self.current_chapter, self.current_number)
                    if next_script:
                        self.root.after(0, lambda: self.status_var.set(f"Auto-running {next_script} in 10s..."))
                        time.sleep(10)  # 等待10秒后运行下一关

                        # 更新当前脚本信息
                        self.current_script = next_script
                        chapter, number = self.parse_script_name(next_script)
                        if chapter and number is not None:
                            self.current_chapter = chapter
                            self.current_number = number

                        # 运行下一关
                        self.execute_script_directly(next_script)
                    else:
                        self.root.after(0, lambda: self.status_var.set("No next script found"))
                        self.stop_auto_run()
            else:
                self.root.after(0, lambda: self.status_var.set("Error"))
                print(f"Error: {result.stderr}")
                self.stop_auto_run()

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.stop_auto_run()

    def execute_script_directly(self, script_file):
        """直接运行脚本（不显示确认对话框）"""
        try:
            self.root.after(0, lambda: self.status_var.set(f"Running {script_file}..."))

            result = subprocess.run(["python", script_file],
                                    cwd=self.script_folder,
                                    capture_output=True,
                                    text=True,
                                    encoding='utf-8')

            if result.returncode == 0:
                self.root.after(0, lambda: self.status_var.set("Completed"))

                # 继续查找并运行下一关
                if self.current_chapter and self.current_number is not None:
                    next_script = self.find_next_script(self.current_chapter, self.current_number)
                    if next_script:
                        self.root.after(0, lambda: self.status_var.set(f"Auto-running {next_script} in 10s..."))
                        time.sleep(10)  # 等待10秒后运行下一关

                        # 更新当前脚本信息
                        self.current_script = next_script
                        chapter, number = self.parse_script_name(next_script)
                        if chapter and number is not None:
                            self.current_chapter = chapter
                            self.current_number = number

                        # 运行下一关
                        self.execute_script_directly(next_script)
                    else:
                        self.root.after(0, lambda: self.status_var.set("No next script found"))
                        self.stop_auto_run()
            else:
                self.root.after(0, lambda: self.status_var.set("Error"))
                print(f"Error: {result.stderr}")
                self.stop_auto_run()

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.stop_auto_run()

    def stop_auto_run(self):
        """停止自动运行"""
        self.current_script = None
        self.current_chapter = None
        self.current_number = None
        self.stop_button.config(state="disabled")
        self.root.after(0, lambda: self.status_var.set("Auto-run stopped"))


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleScriptManager(root)
    root.mainloop()