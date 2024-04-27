# grayscale-check
一个独立的小窗能够实时检查黑白灰关系，支持csp(Clip Studio Paint)、sai2（PaintTool SAI2）等。
# 功能
实时显示黑白灰： 用户选定区域后，将新建一个独立窗口实时显示选定区域的灰度图像。
![PixPin_2024-04-27_11-36-12](https://github.com/asteltis/grayscale-check/assets/145424226/f65f4de4-23de-4a56-b848-9940ba3f0ebc)
# 使用方法
## Windows
1. 下载： 右侧Release下载grayscale check.exe。
2. 启动： 运行grayscale check.exe后，将让你选择一个区域。
3. 选择区域： 通过鼠标拖动来选择一个屏幕区域，然后按 Enter 或 Space 确认。
4. 查看实时图像： 选定区域后，一个新窗口将会显示该区域的实时黑白图像。
# 注意事项
1. 滑块窗口可调整图像大小默认1.0倍和图像捕捉时间默认1000ms（1s=1000ms）。
2. 暂时不支持从窗口调整选择区域范围。如果想要调整，请关闭窗口，再启动grayscale check.exe重新选择区域。
3. 因为是实时捕获目标图像，所以不建议对选定区域进行任何遮挡。
#  为什么做这个
csp观察黑白灰时要不断开关图层太麻烦了。
