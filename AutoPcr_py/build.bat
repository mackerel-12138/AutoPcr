@echo off

echo. ������ʱ�ļ���
md TMP
md TMP\img

echo. ������Դ
XCOPY  .\AutoPcr4.0.py .\TMP\ /Y
XCOPY  .\AutoPcr4.0_GUI.py .\TMP\ /Y
XCOPY  .\AutoPcr.spec .\TMP\ /Y
XCOPY  .\AutoPcr4.0.spec .\TMP\ /Y
XCOPY  .\CloseLeiDian.cmd .\TMP\ /Y
XCOPY  .\config.ini .\TMP\ /Y
XCOPY  .\StartCmd.cmd .\TMP\ /Y
XCOPY  .\StartLeiDian.cmd .\TMP\ /Y
XCOPY  .\StartLeiDian1.cmd .\TMP\ /Y
XCOPY  .\����˵��\ģ��������\com.bilibili.priconne_960x540.kmp .\TMP\ /Y
XCOPY  .\img .\TMP\img\ /q /e /r /S /Y

echo. ���cmd
cd .\TMP
pyinstaller  .\AutoPcr4.0.spec
MOVE .\dist\AutoPcrCmd.exe .\

echo. ���exe
pyinstaller   .\AutoPcr.spec
MOVE .\dist\AutoPcr.exe .\

echo. ���zip
rd /s /q .\build
rd /s /q .\dist
del .\AutoPcr.spec
del .\AutoPcr4.0.spec
del .\AutoPcr4.0.py
del .\AutoPcr4.0_GUI.py

cd ..
python -m zipfile -c AutoPcr.zip .\TMP\AutoPcr.exe .\TMP\AutoPcrCmd.exe .\TMP\CloseLeiDian.cmd .\TMP\config.ini .\TMP\StartCmd.cmd .\TMP\StartLeiDian.cmd .\TMP\StartLeiDian1.cmd .\TMP\com.bilibili.priconne_960x540.kmp .\TMP\img\

echo. ɾ����ʱ�ļ���
rd /s /q .\TMP