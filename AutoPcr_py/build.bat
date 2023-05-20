@echo off

echo. 建立临时文件夹
md TMP
md TMP\img

echo. 复制资源
XCOPY  .\AutoPcr4.0.py .\TMP\ /Y
XCOPY  .\AutoPcr4.0.spec .\TMP\ /Y
XCOPY  .\AutoPcr4.0_GUI.py .\TMP\ /Y
XCOPY  .\AutoPcr4.0_GUI.spec .\TMP\ /Y
XCOPY  .\CloseLeiDian.cmd .\TMP\ /Y
XCOPY  .\config.ini .\TMP\ /Y
XCOPY  .\StartCmd.cmd .\TMP\ /Y
XCOPY  .\StartLeiDian.cmd .\TMP\ /Y
XCOPY  .\StartLeiDian1.cmd .\TMP\ /Y
XCOPY  .\运行说明\模拟器配置\com.bilibili.priconne_1280x720(pcr).kmp .\TMP\ /Y
XCOPY  .\运行说明\使用说明.txt .\TMP\ /Y
XCOPY  .\img .\TMP\img\ /q /e /r /S /Y

echo. 打包cmd
cd .\TMP
pyinstaller  .\AutoPcr4.0.spec
MOVE .\dist\AutoPcrCmd.exe .\

echo. 打包exe
pyinstaller   .\AutoPcr4.0_GUI.spec
MOVE .\dist\AutoPcr.exe .\

echo. 打包zip
rd /s /q .\build
rd /s /q .\dist
del .\AutoPcr4.0.py
del .\AutoPcr4.0.spec
del .\AutoPcr4.0_GUI.py
del .\AutoPcr4.0_GUI.spec

cd ..
python -m zipfile -c AutoPcr.zip .\TMP\AutoPcr.exe .\TMP\AutoPcrCmd.exe .\TMP\CloseLeiDian.cmd .\TMP\config.ini .\TMP\StartCmd.cmd .\TMP\StartLeiDian.cmd .\TMP\StartLeiDian1.cmd .\TMP\com.bilibili.priconne_1280x720(pcr).kmp .\TMP\使用说明.txt .\TMP\img\

echo. 删除临时文件夹
rd /s /q .\TMP

timeout \t 60