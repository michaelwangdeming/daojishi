#pyinstaller --onefile --windowed --clean try.py
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import subprocess
import random
import math
import os
import json

config_file_path = "D:/config.json"

def calculate_divisor_sum(n):
    try:
        n = int(n)
        total = 0
        for i in range(1, int(math.isqrt(n)) + 1):
            if n % i == 0:
                if i == n // i:
                    total += i
                else:
                    total += i + n // i
        return total
    except:
        return -1
    
# 确保配置文件存在
if not os.path.exists(config_file_path):
    default_config = {
        "name": "倒计时",
        "countdowns": [
            {"name": "考试1", "date": "2025/3/1"},
            {"name": "考试2", "date": "2025/3/2"},
            {"name": "考试3", "date": "2025/3/3"}
        ],
        "encouragements": [
            "加油1",
            "加油2",
            "加油3"
        ],
        "start_countdown_index": 0,
        "password": "1000"
    }
    with open(config_file_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

def load_config():
    try:
        with open(config_file_path, "r", encoding="utf-8") as file:
            info = json.load(file)
        
        # 检查必要字段
        required_keys = ["name", "countdowns", "encouragements", "start_countdown_index", "password"]
        for key in required_keys:
            if key not in info:
                raise ValueError(f"缺少必要配置项: {key}")
                
        # 检查countdowns格式
        if not isinstance(info["countdowns"], list):
            raise ValueError("countdowns必须是列表")
        for exam in info["countdowns"]:
            if not isinstance(exam, dict) or "name" not in exam or "date" not in exam:
                raise ValueError("countdowns中的每个考试必须包含name和date字段")
            datetime.strptime(exam["date"], "%Y/%m/%d")  # 验证日期格式
            
        return info
    except Exception as e:
        messagebox.showerror("配置文件错误", f"配置文件格式错误: {str(e)}\n将使用默认配置")
        return {
            "name": "倒计时",
            "countdowns": [
                {"name": "考试1", "date": "2025/3/1"},
                {"name": "考试2", "date": "2025/3/2"},
                {"name": "考试3", "date": "2025/3/3"}
            ],
            "encouragements": [
                "加油1",
                "加油2",
                "加油3"
            ],
            "start_countdown_index": 0,
            "password": "1000"
        }

info = load_config()


class CountdownApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.flag = True
        self.last_valid_exam = ""
        self.current_config_content = ""

        self.attributes('-topmost', True)
        self.overrideredirect(True)

        screen_width = self.winfo_screenwidth()
        self.window_height = 60
        self.geometry(f'+{(screen_width - self.winfo_width()) // 2}+0')
        self.frame = tk.Frame(self)
        self.frame.pack()

        self.selected_exam = tk.StringVar(self)
        self.exam_options = [exam["name"] for exam in info["countdowns"]] + ["设置"]
        start_index = max(0, min(info.get("start_countdown_index", 0), len(info["countdowns"])-1))
        self.selected_exam.set(info["countdowns"][start_index]["name"])
        self.last_valid_exam = self.selected_exam.get()
        
        self.exam_menu = tk.OptionMenu(self.frame, self.selected_exam, *self.exam_options, command=self.on_exam_change)
        self.exam_menu.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.label = tk.Label(self.frame, text='', font=('Helvetica', 36), bg='white', fg='black')
        self.label.pack(side=tk.LEFT, padx=1, pady=1)
        self.label.bind("<Button-1>", self.play_random_encouragement)

        self.update_label()
        self.last_speak_time = datetime.now() - timedelta(seconds=5)

    def update_label(self):
        label_text = self.get_label_text()
        self.label.config(text=label_text)
        self.adjust_window_size(label_text)
        self.after(1000, self.update_label)

    def get_label_text(self):
        current_date = datetime.now()
        selected = self.selected_exam.get()
        if selected == "设置":
            return ""
        
        target_exam = next((exam for exam in info["countdowns"] if exam["name"] == selected), None)
        if not target_exam:
            return "无效的考试"
        
        target_date = datetime.strptime(target_exam["date"], "%Y/%m/%d")
        delta = target_date - current_date
        days = max(delta.days, 0)
        return f'距离{selected}还有 {days} 天'

    def speak(self, text):
        command = f'powershell.exe "Add-Type -AssemblyName System.Speech;' \
                  f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"'
        subprocess.Popen(command, shell=True)

    def play_random_encouragement(self, event):
        current_time = datetime.now()
        time_diff = (current_time - self.last_speak_time).total_seconds()
        if time_diff >= 5 and self.selected_exam.get() != "设置":
            encouragement = random.choice(info["encouragements"])
            self.speak(encouragement)
            self.last_speak_time = current_time

    def on_exam_change(self, *args):
        selected = self.selected_exam.get()
        if selected == "设置":
            self.selected_exam.set(self.last_valid_exam)
            self.open_password_check()
        else:
            self.last_valid_exam = selected
            label_text = self.get_label_text()
            self.label.config(text=label_text)
            self.adjust_window_size(label_text)
            self.speak(label_text)

    def adjust_window_size(self, label_text):
        label_width = self.label.winfo_reqwidth()
        menu_width = self.exam_menu.winfo_reqwidth()
        total_width = label_width + menu_width + 40
        self.geometry(f'{total_width}x{self.window_height}+{(self.winfo_screenwidth() - total_width) // 2}+0')

    def open_password_check(self):
        self.pw_window = tk.Toplevel(self)
        self.pw_window.title("密码验证")
        self.pw_window.geometry("400x150")
        
        tk.Label(self.pw_window, text=f"请输入密码").pack(pady=10)
        self.answer_entry = tk.Entry(self.pw_window)
        self.answer_entry.pack(pady=5)
        
        btn_frame = tk.Frame(self.pw_window)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="提交", command=self.check_password).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="取消", command=self.pw_window.destroy).pack(side=tk.LEFT, padx=10)

    def check_password(self):
        user_input = self.answer_entry.get()
        correct_sum = calculate_divisor_sum(info["password"])
        
        try:
            if int(user_input) == correct_sum:
                self.pw_window.destroy()
                self.open_settings()
            else:
                messagebox.showerror("错误", "不正确")
        except:
            messagebox.showerror("错误", "请输入有效数字")
        finally:
            self.answer_entry.delete(0, tk.END)

    def open_settings(self):
        self.settings_window = tk.Toplevel(self)
        self.settings_window.title("设置")
        self.settings_window.geometry("800x600")
        
        with open(config_file_path, "r", encoding="utf-8") as f:
            self.current_config_content = f.read()
        
        self.text_area = tk.Text(self.settings_window)
        self.text_area.insert(tk.END, self.current_config_content)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        btn_frame = tk.Frame(self.settings_window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="取消", command=self.settings_window.destroy).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="更改", command=self.save_settings).pack(side=tk.LEFT, padx=10)

    def save_settings(self):
        new_content = self.text_area.get("1.0", tk.END).strip()
        try:
            temp_info = json.loads(new_content)
            required_keys = ["name", "countdowns", "encouragements", "start_countdown_index", "password"]
            if not all(key in temp_info for key in required_keys):
                raise ValueError("缺少必要配置项")

            for exam in temp_info["countdowns"]:
                datetime.strptime(exam["date"], "%Y/%m/%d")

            # 保存新的配置文件
            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(temp_info, f, ensure_ascii=False, indent=4)

            # 更新全局变量
            global info
            info = temp_info

            # 更新界面
            self.update_config()

            self.settings_window.destroy()
            messagebox.showinfo("成功", "配置已更新")

        except Exception as e:
            messagebox.showerror("配置错误", f"无效的配置内容：{str(e)}")

    def update_config(self):
        self.exam_options = [exam["name"] for exam in info["countdowns"]] + ["设置"]
        menu = self.exam_menu["menu"]
        menu.delete(0, "end")
        for option in self.exam_options:
            menu.add_command(label=option, command=tk._setit(self.selected_exam, option))

        start_index = max(0, min(info["start_countdown_index"], len(info["countdowns"])-1))
        self.selected_exam.set(info["countdowns"][start_index]["name"])
        self.last_valid_exam = self.selected_exam.get()
        self.label.config(text=self.get_label_text())
        self.adjust_window_size(self.get_label_text())

if __name__ == '__main__':
    app = CountdownApp()
    app.mainloop()