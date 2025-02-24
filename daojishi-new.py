import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import subprocess
import random
import math
import os, sys
import json
import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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
            datetime.strptime(exam["date"], "%Y/%m/%d")
            
        return info
    except Exception as e:
        print(f"配置文件格式错误: {str(e)}\n将使用默认配置")
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
settings_open = False

class CountdownApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.flag = True
        self.last_valid_exam = ""
        self.current_config_content = ""

        self.attributes('-topmost', True)
        self.overrideredirect(True)

        screen_width = self.winfo_screenwidth()
        self.window_height = int(60 * 1.2)
        self.geometry(f'+{(screen_width - self.winfo_width()) // 2}+0')

        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.selected_exam = tk.StringVar(self)
        self.exam_options = [exam["name"] for exam in info["countdowns"]] + ["设置"]
        start_index = max(0, min(info.get("start_countdown_index", 0), len(info["countdowns"]) - 1))
        self.selected_exam.set(info["countdowns"][start_index]["name"])
        self.last_valid_exam = self.selected_exam.get()

        # 固定 CTkOptionMenu 的大小
        self.exam_menu = ctk.CTkOptionMenu(self.main_frame, variable=self.selected_exam, values=self.exam_options, command=self.on_exam_change, width=120)  # 固定宽度为120
        self.exam_menu.pack(side=tk.LEFT, padx=10, pady=10)

        self.label = ctk.CTkLabel(self.main_frame, text='', font=('Helvetica', int(36 * 1.2)), bg_color='transparent')  # 字体大小为原始大小的1.2倍
        self.label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.label.bind("<Button-1>", self.play_random_encouragement)

        self.update_label()
        self.last_speak_time = datetime.now() - timedelta(seconds=2)

    def update_label(self):
        label_text = self.get_label_text()
        self.label.configure(text=label_text)
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
        if time_diff >= 2 and self.selected_exam.get() != "设置":
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
            self.label.configure(text=label_text)
            self.adjust_window_size(label_text)
            self.speak(label_text)

    def adjust_window_size(self, label_text):
        label_width = self.label.winfo_reqwidth()
        menu_width = self.exam_menu.winfo_reqwidth()
        total_width = label_width + menu_width + 40
        self.geometry(f'{total_width}x{self.window_height}+{(self.winfo_screenwidth() - total_width) // 2}+0')

    def open_password_check(self):
        global settings_open
        if not settings_open:
            settings_open = True
            PasswordChecker(self)
        else:
            self.show_message("提示", "设置窗口已经打开，请先关闭它！")

    def show_message(self, title, message):
        msg_box = ctk.CTkToplevel(self)
        msg_box.overrideredirect(True)
        msg_box.attributes('-topmost', True)
        msg_box.geometry(f"300x130+{(self.winfo_screenwidth() - 300) // 2}+{self.winfo_y() + self.winfo_height() + 10}")
        
        ctk.CTkLabel(msg_box, text=message).pack(pady=20)
        ctk.CTkButton(msg_box, text="确定", command=msg_box.destroy).pack(pady=10)
        msg_box.grab_set()
    
class PasswordChecker(ctk.CTkToplevel):
    def __init__(self, parent):
        global settings_open
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry(f"400x150+{(self.parent.winfo_screenwidth() - 400) // 2}+{self.parent.winfo_y() + self.parent.winfo_height() + 10}")
        
        ctk.CTkLabel(self, text="请输入密码").pack(pady=10)
        self.answer_entry = ctk.CTkEntry(self)
        self.answer_entry.pack(pady=5)
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="提交", command=self.check_password).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)

    def check_password(self):
        user_input = self.answer_entry.get()
        correct_sum = calculate_divisor_sum(info["password"])
        
        try:
            if int(user_input) == correct_sum:
                self.destroy()
                global settings_open
                settings_open = False
                SettingsWindow(self.parent)
            else:
                self.parent.show_message("错误", "密码不正确")
        except:
            self.parent.show_message("错误", "请输入有效数字")
        finally:
            if self.winfo_exists():
                self.answer_entry.delete(0, tk.END)

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        global settings_open
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.geometry(f"800x600+{(self.parent.winfo_screenwidth() - 800) // 2}+{self.parent.winfo_y() + self.parent.winfo_height() + 10}")
        
        self.exam_frame = ctk.CTkScrollableFrame(self)
        self.exam_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.exam_list = []
        for exam in info["countdowns"]:
            exam_frame = ctk.CTkFrame(self.exam_frame)
            exam_frame.pack(fill=tk.X, pady=5)
            
            ctk.CTkLabel(exam_frame, text="考试名称:").grid(row=0, column=0, padx=5)
            name_entry = ctk.CTkEntry(exam_frame)
            name_entry.insert(0, exam["name"])
            name_entry.configure(state="readonly")
            name_entry.grid(row=0, column=1, padx=5)
            
            ctk.CTkLabel(exam_frame, text="日期:").grid(row=0, column=2, padx=5)
            date_entry = ctk.CTkEntry(exam_frame)
            date_entry.insert(0, exam["date"])
            date_entry.configure(state="readonly")
            date_entry.grid(row=0, column=3, padx=5)
            
            delete_button = ctk.CTkButton(exam_frame, text="删除", command=lambda e=exam_frame, n=exam["name"]: self.delete_exam(e, n))
            delete_button.grid(row=0, column=4, padx=5)
            
            self.exam_list.append((exam_frame, name_entry, date_entry))
        
        add_exam_frame = ctk.CTkFrame(self.exam_frame)
        add_exam_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(add_exam_frame, text="添加考试名称:").grid(row=0, column=0, padx=5)
        self.new_exam_name = ctk.CTkEntry(add_exam_frame)
        self.new_exam_name.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(add_exam_frame, text="添加日期:").grid(row=0, column=2, padx=5)
        self.new_exam_date = ctk.CTkEntry(add_exam_frame)
        self.new_exam_date.grid(row=0, column=3, padx=5)
        
        ctk.CTkButton(add_exam_frame, text="添加", command=self.add_exam).grid(row=0, column=4, padx=5)
        
        self.encouragement_frame = ctk.CTkScrollableFrame(self)
        self.encouragement_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.encouragement_list = []
        for encouragement in info["encouragements"]:
            encouragement_frame = ctk.CTkFrame(self.encouragement_frame)
            encouragement_frame.pack(fill=tk.X, pady=5)
            
            encouragement_entry = ctk.CTkEntry(encouragement_frame)
            encouragement_entry.insert(0, encouragement)
            encouragement_entry.configure(state="readonly")
            encouragement_entry.pack(side=tk.LEFT, padx=5)
            
            delete_button = ctk.CTkButton(encouragement_frame, text="删除", command=lambda e=encouragement_frame, c=encouragement: self.delete_encouragement(e, c))
            delete_button.pack(side=tk.LEFT, padx=5)
            
            self.encouragement_list.append((encouragement_frame, encouragement_entry))
        
        add_encouragement_frame = ctk.CTkFrame(self.encouragement_frame)
        add_encouragement_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(add_encouragement_frame, text="添加加油语:").grid(row=0, column=0, padx=5)
        self.new_encouragement = ctk.CTkEntry(add_encouragement_frame)
        self.new_encouragement.grid(row=0, column=1, padx=5)
        
        ctk.CTkButton(add_encouragement_frame, text="添加", command=self.add_encouragement).grid(row=0, column=2, padx=5)

        ctk.CTkButton(self, text="保存", command=self.save_settings).pack(padx=10, pady=10, side=tk.LEFT)
        ctk.CTkButton(self, text="取消", command=self.destroy).pack(padx=10, pady=10, side=tk.LEFT)

    def save_settings(self):
        try:
            with open(config_file_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
            self.parent.show_message("成功", "设置已保存！")
            self.destroy()
            self.parent.update_label()
            #restart_app(self)
        except Exception as e:
            self.parent.show_message("错误", f"保存失败：{str(e)}")
    def add_exam(self):
        name = self.new_exam_name.get().strip()
        date = self.new_exam_date.get().strip()
        if not name or not date:
            self.parent.show_message("警告", "考试名称和日期不能为空！")
            return
        try:
            datetime.strptime(date, "%Y/%m/%d")
        except ValueError:
            self.parent.show_message("警告", "日期格式不正确，请使用 YYYY/MM/DD 格式！")
            return
    
        # 添加到配置
        info["countdowns"].append({"name": name, "date": date})
        self.parent.exam_options.append(name)
        self.parent.exam_menu.configure(values=self.parent.exam_options)
        self.parent.exam_menu.set(name)
        self.parent.update_label()
    
        # 更新设置窗口
        exam_frame = ctk.CTkFrame(self.exam_frame)
        exam_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(exam_frame, text="考试名称:").grid(row=0, column=0, padx=5)
        name_entry = ctk.CTkEntry(exam_frame)
        name_entry.insert(0, name)
        name_entry.configure(state="readonly")
        name_entry.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(exam_frame, text="日期:").grid(row=0, column=2, padx=5)
        date_entry = ctk.CTkEntry(exam_frame)
        date_entry.insert(0, date)
        date_entry.configure(state="readonly")
        date_entry.grid(row=0, column=3, padx=5)
        
        delete_button = ctk.CTkButton(exam_frame, text="删除", command=lambda e=exam_frame, n=name: self.delete_exam(e, n))
        delete_button.grid(row=0, column=4, padx=5)
        
        self.exam_list.append((exam_frame, name_entry, date_entry))
    
        # 清空输入框
        self.new_exam_name.delete(0, tk.END)
        self.new_exam_date.delete(0, tk.END)

    def delete_exam(self, exam_frame, name):
        # 从配置中删除
        info["countdowns"] = [exam for exam in info["countdowns"] if exam["name"] != name]
        self.exam_options = [exam["name"] for exam in info["countdowns"]] + ["设置"]
        self.parent.exam_menu.configure(values=self.exam_options)
        self.parent.exam_menu.set(self.exam_options[0])
        self.parent.update_label()

        # 从界面中删除
        exam_frame.destroy()

    def add_encouragement(self):
        encouragement = self.new_encouragement.get().strip()
        if not encouragement:
            self.parent.show_message("警告", "加油语不能为空！")
            return

        # 添加到配置
        info["encouragements"].append(encouragement)

        # 更新设置窗口
        encouragement_frame = ctk.CTkFrame(self.encouragement_frame)
        encouragement_frame.pack(fill=tk.X, pady=5)
        
        encouragement_entry = ctk.CTkEntry(encouragement_frame)
        encouragement_entry.insert(0, encouragement)
        encouragement_entry.configure(state="readonly")
        encouragement_entry.pack(side=tk.LEFT, padx=5)
        
        delete_button = ctk.CTkButton(encouragement_frame, text="删除", command=lambda e=encouragement_frame, c=encouragement: self.delete_encouragement(e, c))
        delete_button.pack(side=tk.LEFT, padx=5)
        
        self.encouragement_list.append((encouragement_frame, encouragement_entry))
        self.new_encouragement.delete(0, tk.END)

    def delete_encouragement(self, encouragement_frame, encouragement):
        info["encouragements"] = [c for c in info["encouragements"] if c != encouragement]
        encouragement_frame.destroy()

    def destroy(self):
        global settings_open
        settings_open = False
        super().destroy()

def restart_app(self):
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == '__main__':
    try:
        app = CountdownApp()
        app.mainloop()
    except Exception as e:
        app.show_message("错误", f"{str(e)}")
