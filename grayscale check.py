import tkinter as tk
from tkinter import Toplevel
import cv2
import numpy as np
import mss
from PIL import Image, ImageTk
import ctypes

# 隐藏控制台窗口的设置
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
hWnd = kernel32.GetConsoleWindow()
if hWnd:
    user32.ShowWindow(hWnd, 0)

class GrayscaleApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Real-time Grayscale View")
        self.window.attributes('-topmost', True)  # 设置主窗口始终置顶
        self.window.minsize(width=200, height=100)  # 设置主窗口的最小尺寸

        self.label = tk.Label(self.window)
        self.label.pack(expand=True, fill=tk.BOTH)

        # 创建一个独立的窗口用于放置滑块
        self.control_window = Toplevel(self.window)
        self.control_window.title("Control Panel")
        self.control_window.attributes('-topmost', False)
        self.control_window.minsize(width=240, height=100)

        # 图像缩放滑块
        self.scale_slider = tk.Scale(self.control_window, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, label="Scale Image")
        self.scale_slider.pack(fill=tk.X)
        self.scale_slider.set(1)
        self.scale_slider.bind("<ButtonRelease-1>", self.handle_scale_change)

        # 图像刷新频率滑块
        self.refresh_rate_slider = tk.Scale(self.control_window, from_=100, to=2000, resolution=100, orient=tk.HORIZONTAL, label="Refresh Rate (ms)")
        self.refresh_rate_slider.pack(fill=tk.X)
        self.refresh_rate_slider.set(1000)
        self.refresh_rate_slider.bind("<ButtonRelease-1>", self.handle_refresh_rate_change)

        self.monitor = None
        self.image = None
        self.refresh_rate = 1000  # 默认刷新频率1000ms

        self.window.withdraw()  # 初始隐藏主窗口

        # 拖拽窗口功能
        self.label.bind('<Button-1>', self.start_move)
        self.label.bind('<ButtonRelease-1>', self.stop_move)
        self.label.bind('<B1-Motion>', self.do_move)

        self.x = None
        self.y = None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def select_area(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            screen_img = np.array(sct_img)
            screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)
            cv2.namedWindow("Select Area", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Select Area", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            area = cv2.selectROI("Select Area", screen_img, False, False)
            cv2.destroyAllWindows()
            if area[2] and area[3]:
                self.monitor = {"top": int(area[1]), "left": int(area[0]), "width": int(area[2]), "height": int(area[3])}
                self.update_image()

        self.window.deiconify()  # 选择区域后显示主窗口

    def update_image(self):
        if self.monitor:
            with mss.mss() as sct:
                img = sct.grab(self.monitor)
                gray_img = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2GRAY)
                self.image = Image.fromarray(gray_img)
            self.refresh_image()
            self.window.after(self.refresh_rate, self.update_image)

    def refresh_image(self):
        if self.image:
            new_width = int(self.monitor['width'] * self.scale_slider.get())
            new_height = int(self.monitor['height'] * self.scale_slider.get())
            img_tk = ImageTk.PhotoImage(self.image.resize((new_width, new_height), Image.LANCZOS))
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)
            self.window.geometry(f'{new_width}x{new_height}')  # 确保窗口大小匹配图像大小

    def handle_scale_change(self, event):
        self.refresh_image()

    def handle_refresh_rate_change(self, event):
        self.refresh_rate = self.refresh_rate_slider.get()

    def run(self):
        self.select_area()
        self.window.mainloop()

if __name__ == "__main__":
    app = GrayscaleApp()
    app.run()
