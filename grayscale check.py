import cv2
import numpy as np
import mss
from PIL import Image, ImageTk
import tkinter as tk

class GrayscaleApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.minsize(width=240, height=30)
        self.label = tk.Label(self.window)
        self.label.pack(expand=True, fill=tk.BOTH)
        self.monitor = None

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

            if area[2] and area[3]:  # 确保选择的区域有效
                self.monitor = {"top": int(area[1]), "left": int(area[0]), "width": int(area[2]), "height": int(area[3])}
                self.window.title("Real-time Grayscale View")
                self.window.geometry(f"{self.monitor['width']}x{self.monitor['height']}")
                self.window.attributes('-topmost', True)
                self.update_image()

    def update_image(self):
        if self.monitor is not None:
            with mss.mss() as sct:
                img = sct.grab(self.monitor)
                gray_img = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2GRAY)
                img_pil = Image.fromarray(gray_img)
                img_tk = ImageTk.PhotoImage(image=img_pil)
                self.label.imgtk = img_tk
                self.label.configure(image=img_tk)
            self.window.after(1000, self.update_image)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = GrayscaleApp()
    app.select_area()
    app.run()
