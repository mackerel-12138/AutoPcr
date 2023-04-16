from asyncio.windows_events import NULL
from operator import ne
import sys
from tkinter import E
from xmlrpc.client import Boolean
import PySimpleGUI as sg
from configparser import ConfigParser
import ctypes
import inspect
from re import A
import threading
import time
import os
from ctypes import *
from PIL import ImageGrab
from PIL import Image
import aircv as ac
import keyboard
import win32gui
import win32ui
import win32con
import win32api
import win32print
import logging
from ctypes.wintypes import HWND, POINT

#logging.basicConfig(level=logging.INFO, format=lft, filemode='w', filename='./autopcr.log')
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(lineno)d %(message)s')
logger = logging.getLogger('pcr')
logger.setLevel(level=logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler('./autopcr.log', mode='w')
file_handler.setLevel(level=logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

#logger.info("path " + os.path.dirname(sys.executable))

curDir = os.path.dirname(__file__)

# 图片路径拼接


# region
def GetFullPath(pngName):
    # global curDir
    # return os.path.join(curDir, pngName)
    return '.\\' + pngName


# 利用文件是否存在判断是Exe 还是 Py文件
if (os.path.exists(GetFullPath('config.ini')) == False):
    logger.info('Exe Run')
    curDir = os.getcwd()

# endregion

waitTime = 0
minMatch = 0.7  # 最低相似度匹配
hightMatch = 0.90
warnMatch = 0.85  # 相似度小于此时, 打印黄字
nextDxcLevel = 1
StartBossIndex = 0

tMain = threading.Thread()
t0 = threading.Thread()
t1 = threading.Thread()

# region 读取配置
# 其他页面
moniqTimeKey = 'moniqTime'
dxcDropKey = 'dxcDrop'
mnqIndexKey = 'mnqDrop'
buyExpNumKey = 'buyExpNumDrop'
dxcDropValue = ["炸脖龙", "绿龙", "黑白王"]
mnqIndexDropValue = ["1", "0"]

cfg = ConfigParser()
configPath = GetFullPath('config.ini')
cfg.read(configPath, encoding='utf-8')
try:
    mnqIndex = cfg.get('MainSetting', mnqIndexKey)
    moniqTime = float(cfg.get('MainSetting', moniqTimeKey))
except:
    mnqIndex = '0'
    moniqTime = 20
MainSettingKey = 'MainSetting_' + str(mnqIndex)

# region win32初始化
# 获取后台窗口的句柄，注意后台窗口不能最小化
# 雷电模拟器 或 雷电模拟器-1 或直接None

window_title = None
MainhWnd = 0
Subhwnd = None
width = 960
height = 540
Scale = 1
saveDC = None
mfcDC = None
saveBitMap = None

# 获取真正的大小
rect = None
trueH = 0
trueW = 0
SaveH = 0
SaveW = 0
lastX = 0
lastY = 0


def winfun(hwnd, lparam):
    global Subhwnd
    subtitle = win32gui.GetWindowText(hwnd)
    if subtitle == 'TheRender':
        Subhwnd = hwnd
        logger.info("Find Subhwnd " + str(Subhwnd))


def get_real_resolution():
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    wide = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    high = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return {"wide": wide, "high": high}


def get_screen_size():
    """获取缩放后的分辨率"""
    wide = win32api.GetSystemMetrics(0)
    high = win32api.GetSystemMetrics(1)
    return {"wide": wide, "high": high}


def get_scaling():
    '''获取屏幕的缩放比例'''
    real_resolution = get_real_resolution()
    screen_size = get_screen_size()
    proportion = round(real_resolution['wide'] / screen_size['wide'], 2)
    return proportion


def WaitWin32Start():
    # 如果Main为0则等待
    global window_title, MainhWnd, Subhwnd, saveDC, mfcDC, saveBitMap, Scale, SaveH, SaveW
    global rect, trueH, trueW
    if (mnqIndex == "0"):
        window_title = "雷电模拟器"
    elif (mnqIndex == "1"):
        window_title = "雷电模拟器-1"

    if (isFor64):
        window_title = window_title + "(64)"
    logger.info("当前请求模拟器名称: " + window_title + " (如启动失败则检查多开器中的模拟器名称 和 序号)")

    MainhWnd = win32gui.FindWindow('LDPlayerMainFrame', window_title)

    while (MainhWnd == 0):
        logger.info("等待模拟器启动中...")
        time.sleep(1.5)
        MainhWnd = win32gui.FindWindow('LDPlayerMainFrame', window_title)

    # 已打开雷电
    logger.info("Find MainhWnd " + str(MainhWnd))
    win32gui.EnumChildWindows(MainhWnd, winfun, None)
    while (Subhwnd == None):
        time.sleep(1.5)
        logger.info("wait subHwnd...")
        win32gui.EnumChildWindows(MainhWnd, winfun, None)

    # 获取窗口大小
    rect = win32gui.GetClientRect(Subhwnd)
    trueH = rect[3]
    trueW = rect[2]
    Scale = get_scaling()

    logger.info("TrueH " + str(trueH) + " TrueW " + str(trueW) + " Scale " + str(Scale))
    SaveW = int(trueW * Scale)
    SaveH = int(trueH * Scale)
    logger.info("SaveH " + str(SaveH) + " SaveW " + str(SaveW))

    hWndDC = win32gui.GetWindowDC(Subhwnd)
    # 创建设备描述表
    mfcDC = win32ui.CreateDCFromHandle(hWndDC)
    # 创建内存设备描述表
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建位图对象准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    # saveBitMap.CreateCompatibleBitmap(mfcDC,trueW,trueH)
    # saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)
    saveBitMap.CreateCompatibleBitmap(mfcDC, SaveW, SaveH)
    # 将截图保存到saveBitMap中
    saveDC.SelectObject(saveBitMap)


def SavaShoot():
    # 保存bitmap到内存设备描述表
    global window_title, MainhWnd, Subhwnd, saveDC, mfcDC, saveBitMap
    # saveDC.BitBlt((0,0), (width,height), mfcDC, (0, 0), win32con.SRCCOPY)
    win32con.SRCINVERT
    saveDC.BitBlt((0, 0), (SaveW, SaveH), mfcDC, (0, 0), win32con.SRCCOPY)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    # im_PIL = Image.frombuffer('RGB',(bmpinfo['bmWidth'],bmpinfo['bmHeight']),bmpstr,'raw','BGRX',0,1)
    im_PIL = Image.frombuffer('RGB', (SaveW, SaveH), bmpstr, 'raw', 'BGRX', 0, 1)

    newImg = im_PIL.resize((width, height), Image.Resampling.LANCZOS)

    newImg.save(GetFullPath("temp.png"))  # 保存

    return GetFullPath("temp.png")
    # im_PIL.show() #显示


key_map = {
    "0": 48,
    "1": 49,
    "2": 50,
    "3": 51,
    "4": 52,
    "5": 53,
    "6": 54,
    "7": 55,
    "8": 56,
    "9": 57,
    'F1': 112,
    'F2': 113,
    'F3': 114,
    'F4': 115,
    'F5': 116,
    'F6': 117,
    'F7': 118,
    'F8': 119,
    'F9': 120,
    'F10': 121,
    'F11': 122,
    'F12': 123,
    'F13': 124,
    'F14': 125,
    'F15': 126,
    'F16': 127,
    "A": 65,
    "B": 66,
    "C": 67,
    "D": 68,
    "E": 69,
    "F": 70,
    "G": 71,
    "H": 72,
    "I": 73,
    "J": 74,
    "K": 75,
    "L": 76,
    "M": 77,
    "N": 78,
    "O": 79,
    "P": 80,
    "Q": 81,
    "R": 82,
    "S": 83,
    "T": 84,
    "U": 85,
    "V": 86,
    "W": 87,
    "X": 88,
    "Y": 89,
    "Z": 90,
    'BACKSPACE': 8,
    'TAB': 9,
    'TABLE': 9,
    'CLEAR': 12,
    'ENTER': 13,
    'SHIFT': 16,
    'CTRL': 17,
    'CONTROL': 17,
    'ALT': 18,
    'ALTER': 18,
    'PAUSE': 19,
    'BREAK': 19,
    'CAPSLK': 20,
    'CAPSLOCK': 20,
    'ESC': 27,
    'SPACE': 32,
    'SPACEBAR': 32,
    'PGUP': 33,
    'PAGEUP': 33,
    'PGDN': 34,
    'PAGEDOWN': 34,
    'END': 35,
    'HOME': 36,
    'LEFT': 37,
    'UP': 38,
    'RIGHT': 39,
    'DOWN': 40,
    'SELECT': 41,
    'PRTSC': 42,
    'PRINTSCREEN': 42,
    'SYSRQ': 42,
    'SYSTEMREQUEST': 42,
    'EXECUTE': 43,
    'SNAPSHOT': 44,
    'INSERT': 45,
    'DELETE': 46,
    'HELP': 47,
    'WIN': 91,
    'WINDOWS': 91,
    'NMLK': 144,
    'NUMLK': 144,
    'NUMLOCK': 144,
    'SCRLK': 145,
    '[': 219,
    ']': 221,
    '+': 107,
    '-': 109
}

SCROLL_KEYS_1 = 0
SCROLL_KEYS_2 = 1
SCROLL_200MS = 0.2
SCROLL_400MS = 0.4
SCROLL_600MS = 0.6
SCROLL_800MS = 0.8
DIRECTION_UP = 'UP'
DIRECTION_DOWN = 'DOWN'
DIRECTION_LEFT = 'LEFT'
DIRECTION_RIGHT = 'RIGHT'
scroll_keys_list = [
    {
        'UP': 'UP',
        'DOWN': 'DOWN',
        'LEFT': 'LEFT',
        'RIGHT': 'RIGHT',
    },
    {
        'UP': '8',
        'DOWN': '2',
        'LEFT': '4',
        'RIGHT': '6',
    },
]

zbmap = {
    '新月的悲叹': 'xinyue',
    '焰帝戒指': 'huojie',
    '忘哭之冠': 'wangkuzhiguan',
    '深渊之弓': 'shenyuanzhiging',
    '愤怒法杖': 'fennufazhang',
    '鹰神之煌剑': 'yingshenjian',
    '狮鹫羽饰': 'shijiuyushi',
    '恶魔法杖': 'emofazhang',
}


def GetWinPos():
    logger.info("")


def Click(x=None, y=None):
    try:
        global Subhwnd, lastY, lastX, rect, trueH, trueW
        if (x == None):
            x = lastX
            y = lastY
        else:
            lastX = x
            lastY = y

        tx = int(x * trueW / 960)
        ty = int(y * trueH / 540)
        # logger.info(trueH,trueW,"simPos:",x,y,"truePos:",tx,ty)
        positon = win32api.MAKELONG(int(tx), int(ty))
        win32api.SendMessage(Subhwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, positon)
        time.sleep(0.02)
        win32api.SendMessage(Subhwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, positon)
        time.sleep(0.1)
    except Exception as e:
        logger.info(f"fallback adb click:{e}")


def testKey():
    win32gui.PostMessage(Subhwnd, win32con.WM_KEYDOWN, 90, 0)
    win32gui.PostMessage(Subhwnd, win32con.WM_KEYUP, 90, 0)


# 抬起按键
def release_key(key_code):
    win32api.keybd_event(key_code, win32api.MapVirtualKey(key_code, 0), win32con.KEYEVENTF_KEYUP, 0)


# 按下按键
def press_key(key_code):
    win32api.keybd_event(key_code, win32api.MapVirtualKey(key_code, 0), 0, 0)


#  按一下按键
def press_and_release_key(key_code):
    press_key(key_code)
    release_key(key_code)


# endregion


# region 图片检查&点击事件
# 快速检测图片
def IsHasImg(targetImg, isClick=True, stopTime=4, offsetY=0, isRgb=False, match=minMatch):
    return WaitToClickImg(targetImg, isClick, True, stopTime, offsetY=offsetY, isRgb=isRgb, match=match)


# 等待图片出现,低频率检测
def WaitImgLongTime(targetImg):
    maxTryTime = 30 * 4  # 4分钟 最大等待上限
    longTimer = 0
    while (WaitToClickImg(targetImg, False, True) == False):
        time.sleep(2)
        longTimer = longTimer + 1
        if (longTimer > maxTryTime):
            return


# 返回图片坐标
def GetImgXY(targetImg, match=minMatch, isRgb=False):
    target_ImgPath = GetFullPath(targetImg)
    Screen_ImgPath = SavaShoot()
    logger.debug(target_ImgPath)
    imsrc = ac.imread(Screen_ImgPath)  # 原始图像
    imsch = ac.imread(target_ImgPath)  # 带查找的部分
    match_result = ac.find_template(imsrc, imsch, match, rgb=isRgb)

    logger.debug('match : %s %s' % (targetImg, match_result))

    if match_result != None:
        x, y = match_result['result']
        if (match_result['confidence'] < warnMatch):
            logger.debug("\033[1;33m %s %s \033[0m" % (targetImg, match_result['confidence']))

        global Subhwnd, lastY, lastX, trueH, trueW
        if (x == None):
            x = lastX
            y = lastY
        else:
            lastX = x
            lastY = y

        tx = int(x * trueW / 960)
        ty = int(y * trueH / 540)
        return tx, ty
    else:
        return 0, 0


# 查找图片
def WaitToClickImg(targetImg, isClick=True, isSkip=True, maxTry=12, autoExit=False, match=minMatch, isRgb=False, offsetY=0):
    # isClick:找到图片后是否点击
    # isSkip:查找失败后是否跳过
    # maxTry:查找失败重新尝试次数
    target_ImgPath = GetFullPath(targetImg)
    Screen_ImgPath = SavaShoot()
    logger.debug(target_ImgPath)
    imsrc = ac.imread(Screen_ImgPath)  # 原始图像
    imsch = ac.imread(target_ImgPath)  # 带查找的部分
    match_result = ac.find_template(imsrc, imsch, match, rgb=isRgb)

    logger.debug('match : %s %s' % (targetImg, match_result))
    global waitTime

    if match_result != None:
        # logger.info(match,minMatch,targetImg)
        # if(match > minMatch):
        # 	for	ma in match_result:
        # 		logger.info('confidence ',ma)
        # 	logger.info("Find Highist " ,len(match_result))

        x1, y1 = match_result['result']
        if (match_result['confidence'] < warnMatch):
            logger.debug("\033[1;33m %s %s \033[0m" % (targetImg, match_result['confidence']))
        waitTime = 0

        if (isClick):
            y1 = y1 + (offsetY * trueH / 540)
            time.sleep(0.1)
            logger.info("Click >> " + targetImg)
            Click(x1, y1)
            time.sleep(1)
        return True
    else:
        waitTime = waitTime + 1
        logger.debug(isSkip == False)
        if ((isSkip == False) | (waitTime < maxTry)):
            time.sleep(0.18)
            if (isSkip == False):
                time.sleep(3)
            if (waitTime < maxTry and autoExit):
                DoKeyDown(exitKey)
            return WaitToClickImg(targetImg, isClick, isSkip, maxTry, autoExit, match, isRgb)
        else:
            logger.info("Skip >> " + targetImg)
            return False


# 屏幕截图,并返回保存路径
def image_X():
    global curDir
    img = ImageGrab.grab()
    sp = os.path.join(curDir, "temp.png")
    img.save(sp)
    return sp


# 点到消失为止
def ClickUntilNul(path, offsetY=0, maxTry=20, isRgb=False, match=minMatch):
    WaitToClickImg(path, offsetY=offsetY, isRgb=isRgb, match=match)
    time.sleep(0.5)
    tryTime = 0
    while (IsHasImg(path, offsetY=offsetY, isRgb=isRgb, match=match)):
        if (tryTime > maxTry):
            break
        tryTime = tryTime + 1
        IsHasImg(path, offsetY=offsetY, isRgb=isRgb, match=match)


# #点击然后exit消失为止
# def ClickUntilNul2(path,exsitPath):
# 	WaitToClickImg(path)
# 	while(IsHasImg(exsitPath,False) == False):
# 		DoKeyDown(exitKey)
# 		ClickUntilNul2(path,exsitPath)
# 		break


# 点击
def pressKey(key):
    keyCode = key_map[key]
    win32gui.PostMessage(Subhwnd, win32con.WM_KEYDOWN, keyCode, 0)
    time.sleep(0.05)
    win32gui.PostMessage(Subhwnd, win32con.WM_KEYUP, keyCode, 0)


def scroll(num: int, direction: str, times: float):
    """使用雷电模拟器的控制视角按键实现滑动

    Args:
        num (int): 按键配置序号
        direction (str): 滑动方向
        times (float): 滑动时间
    """
    keyCode = key_map[scroll_keys_list[num][direction]]
    logger.info(keyCode)
    win32gui.PostMessage(Subhwnd, win32con.WM_KEYDOWN, keyCode, 0)
    time.sleep(times)
    win32gui.PostMessage(Subhwnd, win32con.WM_KEYUP, keyCode, 0)

    # """在坐标(x, y)滚动鼠标滚轮

    # Args:
    #     delta (int): 为正向上滚动，为负向下滚动
    #     x (int): 横坐标
    #     y (int): 纵坐标
    # """
    # wparam = delta << 16
    # p = POINT(x, y)
    # ClientToScreen(Subhwnd, byref(p))
    # lparam = p.y << 16 | p.x
    # main_rect = win32gui.GetWindowRect(Subhwnd)
    # win32api.SetCursorPos([main_rect[0] + x, main_rect[1] + y])
    # win32gui.SendMessage(Subhwnd, WM_MOUSEWHEEL, wparam, lparam)


def scroll_up(num: int, times: int):
    """使用传入序号的控制视角按键向上滚动鼠标滚轮

    Args:
        num (int): 按键配置序号
        times (float): 滑动时间
    """
    logger.info('向上滑动' + str(times) + 's')
    scroll(num, DIRECTION_DOWN, times)
    time.sleep(1)


def scroll_down(num: int, times: int):
    """使用传入序号的控制视角按键向下滚动鼠标滚轮

    Args:
        num (int): 按键配置序号
        times (float): 滑动时间
    """
    logger.info('向下滑动' + str(times) + 's')
    scroll(num, DIRECTION_UP, times)
    time.sleep(1)


def scroll_left(num: int, times: int):
    """使用传入序号的控制视角按键向左滚动鼠标滚轮

    Args:
        num (int): 按键配置序号
        times (float): 滑动时间
    """
    logger.info('向左滑动' + str(times) + 's')
    scroll(num, DIRECTION_RIGHT, times)
    time.sleep(1)


def scroll_right(num: int, times: int):
    """使用传入序号的控制视角按键向右滚动鼠标滚轮

    Args:
        num (int): 按键配置序号
        times (float): 滑动时间
    """
    logger.info('向右滑动' + str(times) + 's')
    scroll(num, DIRECTION_LEFT, times)
    time.sleep(1)


def DoKeyDown(key):
    pressKey(key)
    time.sleep(1)


def LongTimeCheck(im1, im2):
    isWaiting = True
    # True表示识别1图 False表示识别2图
    while (isWaiting):
        time.sleep(2)
        if (IsHasImg(im1, False)):
            logger.info('has ' + im1)
            return True
        if (IsHasImg(im2, False)):
            logger.info('has ' + im2)
            return False


# 快按钮事件
def FastKeyDown(_key):
    logger.info(_key)
    time.sleep(0.03)
    pressKey(_key)


global loopKey


def LoopKeyDown():
    time.sleep(2)
    while (True):
        if (loopKey == 'exit'):
            return
        FastKeyDown(loopKey)


def StartLoopKeyDown(key):
    logger.info("start loop " + key)
    global loopKey
    loopKey = key
    global t1
    t1 = threading.Thread(target=LoopKeyDown, args=())
    t1.start()


def StopLoopKeyDown():
    global loopKey
    loopKey = 'exit'
    logger.info('StopLoopKeyDown')


# endregion


# region 界面跳转
def ToFightPage():
    ToHomePage()
    WaitToClickImg("img/main/fight.png")
    DoKeyDown(exitKey)
    logger.info('进入冒险页面')


def ToHomePage():
    while not IsHasImg("img/main/tuichu.png", False):
        logger.info('回到主页')
        DoKeyDown(endKey)
    DoKeyDown(exitKey)

    # if not IsHasImg("img/main/home2.png", False) and not IsHasImg("img/main/ghHome.png", False):
    #     logger.info('回到主页')
    #     if (WaitToClickImg("img/main/home.png", True, True, 5) == False):
    #         DoKeyDown(exitKey)
    #         DoKeyDown(exitKey)
    #         logging.warning('重新回到主页')
    #         ToHomePage()
    logger.info('已回到主页')
    time.sleep(1)


def ToHangHuiPage():
    ToHomePage()
    WaitToClickImg('img/other/hanghui.png')
    time.sleep(2)
    if (IsHasImg("img/other/members.png") == False):
        DoKeyDown(exitKey)
        DoKeyDown(exitKey)
        logger.info('重新进入行会')
        ToHangHuiPage()
    logger.info('已进入行会')
    time.sleep(1)


def ToShopPage():
    WaitToClickImg("img/shop/shop1.png", True, True, 5)
    time.sleep(1)


# endregion


# 选择队伍
def SelectParty(x, y):
    time.sleep(1)
    DoKeyDown(partyKey)
    time.sleep(0.4)
    x = x - 1
    y = y - 1
    DoKeyDown(groupKeys[x])
    time.sleep(0.1)
    DoKeyDown(duiKeys[y])
    time.sleep(0.1)


def StartJJC():
    logger.info("开始竞技场任务")
    ToFightPage()
    WaitToClickImg("img/jjc/jjc.png")
    # WaitToClickImg("img/jjc/get.png")
    time.sleep(1)
    DoKeyDown(exitKey)
    WaitToClickImg("img/jjc/jjcTop.png", False)
    DoKeyDown(exitKey)
    DoKeyDown(exitKey)
    logger.info("领工资")
    DoKeyDown(huoDongHBossKey)
    DoKeyDown(exitKey)
    logger.info("战斗开始")
    DoKeyDown(listSelectKeys[0])
    time.sleep(1)
    if IsHasImg("img/jjc/lengque.png", False) or IsHasImg("img/jjc/tiaozhancishu.png", False):
        logger.info("jjc冷却中或已达今日上限。。。")
        ToHomePage()
        return
    DoKeyDown(playerKey)
    DoKeyDown(playerKey)
    time.sleep(7)
    logger.info("sleep...")
    if (WaitToClickImg('img/jjc/skip.png', maxTry=25) == False):
        WaitToClickImg('img/jjc/skip.png', maxTry=25)
    Click()
    time.sleep(2)
    LongTimeCheck("img/dxc/win.png", "img/jjc/lose.png")
    time.sleep(1.5)
    DoKeyDown(nextKey)
    time.sleep(1.5)
    DoKeyDown(nextKey)
    ToHomePage()


def StartPJJC():
    logger.info("开始公主竞技场任务")
    ToFightPage()
    WaitToClickImg("img/jjc/pjjc.png")
    # WaitToClickImg("img/jjc/get.png")
    time.sleep(1)
    DoKeyDown(exitKey)
    WaitToClickImg("img/jjc/pjjcTop.png", False)
    DoKeyDown(exitKey)  # 关掉提示框
    logger.info("领工资")
    DoKeyDown(huoDongHBossKey)
    DoKeyDown(exitKey)
    time.sleep(1)
    logger.info("战斗开始")
    DoKeyDown(listSelectKeys[0])  # 选择
    time.sleep(1.5)
    if IsHasImg("img/jjc/lengque.png", False):
        logger.info("pjjc冷却中。。。")
        ToHomePage()
        return
    DoKeyDown(playerKey)
    DoKeyDown(playerKey)
    DoKeyDown(playerKey)
    DoKeyDown(playerKey)
    logger.info("sleep for 5s...")
    time.sleep(6)
    if (WaitToClickImg('img/jjc/skip.png', maxTry=20) == False):
        WaitToClickImg('img/jjc/skip.png', maxTry=20)
    Click()
    Click()
    time.sleep(1.5)
    LongTimeCheck("img/jjc/pjjcEnd.png", "img/jjc/pjjcEnd.png")
    time.sleep(2.5)
    DoKeyDown(nextKey)
    time.sleep(2)
    DoKeyDown(nextKey)
    ToHomePage()


def StartTanSuo():
    logger.info("===探索===")
    ToFightPage()
    time.sleep(0.5)
    WaitToClickImg("img/tansuo/tansuo.png")
    time.sleep(0.5)
    WaitToClickImg("img/tansuo/mana.png")
    WaitToClickImg("img/tansuo/topMana.png", False)
    DoKeyDown(listSelectKeys[0])
    if (IsHasImg("img/tansuo/topMana.png", False)):
        DoKeyDown(listSelectKeys[0])
    time.sleep(0.5)
    WaitToClickImg("img/tansuo/start.png")
    WaitToClickImg("img/main/sure.png")
    WaitToClickImg("img/tansuo/return.png")
    time.sleep(0.5)
    DoKeyDown(exitKey)
    logger.info("===exit===")
    DoKeyDown(exitKey)
    # exp
    if (IsHasImg("img/tansuo/topExp.png", False) == False):
        ToFightPage()
        time.sleep(0.5)
        WaitToClickImg("img/tansuo/tansuo.png")
        time.sleep(0.5)
        WaitToClickImg("img/tansuo/exp.png")

    WaitToClickImg("img/tansuo/topExp.png", False)
    DoKeyDown(listSelectKeys[0])
    if (IsHasImg("img/tansuo/topExp.png", False)):
        DoKeyDown(listSelectKeys[0])
    time.sleep(0.5)
    WaitToClickImg("img/tansuo/start.png")
    WaitToClickImg("img/main/sure.png")
    WaitToClickImg("img/tansuo/return.png")
    time.sleep(0.5)
    DoKeyDown(exitKey)
    DoKeyDown(exitKey)
    time.sleep(1.5)


def StartTakeAll():
    time.sleep(2)
    ToHomePage()
    WaitToClickImg("img/task/task.png")
    WaitToClickImg("img/task/takeAll.png")
    WaitToClickImg("img/task/close.png")


def TakeGift():
    ToHomePage()
    WaitToClickImg("img/task/gift.png")
    WaitToClickImg("img/task/takeAll.png")
    WaitToClickImg("img/task/sure.png", match=hightMatch)
    ExitSaoDang()
    ToHomePage()


# region 地下城
StartBossIndex = 0
lastGroup = ""


def StartDxc(index=1):
    logger.info("===地下城==")
    global nextDxcLevel
    nextDxcLevel = index
    ToFightPage()
    # 进入地下城
    EnterDxc()
    if not IsHasImg(dxcDir + "/quyu.png", False):
        logger.info('地下城今日已完成')
        ToHomePage()
        return
    # 扫荡
    if isSkipDxc:
        time.sleep(1)
        if IsHasImg(dxcDir + "/skip.png"):
            time.sleep(2)
            WaitToClickImg("img/main/sure.png")
            logger.info('地下城扫荡完成')
            ToHomePage()
            return

    IsHasImg("img/main/sure.png")
    time.sleep(2)
    if (nextDxcLevel <= 1):
        logger.info('wait box1...')
        WaitToClickImg(dxcDir + "/box1.png", False)
        logger.info('found box1 => start')
    if (nextDxcLevel <= 0):
        nextDxcLevel = 1

    if (nextDxcLevel <= 1):
        DxcBoxFight(1)
        time.sleep(4)
        CheckAuto()
        DxcBoxFightWait()  # 1战中
    if (nextDxcLevel <= 2):
        DxcBoxFight(2)
        DxcBoxFightWait()  # 2
    if (nextDxcLevel <= 3):
        DxcBoxFight(3)
        DxcBoxFightWait()  # 3
    if (nextDxcLevel <= 4):
        DxcBoxFight(4)
        DxcBoxFightWait()  # 4

    ToHomePage()


def CheckAuto():
    if (WaitToClickImg('img/main/auto2.png', True, match=0.93, isRgb=True, maxTry=40)):
        logger.info('检测到自动未开启, 开启自动')
        WaitToClickImg('img/main/auto2.png', True, match=0.93, isRgb=True, maxTry=6)


# 进入地下城界面
def EnterDxc():
    WaitToClickImg("img/main/dxc.png")
    time.sleep(1.5)
    scroll_right(SCROLL_KEYS_1, SCROLL_400MS)
    WaitToClickImg(dxcDir + "/ex.png")
    time.sleep(1)
    # IsHasImg("img/main/sure.png")
    # time.sleep(2)


def GetBossLoopKey(level):
    rawValue = dxcBossLoopRole
    values = rawValue.split(",")
    listLen = len(values)
    if (rawValue == ""):
        return '0'
    if (listLen > level):
        return values[level]
    return '0'


def GetGroupInfo(level):
    rawValue = dxcGroupDaoZhong
    values = rawValue.split(",")
    listLen = len(values)
    if (rawValue == ""):
        return "5-1"
    if (listLen >= level):
        return values[level - 1]
    else:
        return values[listLen - 1]


def CheckSelectGroup(level, isBoss):
    global lastGroup
    curGroup = GetGroupInfo(level, isBoss)
    # 如果上一个队伍和下一个队伍相同 则什么都不做
    if (lastGroup != curGroup):
        time.sleep(1)
        lastGroup = curGroup
        infos = curGroup.split("-")
        SelectParty(int(infos[0]), int(infos[1]))
        time.sleep(1)


def DxcBoxFight(level):
    global nextDxcLevel
    nextDxcLevel = level + 1
    # 自动取消关闭奖励界面
    if (level == 1):
        ClickUntilNul(dxcDir + "/box1.png")
    elif (level == 2):
        ClickUntilNul(dxcDir + "/box2.png")
    elif (level == 3):
        ClickUntilNul(dxcDir + "/box3.png")
    elif (level == 4):
        ClickUntilNul(dxcDir + "/box4.png")

    time.sleep(1)
    DoKeyDown(playerKey)
    time.sleep(1.5)
    CheckSelectGroup(level, False)

    DoKeyDown(playerKey)


def DxcBoxFightWait():
    time.sleep(2.5)
    WaitImgLongTime(dxcDir + "/win.png")
    time.sleep(2)
    DoKeyDown(nextKey)  # 返回
    DoKeyDown(nextKey)  # 返回
    time.sleep(3)
    DoKeyDown(exitKey)
    time.sleep(0.5)
    DoKeyDown(exitKey)  # 跳过宝箱
    time.sleep(0.5)
    DoKeyDown(exitKey)
    time.sleep(0.5)


def StartBoss():

    global StartBossIndex  # 0开始计数
    values = dxcGroupBoss.split(",")
    listLen = len(values)
    if (StartBossIndex >= listLen):  # 0开始计数
        logger.info("===Boss 挑战 失败==='")
        return

    logger.info('===StartBoss===')
    ClickUntilNul(dxcDir + "/box5.png")
    time.sleep(1)
    DoKeyDown(playerKey)

    time.sleep(0.4)

    CheckSelectGroup(StartBossIndex + 1, True)
    time.sleep(0.4)

    DoKeyDown(playerKey)
    time.sleep(0.4)
    DoKeyDown(playerKey)

    roleLoop = GetBossLoopKey(StartBossIndex)
    logger.info('roleLoop ' + roleLoop)
    if (roleLoop != '0'):
        StartLoopKeyDown(roleLoop)

    StartBossIndex = StartBossIndex + 1
    WaitBossFight()


def WaitBossFight():
    ## TODO
    if LongTimeCheck('img/dxc/win.png', dxcDir + '/lose.png'):
        # win
        logger.info('战斗胜利')
        StopLoopKeyDown()
        time.sleep(5)
        DoKeyDown(nextKey)
        time.sleep(5)
        DoKeyDown(nextKey)
        time.sleep(5)
        DoKeyDown(exitKey)
        time.sleep(0.5)
        DoKeyDown(exitKey)
        time.sleep(0.5)
        DoKeyDown(exitKey)
        logger.info('回到主页')
    else:
        # lose
        StopLoopKeyDown()
        time.sleep(2)
        DoKeyDown(nextKey)
        DoKeyDown(nextKey)
        time.sleep(1)
        StartBoss()


# 等待必胜战斗
def WaitAlwaysWinBossFight():
    LongTimeCheck('img/main/next.png', dxcDir + '/lose.png')
    # win
    logger.info('战斗胜利')
    StopLoopKeyDown()
    time.sleep(2.5)
    DoKeyDown(nextKey)
    time.sleep(3)
    DoKeyDown(nextKey)
    time.sleep(3)
    DoKeyDown(exitKey)
    time.sleep(0.5)
    DoKeyDown(exitKey)
    time.sleep(0.5)
    DoKeyDown(exitKey)
    ToHomePage()
    logger.info('回到主页')


def StartNormalFight():
    # TODO 开启自动 倍速
    logger.info('战斗开始')
    WaitToClickImg('img/main/tiaozhan.png')
    time.sleep(1)
    WaitToClickImg('img/main/zhandoukaishi.png')
    WaitBossFight()


# endregion
def BuyExp():
    # TODO 石头 界面选择 次数限制
    logger.info('买经验和石头, 购买数量' + str(buyExpNum))
    ToHomePage()
    ToShopPage()
    WaitToClickImg('img/shop/shopTop.png', False)
    if IsHasImg('img/shop/shopTop.png', False):
        DoKeyDown(groupKeys[1])
    else:
        BuyExp()

    for i in range(buyExpNum):
        selectItem = 'img/shop/allitem.png'
        if isExp:
            selectItem = 'img/shop/expitem.png'
        if isStone:
            selectItem = 'img/shop/stoneitem.png'
        if isExp and isStone:
            selectItem = 'img/shop/allitem.png'

        logger.info('购买经验, 当前次数: ' + str(i + 1))
        if i == 0:
            WaitToClickImg(selectItem)
        WaitToClickImg('img/shop/selectall.png')

        WaitToClickImg('img/shop/buyBtn.png')
        WaitToClickImg('img/shop/buyTitle.png', False)
        WaitToClickImg('img/main/sure.png')
        time.sleep(0.5)
        WaitToClickImg('img/main/sure.png')
        if i + 1 != buyExpNum:
            WaitToClickImg('img/shop/update.png')
            WaitToClickImg('img/main/sure.png')

    ToHomePage()


def NiuDan():
    # TODO 按键位置
    WaitToClickImg('img/main/niuDan.png')
    time.sleep(2)
    DoKeyDown(exitKey)
    DoKeyDown(exitKey)
    DoKeyDown(partyKey)
    DoKeyDown(partyKey)

    if (IsHasImg('img/other/niu1.png')):
        WaitToClickImg('img/main/sure.png')
    ToHomePage()


def EnterDiaoCha():
    ToFightPage()
    WaitToClickImg('img/main/diaoCha.png')


def SaoDang(_time=4):
    WaitToClickImg('img/tansuo/plus.png')
    for i in range(_time):
        time.sleep(0.5)
        Click()

    WaitToClickImg('img/tansuo/start.png')
    if (IsHasImg('img/main/huifu.png', False)):
        DoKeyDown(exitKey)
        DoKeyDown(exitKey)
        return
    WaitToClickImg("img/main/sure.png")
    WaitToClickImg("img/main/skip.png")
    DoKeyDown(exitKey)
    time.sleep(1)


def ExitSaoDang():
    DoKeyDown(exitKey)
    DoKeyDown(exitKey)


def Xqb():
    if (WaitToClickImg('img/tansuo/xqbEnter.png') == False):
        ExitSaoDang()
        WaitToClickImg('img/tansuo/xqbEnter.png')

    for i in range(2):
        time.sleep(0.5)
        WaitToClickImg('img/tansuo/xqbTop.png', False)
        DoKeyDown(listSelectKeys[i])
        SaoDang()
        ExitSaoDang()
        DoKeyDown(exitKey)
        DoKeyDown(exitKey)


def xinSui():
    if (WaitToClickImg('img/tansuo/xinSuiEnter.png') == False):
        ExitSaoDang()
        WaitToClickImg('img/tansuo/xinSuiEnter.png')

    for i in range(3):
        time.sleep(0.5)
        WaitToClickImg('img/tansuo/xinSuiTop.png', False)
        DoKeyDown(listSelectKeys[i])
        SaoDang()
        ExitSaoDang()
        DoKeyDown(exitKey)
        DoKeyDown(exitKey)
    ToHomePage()


def SendZb():
    ToHomePage()
    WaitToClickImg('img/other/hanghui.png')
    time.sleep(0.4)
    WaitToClickImg('img/other/hhDown.png')
    time.sleep(0.2)
    for i in range(2):
        if (WaitToClickImg('img/other/sendBtn.png', True, match=0.93, isRgb=True)):
            WaitToClickImg('img/other/sendMax.png', True, True, 7, False, 0.85)
            WaitToClickImg('img/main/sure.png')
            time.sleep(0.2)
            DoKeyDown(exitKey)
            DoKeyDown(exitKey)


def GetZBPath(name):
    return os.path.join('img\\other\\zhuangbei\\', str(name) + '.png')


isRetryNeedZb = False


def needSeedZbStart():
    global isRetryNeedZb
    logger.info('装备乞讨任务')
    if (isRetryNeedZb == False):
        ToHomePage()
        WaitToClickImg('img/other/hanghui.png')
    time.sleep(2)
    # WaitToClickImg('img/other/needSend.png')
    DoKeyDown(huodongKey)
    time.sleep(2)

    if (IsHasImg('img/other/needSend2.png', False) == True):
        needSeedZb()
    else:
        logger.info("确认上期乞讨")
        WaitToClickImg('img/main/sure.png')
        time.sleep(1)
        # WaitToClickImg('img/other/needSend.png')
        DoKeyDown(huodongKey)
        time.sleep(1)
        if (IsHasImg('img/main/sure.png', False) == True):
            logger.info("上期乞讨尚未结束")
            DoKeyDown(exitKey)
            DoKeyDown(exitKey)
            time.sleep(0.5)
            ToHomePage()
        else:
            needSeedZb()


def needSeedZb():
    logger.info("装备乞讨")
    if (WaitToClickImg(GetZBPath(zbmap[needZbName]), False, maxTry=5, match=0.7) == False):
        logger.info("找不到装备，反转排序")
        DoKeyDown(partyKey)
        time.sleep(1)
    if (WaitToClickImg(GetZBPath(zbmap[needZbName]), maxTry=5, match=0.7)):
        WaitToClickImg('img/other/needSend2.png')
        WaitToClickImg('img/main/sure.png')
        WaitToClickImg('img/main/sure.png')
    else:
        DoKeyDown(exitKey)
        DoKeyDown(exitKey)


def ghHomeTake():
    WaitToClickImg('img/main/ghHome.png')
    time.sleep(1)
    WaitToClickImg('img/main/ghHome_take.png')
    DoKeyDown(exitKey)
    WaitToClickImg('img/task/close.png')
    DoKeyDown(exitKey)


tuichuMaxTry = 0


def ClickPlayer():
    global playerName
    if (playerName == ""):
        logger.info("玩家角色 为空!")
        playerName = "player0"

    while (WaitToClickImg('img/main/' + playerName + '.png', isClick=False, isRgb=True, match=0.6, maxTry=8) == NULL):
        ExitSaoDang()
        logger.info("No player")
    ClickUntilNul('img/main/' + playerName + '.png', offsetY=50, maxTry=8, isRgb=True, match=0.6)


def ClickPlayer_Or_Next():
    global playerName
    if (playerName == ""):
        logger.info("玩家角色 为空!")
        playerName = "player0"

    while (WaitToClickImg('img/main/' + playerName + '.png', isClick=False, isRgb=True, match=0.6, maxTry=8) == NULL):
        if (IsHasImg('img/main/next2.png', False)):
            FinghtNext()
        ExitSaoDang()
        logger.info("No player")
    ClickUntilNul('img/main/' + playerName + '.png', offsetY=50, maxTry=8, isRgb=True, match=0.6)


def FinghtNext():
    WaitImgLongTime("img/main/next2.png")
    DoKeyDown(nextKey)
    DoKeyDown(nextKey)
    time.sleep(2)
    if (WaitToClickImg("img/main/next2.png") == False):
        ExitSaoDang()
        WaitToClickImg("img/main/next2.png")


IsFirst = True


def OnTuitu():

    global IsFirst
    if (IsFirst):
        ClickPlayer_Or_Next()
        IsFirst = False
    else:
        ClickPlayer()

    if (WaitToClickImg('img/tansuo/start2.png', match=hightMatch, isRgb=True, maxTry=16, isClick=False)):
        logger.info("检测到不能扫荡 -> 新关卡")
        time.sleep(1)

        DoKeyDown(playerKey)
        DoKeyDown(playerKey)
        time.sleep(0.8)
        DoKeyDown(playerKey)
        DoKeyDown(playerKey)
        DoKeyDown(playerKey)

        logger.info("sleep 10")
        time.sleep(10)
        WaitImgLongTime("img/main/next2.png")

        DoKeyDown(nextKey)
        DoKeyDown(nextKey)
        time.sleep(2)
        if (WaitToClickImg("img/main/next2.png") == False):
            ExitSaoDang()
            WaitToClickImg("img/main/next2.png")
        DoKeyDown(nextKey)
        OnTuitu()
    else:
        if (WaitToClickImg('img/tansuo/start.png', match=hightMatch, isRgb=True, maxTry=8, isClick=False) == False):
            ExitSaoDang()
            OnTuitu()
            return
        else:
            logger.info("已经全部通关...")
            ExitSaoDang()


def OnAutoTaskStart():
    logger.info("AutoTask")
    OnAutoTask()


menuNofindTime = 0


def OnAutoTask():
    logger.info("AutoTask")
    global menuNofindTime

    hasMenu = False

    # 菜单存在时
    if (WaitToClickImg('img/task/menu.png')):
        hasMenu = True
        menuNofindTime = 0
        # if(IsHasImg('img/task/skip.png') == False):
        # IsHasImg('img/task/menu.png')
        if (IsHasImg('img/task/skip.png')):
            # 蓝色按钮
            WaitToClickImg('img/task/skipBtn.png')
        else:
            # 出现选项时
            if (IsHasImg("img/task/menu_black.png", False, isRgb=True)):
                ClickCenter()
                OnAutoTask()
                return
        time.sleep(0.6)

    # 没有菜单
    if ((1 - hasMenu) or (IsHasImg('img/task/menu.png', isClick=False) == False)):
        # 需要区分是视频还是 主页
        if (IsHasImg('img/task/close.png', stopTime=6) == False and IsHasImg('img/task/noSound.png') == False):
            DoKeyDown(exitKey)
            time.sleep(0.6)
            menuNofindTime = menuNofindTime + 1

        IsHasImg('img/task/skipBtn.png')
        IsHasImg('img/task/noSound.png')
    else:
        menuNofindTime = 0

    if (menuNofindTime > 1):
        if ((1 - IsHasImg('img/task/skipBtn.png'))):
            if (IsHasImg("img/main/fight.png", False)):
                logger.info("任务结束")
                return
            else:
                menuNofindTime = 0
        else:
            menuNofindTime = 0
    logger.info("=====Again======")
    OnAutoTask()


# 跳过对话
# def SkipDuiHua():


def OnHouDongHard():
    logger.info('开始剧情活动')
    ToFightPage()
    WaitToClickImg('img/main/dxc.png', False)
    # DoKeyDown(huodongKey)
    WaitToClickImg('img/huodong/jqhd.png')
    DoKeyDown(exitKey)
    DoKeyDown(exitKey)

    # 跳过剧情
    while not IsHasImg('img/huodong/baoxiang.png', False) and not IsHasImg('img/huodong/hard1.png', False) and not IsHasImg('img/huodong/hard2.png', False):
        logger.info("跳过剧情")
        DoKeyDown(exitKey)

    if IsHasImg('img/huodong/baoxiang.png', False):
        logger.info("打开活动困难关卡")
        DoKeyDown(groupKeys[3])
        DoKeyDown(partyKey)

    # ClickPlayer()
    logger.info('刷剧情活动关卡' + huoDongHard)
    if huoDongHard:
        beats = list(huoDongHard)
        WaitToClickImg('img/huodong/jqhd1-5.png')
        for i in range(5):
            time.sleep(1)
            if str(5 - i) not in beats:
                logger.info('跳过当前关卡')
                MoveToLeft()
                continue
            if not IsHasImg('img/main/tiaozhan.png', False):
                logger.info('当前关卡已经打过了')
                MoveToLeft()
                continue
            SaoDang(2)
        DoKeyDown(exitKey)
    else:
        logger.info('必须输入剧情活动关卡')

    # vhboss
    time.sleep(1)
    if (isVHBoss):
        # TODO 缺票
        DoKeyDown(huoDongVHBossKey)
        time.sleep(0.5)
        if IsHasImg('img/main/tiaozhan.png', False):
            logger.info("VH战斗")
            StartNormalFight()
        else:
            logger.info("VH已经打过了")
        logger.info("VH结束")
    ExitSaoDang()

    # 领奖励
    if IsHasImg('img/task/task.png'):
        logger.info('领活动奖励')
        time.sleep(2)
        DoKeyDown(huoDongJiangLiKeys[0])
        WaitToClickImg("img/task/takeAll.png")
        WaitToClickImg("img/task/close.png")
        DoKeyDown(exitKey)
        DoKeyDown(huoDongJiangLiKeys[1])
        WaitToClickImg("img/task/takeAll.png")
        WaitToClickImg("img/task/close.png")
        DoKeyDown(exitKey)
    ToHomePage()


def MoveToLeft():
    DoKeyDown('C')


def UseAllPower():
    logger.info('OnHouDongHard')
    ToFightPage()
    WaitToClickImg('img/main/zhuXian.png', True)

    ClickPlayer()

    i = 0
    isSaodang = True
    while (WaitToClickImg('img/tansuo/start2.png', match=hightMatch, isRgb=True, maxTry=6, isClick=False)):
        MoveToLeft()
        i = i + 1
        if (i > 3):
            isSaodang = False
            break

    if (isSaodang):
        SaoDang(60)
        ExitSaoDang()
    ExitSaoDang()


def DianZan():
    ToHangHuiPage()
    WaitToClickImg('img/other/members.png')
    time.sleep(2)

    logger.info("开始点赞任务")
    if (IsHasImg('img/other/dianzan.png', False) == False):
        logger.info("已经点过赞了")
    else:
        # TODO 选人
        logger.info("开始点赞")
        WaitToClickImg('img/other/dianzan.png')
        time.sleep(2)
    logger.info("点赞完成")
    ToHomePage()


# 日常任务
def DailyTasks():
    if isExp or isStone:
        BuyExp()
    if (isNiuDan):
        NiuDan()
    if (isTansuo):
        StartTanSuo()
    if (isJJC):
        StartJJC()
        StartPJJC()
    if (isDxc):
        StartDxc()
    if (isHomeTake):
        ghHomeTake()
        StartTakeAll()

    if (isXQB):
        EnterDiaoCha()
        Xqb()
    if (isXinSui):
        EnterDiaoCha()
        xinSui()
    if (isSend):
        SendZb()
    if (isNeedSeed):
        needSeedZbStart()
    if (isDianZan):
        DianZan()
    if (isHouDongHard):
        OnHouDongHard()
    if (isUseAllPower):
        UseAllPower()
        StartTakeAll()
    if (isTuitu):
        OnTuitu()
    if (isHomeTake):
        TakeGift()
    if (isAutoTask):
        OnAutoTask()


def CloseMoniqi():
    logger.info("3 秒后关闭模拟器")
    time.sleep(3)
    win32api.ShellExecute(0, 'open', GetFullPath('CloseLeiDian.cmd'), '', '', 1)


def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def ClickCenter():
    logger.info("Center")
    Click(x=width / 2, y=height * 0.55)
    Click(x=width / 2, y=height * 0.53)
    Click(x=width / 2, y=height * 0.50)
    Click(x=width / 2, y=height * 0.45)
    Click(x=width / 2, y=height * 0.43)
    Click(x=width / 2, y=height * 0.40)


def WaitStart():
    logger.info('=== WaitStart ===')
    while (IsHasImg("img/main/fight.png", False, stopTime=3) == False):
        DoKeyDown(exitKey)
        time.sleep(2)
        DoKeyDown(exitKey)
        time.sleep(3)
        # 更新
        if (IsHasImg("img/main/sure.png", True)):
            Click()
            time.sleep(10)
            logger.info('=== Update sleep 10 ===')
        # 跳过生日
        if (IsHasImg("img/main/skipIco.png", True)):
            Click()
            time.sleep(2)
            ClickCenter()

        if (IsHasImg("img/task/menu.png", True)):
            if (IsHasImg("img/task/skip.png", True)):
                WaitToClickImg("img/main/sure.png", True)
            else:
                if (IsHasImg("img/task/menu_black.png", False, isRgb=True)):
                    ClickCenter()
        # if(IsHasImg("img/other/brithDay.png")):

        if (IsHasImg("img/main/home.png", stopTime=3)):
            logger.info("find home")

    DoKeyDown(exitKey)
    DoKeyDown(exitKey)
    while (IsHasImg("img/main/fight.png", False) == False):
        DoKeyDown(exitKey)
        DoKeyDown(exitKey)
    time.sleep(1)
    ToHomePage()


# 按下Esc 停止


def CheckEnd(_key):
    while (True):
        keyboard.wait(_key)
        logger.info(_key)
        os._exit(0)


# 1-5是编组位置 6 是队伍
# num1-3 队伍位置
partyKey = 'Y'
exitKey = 'Z'
huodongKey = 'X'
playerKey = 'P'  # p是挑战位置
nextKey = 'L'  # n 是下一步
endKey = 'ESC'
# roleKey 123
listSelectKeys = ['I', 'J', 'N']
roleKeys = ['1', '2', '3', '4', '5']
groupKeys = ['Q', 'W', 'E', 'R', 'T']
duiKeys = ['U', 'H', 'B']
huoDongJiangLiKeys = ['S', 'D']
huoDongHBossKey = 'O'
huoDongVHBossKey = 'J'

StartRunName = "启动模拟器并运行"
RunName = "运行"


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


def GetIntConfig(key):
    try:
        return int(cfg.get(MainSettingKey, key))
    except:
        return 0


isRunAndStart = False

StartRunName = "启动模拟器并运行"
RunName = "运行"

isJJCKey = 'isJJC'
isTansuoKey = 'isTansuo'
isDxcKey = 'isDxc'
isSkipDxcKey = 'isSkipDxc'
dxcGroupDaoZhongKey = 'DxcGroupDaoZhong'
isExpKey = 'isExp'
isStoneKey = 'isStone'
isNiuDanKey = 'isNiuDan'
LeiDianDirKey = 'LeiDianDir'
isRunAndStartKey = 'isRunAndStart'
isAutoCloseKey = "isAutoClose"
isTuituKey = 'isTuituKey'
isFor64Key = 'isFor64'
isAutoTaskKey = 'isAutoTask'

# newKey
isXQBKey = 'isXQB'
isXinSuiKey = 'isXinSui'
isSendKey = 'isSend'

isNeedSeedKey = 'isNeedSeed'

isHomeTakeKey = 'isHomeTake'
isHouDongHardKey = 'isHouDongHard'
huoDongHardKeys = 'huoDongHard'
isUseAllPowerKey = 'isUseAllPower'
needZbNameKey = 'needZbName'
playerNameKey = 'playerName'

isBuyMoreExpKey = 'isBuyMoreExp'
isDianZanKey = 'isDianZan'
isVHBossKey = 'isVHBoss'

isBuyMoreExp = GetBoolConfig(isBuyMoreExpKey)
isJJC = GetBoolConfig(isJJCKey)
isTansuo = GetBoolConfig(isTansuoKey)
isDxc = GetBoolConfig(isDxcKey)
isSkipDxc = GetBoolConfig(isSkipDxcKey)
dxcGroupDaoZhong = GetStrConfig(dxcGroupDaoZhongKey)
isExp = GetBoolConfig(isExpKey)
isStone = GetBoolConfig(isStoneKey)
buyExpNum = GetIntConfig(buyExpNumKey)
isNiuDan = GetBoolConfig(isNiuDanKey)
LeiDianDir = cfg.get('MainSetting', LeiDianDirKey)

isXinSui = GetBoolConfig(isXinSuiKey)
isXQB = GetBoolConfig(isXQBKey)
isSend = GetBoolConfig(isSendKey)
isNeedSeed = GetBoolConfig(isNeedSeedKey)

isRunAndStart = GetBoolConfig(isRunAndStartKey)
isAutoClose = GetBoolConfig(isAutoCloseKey)
isTuitu = GetBoolConfig(isTuituKey)
isFor64 = GetBoolConfig(isFor64Key)
isAutoTask = GetBoolConfig(isAutoTaskKey)
isHomeTake = GetBoolConfig(isHomeTakeKey)
isHouDongHard = GetBoolConfig(isHouDongHardKey)
huoDongHard = GetStrConfig(huoDongHardKeys)
isVHBoss = GetBoolConfig(isVHBossKey)
isUseAllPower = GetBoolConfig(isUseAllPowerKey)
isDianZan = GetBoolConfig(isDianZanKey)
needZbName = GetStrConfig(needZbNameKey)
playerName = GetStrConfig(playerNameKey)

dxcBoss = GetStrConfig(dxcDropKey)
dxcDir = "img/dxc"

# endregion


def test():
    time.sleep(1)
    for i in range(100):
        time.sleep(0.5)
        testWin(i, i)

    logger.info("testend")
    time.sleep(40)
    return


def testWin(x, y):
    ret = win32gui.GetWindowRect(Subhwnd)
    ret2 = win32gui.GetClientRect(Subhwnd)
    height = ret[3] - ret[1]
    width = ret[2] - ret[0]
    tx = int(x * width / 960)
    ty = int(y * height / 540)
    logger.info(str(ret) + ' ' + str(ret2))
    logger.info(str(height) + str(width) + " oldPos:" + x + y + " truePos:" + str(tx) + str(ty))

    return


def RunAutoPcr():
    # 按下Esc键停止
    global t0
    global t1
    t0 = threading.Thread(target=CheckEnd, args=(endKey, ))
    t0.start()
    WaitWin32Start()
    # test()
    time.sleep(0.5)
    if (isRunAndStart):
        logger.info('Wait Start... ' + str(moniqTime) + "s")
        time.sleep(moniqTime)
        WaitStart()
    else:
        time.sleep(2)

    logger.info('=== Start ===')
    logger.info('\n=== 按Exc退出程序 ===\n')

    # 日常
    # OnAutoTask()
    DailyTasks()
    # tuichu()
    logger.info('=== end ===')

    if (isAutoClose):
        CloseMoniqi()

    time.sleep(2)
    os._exit(0)


if __name__ == '__main__':
    RunAutoPcr()
