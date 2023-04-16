import sys
from sysconfig import get_path
from xmlrpc.client import Boolean
import PySimpleGUI as sg
from configparser import ConfigParser
from importlib.resources import path
from re import A
import os
from ctypes import *
import win32api
import win32gui
import win32ui
import win32con
import win32api
import webbrowser

# Glabol
print("path ", os.path.dirname(sys.executable))
# print("path " , os.getcwd())

curDir = os.path.dirname(__file__)
# 图片路径拼接


def GetFullPath(pngName):
    # global curDir
    # return os.path.join(curDir, pngName)
    return '.\\' + pngName


# ======读取配置======
mnqIndexKey = 'mnqDrop'
dxcDropKey = 'dxcDrop'
needZbNameKey = 'zbDrop'
buyExpNumKey = 'buyExpNumDrop'
buyDxcNumKey = 'buyDxcNumDrop'
buyDxcRowKey = 'buyDxcRowDrop'
dxcDropValue = ["黑白王"]
mnqIndexDropValue = ["1", "0"]
needZbNameValue = ['新月的悲叹', '焰帝戒指', '忘哭之冠', '深渊之弓', '愤怒法杖', '鹰神之煌剑', '狮鹫羽饰', '恶魔法杖']
buyExpNumValue = [1, 2, 3, 4, 5, 6, 7, 8]
buyDxcNumValue = [1, 2, 3, 4, 5, 6, 7, 8]
buyDxcRowValue = [1, 2, 3, 4]

cfg = ConfigParser()
configPath = GetFullPath('config.ini')
cfg.read(configPath, 'utf-8')
mnqIndex = cfg.get('MainSetting', mnqIndexKey)
MainSettingKey = 'MainSetting_' + mnqIndex


def SetConfigAuto(key, AllValues):
    SetConfig(key, str(AllValues[key]))


def SetConfig(key, value):
    cfg.set(MainSettingKey, key, value)


def ReadStrConfig(key):
    window[key].Update(GetStrConfig(key))


def ReadBoolConfig(key):
    window[key].Update(GetBoolConfig(key))


def GetStrConfigDefault(key, defautValu):
    tmpV = GetStrConfig_Main(key)
    if (tmpV == ''):
        tmpV = defautValu
        print(key, " setDefaut =>", defautValu)
    return tmpV


def GetStrConfig_Main(key):
    try:
        return cfg.get("MainSetting", key)
    except:
        return ""


def GetStrConfig(key):
    try:
        return cfg.get(MainSettingKey, key)
    except:
        return ""


def GetBoolConfig(boolKey):
    try:
        return Boolean(cfg.get(MainSettingKey, boolKey) == 'True')
    except:
        return False


def SetCurMnqIndex():
    cfg.set('MainSetting', mnqIndexKey, mnqIndex)
    cfg.set('MainSetting', moniqTimeKey, moniqTime)


def SetMnqDir():
    print(LeiDianDir)
    cfg.set('MainSetting', LeiDianDirKey, LeiDianDir)


isRunAndStart = False
isAutoClose = False

StartRunName = "启动模拟器并运行"
RunName = "运行"

isJJCKey = 'isJJC'
isTansuoKey = 'isTansuo'
isDxcKey = 'isDxc'
isSkipDxcKey = 'isSkipDxc'
dxcGroupDaoZhongKey = 'DxcGroupDaoZhong'
isExpKey = 'isExp'
isStoneKey = 'isStone'
isDxcShopKey = 'isDxcShop'
isNiuDanKey = 'isNiuDan'
LeiDianDirKey = 'LeiDianDir'
isRunAndStartKey = 'isRunAndStart'
isAutoCloseKey = 'isAutoClose'
isFor64Key = 'isFor64'

# newKey
isXQBKey = 'isXQB'
isXinSuiKey = 'isXinSui'
isSendKey = 'isSend'
isNeedSeedKey = 'isNeedSeed'

isHomeTakeKey = 'isHomeTake'
isJuQingHuoDongKey = 'isJuQingHuoDong'
isFuKeHuoDongKey = 'isFuKeHuoDong'
isHouDongHardKey = 'isHouDongHard'
huoDongHardKeys = 'huoDongHard'
isVHBossKey = 'isVHBoss'
needZbNameKey = 'needZbName'
#isBuyMoreExpKey = 'isBuyMoreExp'
isTuituKey = 'isTuituKey'
isAutoTaskKey = 'isAutoTask'
isDianZanKey = 'isDianZan'
moniqTimeKey = 'moniqTime'

isJJC = GetBoolConfig(isJJCKey)
isTansuo = GetBoolConfig(isTansuoKey)
isDxc = GetBoolConfig(isDxcKey)
isSkipDxc = GetBoolConfig(isSkipDxcKey)
dxcBoss = GetStrConfig(dxcDropKey)
dxcGroupDaoZhong = GetStrConfig(dxcGroupDaoZhongKey)
isExp = GetBoolConfig(isExpKey)
isStone = GetBoolConfig(isStoneKey)
buyExpNum = GetStrConfig(buyExpNumKey)
isDxcShop = GetBoolConfig(isDxcShopKey)
buyDxcNum = GetStrConfig(buyDxcNumKey)
buyDxcRow = GetStrConfig(buyDxcRowKey)

isNiuDan = GetBoolConfig(isNiuDanKey)
isXinSui = GetBoolConfig(isXinSuiKey)
isXQB = GetBoolConfig(isXQBKey)
isSend = GetBoolConfig(isSendKey)
isNeedSeed = GetBoolConfig(isNeedSeedKey)
isAutoClose = GetBoolConfig(isAutoCloseKey)
isTuitu = GetBoolConfig(isTuituKey)
isAutoTask = GetBoolConfig(isAutoTaskKey)
isFor64 = GetBoolConfig(isFor64Key)
#isBuyMoreExp = GetBoolConfig(isBuyMoreExpKey)
isRunAndStart = False

isHomeTake = GetBoolConfig(isHomeTakeKey)
isJuQingHuoDong = GetBoolConfig(isJuQingHuoDongKey)
isFuKeHuoDong = GetBoolConfig(isFuKeHuoDongKey)
isHouDongHard = GetBoolConfig(isHouDongHardKey)
huoDongHard = GetStrConfig(huoDongHardKeys)
isVHBoss = GetBoolConfig(isVHBossKey)
isDianZan = GetBoolConfig(isDianZanKey)

LeiDianDir = cfg.get('MainSetting', LeiDianDirKey)
moniqTime = GetStrConfigDefault(moniqTimeKey, '20')

needZbName = GetStrConfig(needZbNameKey)

# new
DxcDuiWu = '1,2,3'
isAllSelectKey = 'isAllSelect'
isAllSelect = False


# 保存配置
def SavaConfig(AllValues):
    RunTimeValue()
    SetConfigAuto(isJJCKey, AllValues)
    SetConfigAuto(isTansuoKey, AllValues)
    SetConfigAuto(isDxcKey, AllValues)
    SetConfigAuto(isSkipDxcKey, AllValues)
    SetConfigAuto(dxcGroupDaoZhongKey, AllValues)
    SetConfigAuto(isExpKey, AllValues)
    SetConfigAuto(isStoneKey, AllValues)

    SetConfigAuto(isDxcShopKey, AllValues)
    SetConfigAuto(buyDxcNumKey, AllValues)
    SetConfigAuto(buyDxcRowKey, AllValues)
    SetConfigAuto(isNiuDanKey, AllValues)
    SetConfigAuto(isAutoCloseKey, AllValues)
    SetConfigAuto(isFor64Key, AllValues)  # new

    SetConfigAuto(isXQBKey, AllValues)
    SetConfigAuto(isXinSuiKey, AllValues)

    SetConfigAuto(isSendKey, AllValues)
    SetConfigAuto(isNeedSeedKey, AllValues)
    SetConfigAuto(dxcDropKey, AllValues)
    SetConfigAuto(isTuituKey, AllValues)
    SetConfigAuto(isAutoTaskKey, AllValues)
    #SetConfigAuto(isBuyMoreExpKey, AllValues)

    SetConfigAuto(isHomeTakeKey, AllValues)
    SetConfigAuto(isJuQingHuoDongKey, AllValues)
    SetConfigAuto(isFuKeHuoDongKey, AllValues)
    SetConfigAuto(isHouDongHardKey, AllValues)
    SetConfigAuto(huoDongHardKeys, AllValues)
    SetConfigAuto(isVHBossKey, AllValues)
    SetConfigAuto(isDianZanKey, AllValues)

    SetConfigAuto(needZbNameKey, AllValues)

    # SetConfigAuto(LeiDianDirKey,AllValues)
    global LeiDianDir
    LeiDianDir = AllValues[LeiDianDirKey]
    SetCurMnqIndex()
    SetMnqDir()

    with open(configPath, "w+", encoding='utf-8') as f:
        cfg.write(f)


def ReadConfig():
    RunTimeValue()
    ReadBoolConfig(isJJCKey)
    ReadBoolConfig(isTansuoKey)
    ReadBoolConfig(isDxcKey)
    ReadBoolConfig(isExpKey)
    ReadBoolConfig(isStoneKey)
    ReadBoolConfig(isDxcShopKey)
    ReadBoolConfig(isNiuDanKey)
    ReadBoolConfig(isAutoCloseKey)
    ReadBoolConfig(isFor64Key)
    # new
    ReadBoolConfig(isXQBKey)
    ReadBoolConfig(isXinSuiKey)
    ReadBoolConfig(isSkipDxcKey)
    ReadBoolConfig(isSendKey)
    ReadBoolConfig(isNeedSeedKey)
    ReadBoolConfig(isHomeTakeKey)
    ReadBoolConfig(isJuQingHuoDongKey)
    ReadBoolConfig(isFuKeHuoDongKey)
    ReadBoolConfig(isHouDongHardKey)
    ReadStrConfig(huoDongHardKeys)
    ReadBoolConfig(isVHBossKey)
    ReadBoolConfig(isTuituKey)
    ReadBoolConfig(isAutoTaskKey)
    #ReadBoolConfig(isBuyMoreExpKey)
    ReadBoolConfig(isDianZanKey)

    ReadStrConfig(dxcDropKey)
    ReadStrConfig(needZbNameKey)

    ReadStrConfig(moniqTimeKey)
    # ReadStrConfig(mnqIndexKey,AllValues)


def WriteCmds():
    path = str(LeiDianDir)
    index = str(mnqIndex)
    WriteLeiDian(path, index)
    WriteCloseLeidian(path)
    # WirteStartPy()


def WriteCloseLeidian(path):
    print('write ', path, 'CloseLeiDian.cmd')
    fileName = 'CloseLeiDian.cmd'
    with open(GetFullPath(fileName), 'w') as f:
        cmdStr = ("cd /d " + path + "\n\ndnconsole.exe quitall\n\nexit")
        f.write(cmdStr)


def WriteLeiDian(path, index):
    print('write ', path, 'StartLeiDian.cmd')
    fileName = 'StartLeiDian.cmd'
    if (index == '1'):
        fileName = 'StartLeiDian1.cmd'
    with open(GetFullPath(fileName), 'w') as f:
        cmdStr = ("cd /d " + path + "\n\ndnconsole.exe launchex --index " + index + " --packagename com.bilibili.priconne\n\nexit")
        f.write(cmdStr)


# def WirteStartPy():
# 	with open(GetFullPath('StartPy.cmd'),'w') as f:
# 		cmdStr =("python "+curDir+"\AutoPcr4.0.py\n\nexit")
# 		f.write(cmdStr)

# def WirteStart(path):
# 	with open(GetFullPath('start.cmd'),'w') as f:
# 		print('write ',path,'start.cmd')
# 		cmdStr  = "start call "+curDir+"\startPy.cmd\n\n"+"cd /d "+ path+"\n\ndnconsole.exe launchex --index 0 --packagename com.bilibili.priconne\n\nexit"
# 		f.write(cmdStr)


def CallLeiDian():
    index = str(mnqIndex)
    if (index == '0'):
        win32api.ShellExecute(0, 'open', GetFullPath('StartLeiDian.cmd'), '', '', 1)
    if (index == '1'):
        win32api.ShellExecute(0, 'open', GetFullPath('StartLeiDian1.cmd'), '', '', 1)


def CallPy():
    if os.path.exists(GetFullPath('AutoPcr4.0.py')):
        win32api.ShellExecute(0, 'open', GetFullPath('AutoPcr4.0.py'), '', '', 1)  # 运行程序
    else:
        win32api.ShellExecute(0, 'open', GetFullPath('AutoPcrCmd.exe'), '', '', 1)  # 运行程序


def StartPcr():
    CallLeiDian()
    CallPy()


sg.theme('SystemDefaultForReal')
sg.set_global_icon('img/other/icon.ico')
main_col = [
    [sg.Text('日常功能'), sg.Checkbox('', isAllSelect, key=isAllSelectKey, enable_events=True)],
    [
        sg.Checkbox('竞技场', isJJC, key=isJJCKey),
        sg.Checkbox('探索', isTansuo, key=isTansuoKey),
        sg.Checkbox('地下城', isDxc, key=isDxcKey),
    ],
    [
        sg.Checkbox('购买经验', isExp, key=isExpKey),
        sg.Checkbox('购买石头', isStone, key=isStoneKey),
        sg.Text('购买次数'),
        sg.DropDown(buyExpNumValue, buyExpNum, key=buyExpNumKey, size=(2, None)),
    ],
    [
        sg.Checkbox('消耗地下城币', isDxcShop, key=isDxcShopKey),
        sg.Text('行数'),
        sg.DropDown(buyDxcRowValue, buyDxcRow, key=buyDxcRowKey, size=(2, None)),
        sg.Text('次数'),
        sg.DropDown(buyDxcNumValue, buyDxcNum, key=buyDxcNumKey, size=(2, None)),
    ],
    [
        sg.Checkbox('扭蛋', isNiuDan, key=isNiuDanKey),
        sg.Checkbox('领取奖励', isHomeTake, key=isHomeTakeKey),
    ],
    [
        sg.Checkbox('星球杯', isXQB, key=isXQBKey),
        sg.Checkbox('心之碎片', isXinSui, key=isXinSuiKey),
    ],
    [
        sg.Checkbox('请求捐赠', isNeedSeed, key=isNeedSeedKey),
        sg.DropDown(needZbNameValue, needZbName, key=needZbNameKey, size=(10, None)),
    ],
    [
        sg.Checkbox('赠送礼物', isSend, key=isSendKey),
        sg.Checkbox('点赞', isDianZan, key=isDianZanKey),
    ],
]
hd_col = [
    [
        sg.Checkbox('剧情活动', isJuQingHuoDong, key=isJuQingHuoDongKey),
        sg.Checkbox('复刻活动', isFuKeHuoDong, key=isFuKeHuoDongKey),
    ],
    [
        sg.Checkbox('困难本', isHouDongHard, key=isHouDongHardKey),
        sg.Text('关卡'),
        sg.InputText(huoDongHard, size=(8, None), key=huoDongHardKeys),
        sg.Checkbox('VHBoss', isVHBoss, key=isVHBossKey)
    ],
]
duli_col = [
    [
        sg.Checkbox('自动剧情', isAutoTask, text_color='green', key=isAutoTaskKey),
        sg.Checkbox('自动推图', isTuitu, text_color='green', key=isTuituKey),
        sg.Text('需要单独使用', text_color='red'),
    ],
]
left_col = [
    [sg.Frame('日常', layout=main_col, expand_x=True)],
    [sg.Frame('活动', layout=hd_col, expand_x=True)],
    [sg.Frame('独立功能', layout=duli_col, expand_x=True)],
]

dxc_col = [
    [sg.Text('地下城'), sg.DropDown(dxcDropValue, dxcBoss, key=dxcDropKey, size=(10, None)),
     sg.Checkbox('扫荡', isSkipDxc, key=isSkipDxcKey)],
    [sg.Text('编组-队伍 编组:1~5 队伍:1~3')],
    [sg.Text('道中队:'), sg.InputText(dxcGroupDaoZhong, size=(35, None), key=dxcGroupDaoZhongKey)],
]
other_col = [
    [
        sg.Text('模拟器序号'),
        sg.DropDown(mnqIndexDropValue, mnqIndex, enable_events=True, size=(8, None), key=mnqIndexKey),
        sg.Checkbox('自动关闭', isAutoClose, key=isAutoCloseKey),
        sg.Checkbox('64位', isFor64, key=isFor64Key)
    ],
    [sg.Text('模拟器启动等待时间'), sg.InputText(moniqTime, size=(6, None), key=moniqTimeKey)],
    [sg.Text('雷电模拟器文件夹:')],
    [sg.InputText(LeiDianDir, size=(30, None), key=LeiDianDirKey), sg.FolderBrowse()],
    [sg.Button('保存配置'), sg.Button(StartRunName), sg.Button(RunName), sg.Button('检查模拟器')],
]
menu_col = [
    [sg.Text('项目地址', font='underline', enable_events=True, key="URL")],
]
right_col = [
    [sg.Frame('地下城', layout=dxc_col, expand_x=True)],
    [sg.Frame('模拟器配置', layout=other_col, expand_x=True, expand_y=True)],
    [sg.Frame('关于', layout=menu_col, expand_x=True)],
]

# menu_def = [
#     [sg.Text('下载地址', enable_events=True, key="URL")],
# ]

layout = [
    # [sg.Pane(
    #[sg.Menu(menu_def)],
    [
        sg.Column(left_col, element_justification='l', expand_x=True, expand_y=True),
        sg.Column(right_col, element_justification='l', expand_x=True, expand_y=True)
    ]
    # , orientation='h', relief=sg.RELIEF_SUNKEN, k='-PANE-')]
]

# Create the Window
window = sg.Window('AutoPcr', layout, font=('黑体', 13))


def RunTimeValue():
    global isRunAndStart, mnqIndex, MainSettingKey, moniqTime
    mnqIndex = values[mnqIndexKey]
    MainSettingKey = 'MainSetting_' + mnqIndex
    moniqTime = values[moniqTimeKey]
    print('MainSettingKey = ', MainSettingKey)


def SetAllSelect():
    window[isJJCKey].Update(isAllSelect)
    window[isTansuoKey].Update(isAllSelect)
    window[isDxcKey].Update(isAllSelect)
    window[isExpKey].Update(isAllSelect)
    window[isStoneKey].Update(isAllSelect)
    window[isDxcShopKey].Update(isAllSelect)
    window[isNiuDanKey].Update(isAllSelect)
    window[isHomeTakeKey].Update(isAllSelect)
    window[isXQBKey].Update(isAllSelect)
    window[isXinSuiKey].Update(isAllSelect)
    window[isNeedSeedKey].Update(isAllSelect)
    window[isSendKey].Update(isAllSelect)
    window[isDianZanKey].Update(isAllSelect)


# def OutLog():
#     yield
#     fname = './autopcr.log'
#     with open(fname, 'r', encoding='gbk') as f:
#         lines = f.readlines()
#         last_line = lines[-1]
#         print(last_line)

# log = OutLog()
# sg.popup_get_folder('Enter the file you wish to process')
# Event Loop to process "events" and get the "values" of the inputs
while True:
    # print("next")
    # next(log)

    event, values = window.read()
    print(event)
    if event == '检查模拟器':
        MainhWnd = win32gui.FindWindow('LDPlayerMainFrame', None)
        if (MainhWnd == 0):
            print("没有检测到雷电模拟器启动")
            continue
        isFor64 = values[isFor64Key]
        winName = win32gui.GetWindowText(MainhWnd)
        isCur64 = False
        if (winName.endswith("(64)")):
            isCur64 = True

        targetName = "雷电模拟器"
        cmpName = ""
        print("Find", MainhWnd, winName)
        if (values[mnqIndexKey] == "0"):
            targetName = "雷电模拟器"
        elif (values[mnqIndexKey] == "1"):
            targetName = "雷电模拟器-1"

        weiShu = "32"
        cmpName = targetName
        if (isFor64):
            cmpName = targetName + "(64)"
            weiShu = "64"

        moniqWeiShu = "32"
        if (isCur64):
            moniqWeiShu = "64"

        if (isCur64 != isFor64):
            print("设置位数错误,设置位数:", weiShu, "应该设置为:", moniqWeiShu)
            continue

        if (cmpName == winName):
            print("模拟器名字正确")
        else:
            print("模拟器名字或序号错误! 请求目标模拟器名为", targetName, "而正运行的模拟器名为", winName)

    if event == isAllSelectKey:
        isAllSelect = bool(1 - isAllSelect)
        SetAllSelect()

    if event == mnqIndexKey:
        ReadConfig()

    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        print("close")
        os._exit(0)
        break
    if event == '保存配置':
        print('初始化配置')
        SavaConfig(values)
        WriteCmds()
    if ((event == RunName) | (event == StartRunName)):
        SetConfig(isRunAndStartKey, str(event == StartRunName))
        SavaConfig(values)
        StartPcr()
    if event == "URL":
        webbrowser.open("https://github.com/mackerel-12138/AutoPcr")