# grayscale-check
能够实时检查黑白灰关系，支持csp(Clip Studio Paint)、sai2（PaintTool SAI2）等。
# 功能
实时显示黑白灰： 用户选定区域后，将新建一个独立窗口实时显示选定区域的黑白灰。
![PixPin_2024-04-27_11-36-12](https://github.com/asteltis/grayscale-check/assets/145424226/f65f4de4-23de-4a56-b848-9940ba3f0ebc)
# 使用方法
## Windows
1. 下载： 下载grayscale check.exe。
2. 启动： 运行grayscale check.exe后，将让你选择一个区域。
3. 选择区域： 通过鼠标拖动来选择一个屏幕区域，然后按 Enter 或 Space 确认。
4. 查看实时图像： 选定区域后，一个新窗口将会显示该区域的实时黑白图像。
# 注意事项
1. 如果想调整窗口的捕捉时间（默认为1s），可以对grayscale check.py中的1000（1s=1000ms）进行修改。exe暂不支持。
2. 暂时不支持从窗口调整区域大小。如果想要调整，请关闭窗口，再启动grayscale check.exe重新选择区域。
3. 因为是实时捕获目标图像，所以不建议对选定区域进行任何遮挡。
#  为什么做这个
因为不会ps，而且其他要观察黑白灰时不断开关图层太麻烦了。
