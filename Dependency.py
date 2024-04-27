import subprocess
import sys

def install_packages():
    packages = ["opencv-python", "numpy", "mss", "Pillow"]
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages()
