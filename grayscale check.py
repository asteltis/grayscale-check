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
        self.window.minsize(width=220, height=40)  # 设置主窗口的最小尺寸

        self.label = tk.Label(self.window)
        self.label.pack(expand=True, fill=tk.BOTH)

        # 创建一个独立的窗口用于放置滑块，取消置顶
        self.control_window = tk.Toplevel(self.window)
        self.control_window.title("Control Panel")
        self.control_window.attributes('-topmost', False)  # 取消控制面板的置顶
        self.control_window.minsize(width=220, height=40)  # 设置控制面板的最小尺寸

        self.scale = tk.Scale(self.control_window, from_=0.5, to=2.5, resolution=0.1, orient=tk.HORIZONTAL, label="Scale Image")
        self.scale.pack(fill=tk.X)
        self.scale.set(1)  # 默认比例是1
        self.scale.bind("<ButtonRelease-1>", self.handle_scale_change)

        self.monitor = None
        self.image = None

        self.window.withdraw()  # 初始隐藏主窗口

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
            self.window.after(800, self.update_image)

    def refresh_image(self):
        if self.image:
            new_width = int(self.monitor['width'] * self.scale.get())
            new_height = int(self.monitor['height'] * self.scale.get())
            img_tk = ImageTk.PhotoImage(self.image.resize((new_width, new_height), Image.LANCZOS))
            self.label.imgtk = img_tk
            self.label.configure(image=img_tk)
            self.window.geometry(f'{new_width}x{new_height}')  # 确保窗口大小匹配图像大小

    def handle_scale_change(self, event):
        self.refresh_image()

    def run(self):
        self.select_area()
        self.window.mainloop()

if __name__ == "__main__":
    app = GrayscaleApp()
    app.run()
