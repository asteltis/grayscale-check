import tkinter as tk
from tkinter import Toplevel, messagebox
import cv2
import numpy as np
import mss
from PIL import Image, ImageTk
import ctypes
import configparser
import os
import time
from typing import Dict, Optional

# 常量
MIN_WINDOW_WIDTH = 200
MIN_WINDOW_HEIGHT = 100
MIN_CONTROL_WINDOW_WIDTH = 240
MIN_CONTROL_WINDOW_HEIGHT = 155
SCALE_RANGE = (0.1, 3.0)
REFRESH_RATE_RANGE = (0.02, 1.50)
CONFIG_FILE = os.path.join(os.getcwd(), 'settings.ini')

# 隐藏控制台窗口
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
hWnd = kernel32.GetConsoleWindow()
if hWnd:
    user32.ShowWindow(hWnd, 0)

# 配置管理类
class ConfigManager:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config['Settings'] = {
                'scale': '1.0',
                'refresh_rate': '1.0',
                'main_window_x': '100',
                'main_window_y': '100',
                'control_window_x': '200',
                'control_window_y': '200'
            }
            self.save_settings()

    def save_settings(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get(self, section: str, option: str, fallback: str) -> str:
        return self.config.get(section, option, fallback=fallback)

    def set(self, section: str, option: str, value: str):
        self.config.set(section, option, value)

    def save_on_close(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

# 截图管理类
class ScreenshotManager:
    def __init__(self):
        self.monitor = None

    def select_area(self) -> Optional[Dict[str, int]]:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            screen_img = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
            cv2.namedWindow("Select Area", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Select Area", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            area = cv2.selectROI("Select Area", screen_img, False, False)
            cv2.destroyAllWindows()
            if area[2] and area[3]:
                self.monitor = {"top": int(area[1]), "left": int(area[0]), "width": int(area[2]), "height": int(area[3])}
        return self.monitor

    def get_screenshot(self) -> Optional[np.ndarray]:
        if self.monitor:
            with mss.mss() as sct:
                img = sct.grab(self.monitor)
                gray_img = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2GRAY)
                return gray_img
        return None

# 主应用程序类
class GrayscaleApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.screenshot_manager = ScreenshotManager()

        self.refresh_rate = float(self.config_manager.get('Settings', 'refresh_rate', '1.0'))
        self.scale = float(self.config_manager.get('Settings', 'scale', '1.0'))

        self.setup_main_window()
        self.setup_control_panel()

        self.image = None
        self.drag_data = {"x": 0, "y": 0}
        self.last_update_time = time.time()

        self.window.withdraw()  # 初始隐藏主窗口

    def setup_main_window(self):
        self.window = tk.Tk()
        self.window.title("Real-time Grayscale View")
        self.window.attributes('-topmost', True)
        self.window.minsize(width=MIN_WINDOW_WIDTH, height=MIN_WINDOW_HEIGHT)

        main_window_x = self.config_manager.get('Settings', 'main_window_x', '100')
        main_window_y = self.config_manager.get('Settings', 'main_window_y', '100')
        self.window.geometry(f"+{main_window_x}+{main_window_y}")

        self.label = tk.Label(self.window)
        self.label.pack(expand=True, fill=tk.BOTH)

        self.label.bind('<Button-1>', self.start_move)
        self.label.bind('<ButtonRelease-1>', self.stop_move)
        self.label.bind('<B1-Motion>', self.do_move)

        self.window.protocol("WM_DELETE_WINDOW", self.on_main_window_close)

    def setup_control_panel(self):
        self.control_window = Toplevel(self.window)
        self.control_window.title("Control Panel")
        self.control_window.attributes('-topmost', False)
        self.control_window.geometry(f"{MIN_CONTROL_WINDOW_WIDTH}x{MIN_CONTROL_WINDOW_HEIGHT}")

        self.center_control_window()

        self.scale_slider = tk.Scale(self.control_window, from_=SCALE_RANGE[0], to=SCALE_RANGE[1], resolution=0.1, orient=tk.HORIZONTAL, label="Scale Image")
        self.scale_slider.pack(fill=tk.X)
        self.scale_slider.set(self.scale)
        self.scale_slider.bind("<ButtonRelease-1>", self.handle_scale_change)

        self.refresh_rate_slider = tk.Scale(self.control_window, from_=REFRESH_RATE_RANGE[0], to=REFRESH_RATE_RANGE[1], resolution=0.02, orient=tk.HORIZONTAL, label="Refresh Rate (s)")
        self.refresh_rate_slider.pack(fill=tk.X)
        self.refresh_rate_slider.set(self.refresh_rate)
        self.refresh_rate_slider.bind("<ButtonRelease-1>", self.handle_refresh_rate_change)

        self.start_button = tk.Button(self.control_window, text="Start", command=self.start)
        self.start_button.pack(fill=tk.X)

        self.control_window.protocol("WM_DELETE_WINDOW", self.on_control_window_close)

    def center_control_window(self):
        self.control_window.update_idletasks()
        screen_width = self.control_window.winfo_screenwidth()
        screen_height = self.control_window.winfo_screenheight()
        size = tuple(int(_) for _ in self.control_window.geometry().split('+')[0].split('x'))
        x = screen_width // 2 - size[0] // 2
        y = screen_height // 2 - size[1] // 2
        self.control_window.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

    def start_move(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def stop_move(self, event):
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def do_move(self, event):
        self.move_window(event.x - self.drag_data["x"], event.y - self.drag_data["y"])

    def move_window(self, deltax: int, deltay: int):
        new_x = self.window.winfo_x() + deltax
        new_y = self.window.winfo_y() + deltay

        self.window.geometry(f"+{new_x}+{new_y}")

    def select_area(self):
        self.monitor = self.screenshot_manager.select_area()
        if self.monitor:
            self.window.deiconify()

    def update_image(self):
        current_time = time.time()
        if current_time - self.last_update_time >= self.refresh_rate:
            self.last_update_time = current_time
            if self.monitor:
                img = self.screenshot_manager.get_screenshot()
                if img is not None:
                    self.image = img
                    self.refresh_image()
        self.window.after(10, self.update_image)

    def refresh_image(self):
        if self.image is not None:
            new_width = max(int(self.monitor['width'] * self.scale_slider.get()), MIN_WINDOW_WIDTH)
            new_height = max(int(self.monitor['height'] * self.scale_slider.get()), MIN_WINDOW_HEIGHT)
            resized_image = cv2.resize(self.image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(resized_image))
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)
            self.window.geometry(f'{new_width}x{new_height}')

    def handle_scale_change(self, event):
        self.scale = self.scale_slider.get()
        self.config_manager.set('Settings', 'scale', str(self.scale))
        self.refresh_image()

    def handle_refresh_rate_change(self, event):
        self.refresh_rate = self.refresh_rate_slider.get()
        self.config_manager.set('Settings', 'refresh_rate', str(self.refresh_rate))

    def start(self):
        self.select_area()
        self.update_image()

    def run(self):
        self.window.mainloop()

    def on_main_window_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.config_manager.set('Settings', 'main_window_x', str(self.window.winfo_x()))
            self.config_manager.set('Settings', 'main_window_y', str(self.window.winfo_y()))
            self.config_manager.save_on_close()
            self.window.destroy()

    def on_control_window_close(self):
        self.config_manager.set('Settings', 'control_window_x', str(self.control_window.winfo_x()))
        self.config_manager.set('Settings', 'control_window_y', str(self.control_window.winfo_y()))
        self.config_manager.save_on_close()
        self.control_window.destroy()

if __name__ == "__main__":
    app = GrayscaleApp()
    app.run()
