## 公主连结自动化任务 

git: https://github.com/mackerel-12138/AutoPcr

fork自 https://github.com/smartgrass/AutoPcr

b站: https://www.bilibili.com/video/BV1xT4y1U75y

安装视频教程: https://share.weiyun.com/o80ZgPr0

<img src="https://github.com/smartgrass/AutoPcr/blob/main/png/Top.png" width= "500"/>

# 更新保留配置

config.ini是配置文件, 如果想保留配置, 可以在更新代码后, 把这个文件放回原位
# 小更新

买多次购买经验药

# 更新5.6 可挂后台版本

自动推图, 自动剧情 (说明见 文件夹 运行说明/其他说明)

跳过启动时生日

使用win32gui代替鼠标点击, 运行时可挂后台,但不能最小化

如果小号启动失败 ,则需要检查模拟器名称是否为"雷电模拟器-1"

# 更新5.0绿龙自动刀版本(仅限Windows) 

功能渐渐花里胡哨了起来...

<img src="https://github.com/smartgrass/AutoPcr/blob/main/png/GUIWindow.png" width= "500"/>

运行配置见'运行说明'文件夹

步骤: 

1. ~~安装py, ```\AutoPcr_py\运行说明\python安装包\python-3.11.0-amd64.exe```~~

2. ~~安装py第三方库: 运行 SetupPip.cmd (管理员~~

3. ~~设置管理员权限 : (把python.exe的启动改为管理员模式)~~

4. 安装雷电模拟器(雷电9), 将```AutoPcr_py\运行说明\模拟器配置\com.bilibili.priconne_960x540.kmp```放入按键配置文件夹并启用, 更改雷电模拟器分辨率为```960*540 dpi160```

5. ~~右键```AutoPcr4.0_GUI.py```-打开方式-选择python(深灰色)-点击始终~~ 解压, 运行```AutoPcr.exe```

6. 界面上选择雷电模拟器路径, 选择模拟器序号, 点击启动模拟器并运行

# 提示:

1. 本源码供学习用，禁止用于商业相关

2. 使用时不能有中文路径

3. Esc可退出程序

### 运行失败原因
1. 没有安装python

2. 没安装第三方库 解决: 管理员模式运行SetupPip.cmd

3. 文件夹有中文路径

4. GUI版模拟器启动不了?  解决: 模拟器路径改完 需要点击保存路径

5. 没有使用管理员模式运行 解决:将python.exe设置为管理员方式启动:

-属性->兼容性->更改所有用户设置->√管理员身份运行

-建议模拟器启动也设为管理员模拟式启动


# 运行需求:
Windows
python环境, 没用过python的还是不推荐去用了


## 1.py核心库:

 aircv 做图像识别;
 
 win32gui库获取模拟器截屏, 并做按钮键盘事件;
 
 PIL库做截图保存;
 
管理员模式运行 "SetupPip.cmd" 安装

