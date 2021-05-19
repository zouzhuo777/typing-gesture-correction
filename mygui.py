from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os
import qtawesome
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2
from main1 import main_project
import time
from img_merge import merge_img


class SwitchBtn(QWidget):
    # 信号
    checkedChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)

        self.checked = False
        self.bgColorOff = QColor(21, 76, 187)
        self.bgColorOn = QColor(242, 144, 28)

        self.sliderColorOff = QColor(43, 44, 53)
        self.sliderColorOn = QColor(43, 44, 53)

        self.textColorOff = QColor(255, 255, 255)
        self.textColorOn = QColor(255, 255, 255)

        self.textOff = "OFF"
        self.textOn = "ON"

        self.space = 2
        self.rectRadius = 5

        self.step = self.width() / 50
        self.startX = 0
        self.endX = 0

        self.timer = QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.updateValue)  # 计时结束调用operate()方法

        # self.timer.start(5)  # 设置计时间隔并启动

        self.setFont(QFont("Microsoft Yahei", 10))

        # self.resize(10, 4)

    def updateValue(self):
        if self.checked:
            if self.startX < self.endX:
                self.startX = self.startX + self.step
            else:
                self.startX = self.endX
                self.timer.stop()
        else:
            if self.startX > self.endX:
                self.startX = self.startX - self.step
            else:
                self.startX = self.endX
                self.timer.stop()

        self.update()

    def mousePressEvent(self, event):
        self.checked = not self.checked
        # 发射信号
        self.checkedChanged.emit(self.checked)

        # 每次移动的步长为宽度的50分之一
        self.step = self.width() / 50
        # 状态切换改变后自动计算终点坐标
        if self.checked:
            self.endX = self.width() - self.height()
        else:
            self.endX = 0
        self.timer.start(5)

    def paintEvent(self, evt):
        # 绘制准备工作, 启用反锯齿
        painter = QPainter()

        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        self.drawBg(evt, painter)
        # 绘制滑块
        self.drawSlider(evt, painter)
        # 绘制文字
        self.drawText(evt, painter)

        painter.end()

    def drawText(self, event, painter):
        painter.save()

        if self.checked:
            painter.setPen(self.textColorOn)
            painter.drawText(0, 0, self.width() / 2 + self.space * 2, self.height(), Qt.AlignCenter, self.textOn)
        else:
            painter.setPen(self.textColorOff)
            painter.drawText(self.width() / 2, 0, self.width() / 2 - self.space, self.height(), Qt.AlignCenter,
                             self.textOff)

        painter.restore()

    def drawBg(self, event, painter):
        painter.save()
        painter.setPen(Qt.NoPen)

        if self.checked:
            painter.setBrush(self.bgColorOn)
        else:
            painter.setBrush(self.bgColorOff)

        rect = QRect(0, 0, self.width(), self.height())
        # 半径为高度的一半
        radius = rect.height() / 2
        # 圆的宽度为高度
        circleWidth = rect.height()

        path = QPainterPath()
        path.moveTo(radius, rect.left())
        path.arcTo(QRectF(rect.left(), rect.top(), circleWidth, circleWidth), 90, 180)
        path.lineTo(rect.width() - radius, rect.height())
        path.arcTo(QRectF(rect.width() - rect.height(), rect.top(), circleWidth, circleWidth), 270, 180)
        path.lineTo(radius, rect.top())

        painter.drawPath(path)
        painter.restore()

    def drawSlider(self, event, painter):
        painter.save()

        if self.checked:
            painter.setBrush(self.sliderColorOn)
        else:
            painter.setBrush(self.sliderColorOff)

        rect = QRect(0, 0, self.width(), self.height())
        sliderWidth = rect.height() - self.space * 2
        sliderRect = QRect(self.startX + self.space, self.space, sliderWidth, sliderWidth)
        painter.drawEllipse(sliderRect)

        painter.restore()


class MyTextEdit(QtWidgets.QTextEdit):
    def __init__(self, *__args):
        # 上一个键盘输入的ascii码
        self.last_input = -1
        # 是否按下了按钮，新判定一次，否则继续输出上次的结果
        self.refresh_flag = False

        super(MyTextEdit, self).__init__(*__args)

    # 键盘事件拦截，要保持原本的作用，还要将当前按下的键转化为对应字符串放入self.last_input
    # fn,caps无法识别，左右shift,ctrl,alt,win不能区分，另外，被占用的快捷键无法识别，其他主键位按键都没问题
    def keyPressEvent(self, keyevent):
        key = keyevent.key()
        text = keyevent.text()
        # print(keyevent.text(), keyevent.key())

        if Qt.Key_A <= key <= Qt.Key_Z:
            self.last_input = text.upper()
        elif Qt.Key_0 <= key <= Qt.Key_9:
            self.last_input = str(key - Qt.Key_0)
        elif Qt.Key_F1 <= key <= Qt.Key_F12:
            self.last_input = 'F' + str(key - Qt.Key_F1 + 1)
        elif key == 16777216:
            self.last_input = 'Esc'
        elif key == 96 or key == 126:
            self.last_input = '~'
        elif key == 45:
            self.last_input = '-'
        elif key == 61:
            self.last_input = '='
        elif key == 16777219:
            self.last_input = 'Backspace'
        elif key == 16777217:
            self.last_input = 'Tab'
        elif key == 91:
            self.last_input = '['
        elif key == 93:
            self.last_input = ']'
        elif key == 92:
            self.last_input = '\\'
        elif key == 59:
            self.last_input = ';'
        elif key == 39:
            self.last_input = '\"'
        elif key == 16777220:
            self.last_input = 'Return'
        elif key == 16777248:
            self.last_input = 'Shift'
        elif key == 44:
            self.last_input = ','
        elif key == 46:
            self.last_input = '.'
        elif key == 47:
            self.last_input = '/'
        elif key == 16777249:
            self.last_input = 'Ctrl'
        elif key == 16777250:
            self.last_input = 'Win'
        elif key == 16777251:
            self.last_input = 'Alt'
        elif key == 32:
            self.last_input = 'Space'

        print('按下:', self.last_input)
        self.refresh_flag = True
        return super(MyTextEdit, self).keyPressEvent(keyevent)


class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # 是否检测键盘布局
        self.check_keyboard_flag = False
        self.m_drag = False

        # 定时器：xx ms捕获一帧
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(500)

        print('初始化main_project')
        self.main_project = main_project()
        print('初始化main_project完成')
        self.textshow('程序初始化完成')
        keyboard = cv2.imread('right_wrong/keyboard.png', cv2.IMREAD_UNCHANGED)
        ori_hand = cv2.imread('right_wrong/origin.png', cv2.IMREAD_UNCHANGED)
        self.ori_pic = merge_img(keyboard, ori_hand, 0, ori_hand.shape[0], 0, ori_hand.shape[1])
        # ori_pic = cv2.imread('./right_wrong/keyboard.png')
        self.set_label_Iamge(self.ori_pic)

    def init_ui(self):
        self.setFixedSize(1400, 860)
        self.main_widget = QtWidgets.QWidget()  # 创建窗口主部件
        self.main_layout = QtWidgets.QGridLayout()  # 创建主部件的网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        self.left_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.left_widget.setObjectName('left_widget')
        self.left_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.left_widget.setLayout(self.left_layout)  # 设置左侧部件布局为网格

        self.left2_widget = QtWidgets.QWidget()  # 创建左侧2部件
        self.left2_widget.setObjectName('left2_widget')
        self.left2_layout = QtWidgets.QGridLayout()  # 创建左侧2部件的网格布局层
        self.left2_widget.setLayout(self.left2_layout)  # 设置左侧2部件布局为网格

        self.on_widget = QtWidgets.QWidget()  # 创建右上侧部件
        self.on_widget.setObjectName('on_widget')
        self.on_layout = QtWidgets.QGridLayout()
        self.on_widget.setLayout(self.on_layout)  # 设置右上侧部件布局为网格

        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QtWidgets.QGridLayout()
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.mid_widget = QtWidgets.QWidget()  # 创建mid部件
        self.mid_widget.setObjectName('mid_widget')
        self.mid_layout = QtWidgets.QGridLayout()
        self.mid_widget.setLayout(self.mid_layout)  # 设置mid部件布局为网格

        self.te = MyTextEdit(self.mid_widget)
        self.te.setPlaceholderText("Input something...")

        self.statearea = QtWidgets.QTextEdit(self.mid_widget)
        # self.statearea.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.statearea.setAlignment(Qt.AlignTop)
        self.statearea.setPlaceholderText("Output information:")

        self.mid_layout.addWidget(self.te, 0, 0, 1, 1)
        self.mid_layout.addWidget(self.statearea, 0, 1, 1, 1)

        self.under_widget = QtWidgets.QWidget()  # 创建under部件
        self.under_widget.setObjectName('under_widget')
        self.under_layout = QtWidgets.QGridLayout()
        self.under_widget.setLayout(self.under_layout)  # 设置under部件布局为网格

        self.top_widget = QtWidgets.QWidget()  # 创建top控件 是空的

        self.main_layout.addWidget(self.top_widget, 0, 0, 1, 8)
        self.main_layout.addWidget(self.left_widget, 1, 0, 6, 8)
        self.main_layout.addWidget(self.left2_widget, 1, 8, 6, 8)
        self.main_layout.addWidget(self.on_widget, 0, 16, 1, 3)
        self.main_layout.addWidget(self.right_widget, 1, 16, 6, 3)
        self.main_layout.addWidget(self.mid_widget, 7, 0, 3, 19)
        self.main_layout.addWidget(self.under_widget, 10, 0, 1, 19)

        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

        self.labelCamera = QtWidgets.QLabel(self.left_widget)  # 创建显示摄像头画面的label
        self.left_layout.addWidget(self.labelCamera, 0, 0, 1, 1)
        self.labelCamera.setFixedSize(518, 370)
        self.labelCamera.setObjectName("labelCamera")

        self.labelImage = QtWidgets.QLabel(self.left2_widget)  # 创建显示提示图像画面的label
        self.left2_layout.addWidget(self.labelImage, 0, 0, 1, 1)
        self.labelImage.setFixedSize(590, 236)
        self.labelImage.setObjectName("labelImage")

        self.close_btn = QtWidgets.QPushButton("")  # 关闭按钮
        self.max_btn = QtWidgets.QPushButton("")  # 空白按钮
        self.mini_btn = QtWidgets.QPushButton("")  # 最小化按钮

        self.close_btn.clicked.connect(self.close)
        self.max_btn.clicked.connect(self.slot_max_or_recv)
        self.mini_btn.clicked.connect(self.showMinimized)

        self.on_layout.addWidget(self.mini_btn, 0, 0, 1, 1)
        self.on_layout.addWidget(self.max_btn, 0, 1, 1, 1)
        self.on_layout.addWidget(self.close_btn, 0, 2, 1, 1)

        self.close_btn.setFixedSize(20, 20)  # 设置关闭按钮的大小
        self.max_btn.setFixedSize(20, 20)  # 设置按钮大小
        self.mini_btn.setFixedSize(20, 20)  # 设置最小化按钮大小

        self.switchBtn_1 = SwitchBtn(self)
        self.switchBtn_2 = SwitchBtn(self)
        self.switchBtn_3 = SwitchBtn(self)

        # self.switchBtn_1.checkedChanged.connect(self.getState)
        # self.switchBtn_2.checkedChanged.connect(self.getState)
        # self.switchBtn_3.checkedChanged.connect(self.getState)

        self.right_layout.addWidget(self.switchBtn_1, 1, 0, 1, 1)
        self.right_layout.addWidget(self.switchBtn_2, 3, 0, 1, 1)
        self.right_layout.addWidget(self.switchBtn_3, 5, 0, 1, 1)

        self.switchBtn_1.setFixedSize(100, 35)
        self.switchBtn_2.setFixedSize(100, 35)
        self.switchBtn_3.setFixedSize(100, 35)

        self.right_lable_0 = QtWidgets.QLabel("")
        self.right_lable_1 = QtWidgets.QLabel("键盘检测AR显示")
        self.right_lable_2 = QtWidgets.QLabel("手部检测AR显示")
        self.right_lable_3 = QtWidgets.QLabel("手部关键点AR显示")
        self.right_lable_4 = QtWidgets.QLabel("")

        self.right_lable_0.setObjectName('right_lable')
        self.right_lable_1.setObjectName('right_lable')
        self.right_lable_2.setObjectName('right_lable')
        self.right_lable_3.setObjectName('right_lable')
        self.right_lable_4.setObjectName('right_lable')

        self.right_layout.addWidget(self.right_lable_0, 0, 0, 1, 1)
        self.right_layout.addWidget(self.right_lable_1, 2, 0, 1, 1)
        self.right_layout.addWidget(self.right_lable_2, 4, 0, 1, 1)
        self.right_layout.addWidget(self.right_lable_3, 6, 0, 1, 1)
        self.right_layout.addWidget(self.right_lable_4, 7, 0, 1, 1)

        self.under_button_0 = QtWidgets.QPushButton(QIcon('./art/使用说明.png'), "使用说明")
        self.under_button_1 = QtWidgets.QPushButton(QIcon('./art/参数设置.png'), "参数设置")
        self.under_button_2 = QtWidgets.QPushButton(QIcon('./art/摄像头开启.png'), "摄像头开启")
        self.under_button_3 = QtWidgets.QPushButton(QIcon('./art/检测键盘.png'), "键盘检测")
        self.under_button_4 = QtWidgets.QPushButton(QIcon('./art/重置日志.png'), "重置日志")
        self.under_button_5 = QtWidgets.QPushButton(QIcon('./art/导出日志.png'), "导出日志")

        self.under_button_0.setFixedSize(210, 80)
        self.under_button_1.setFixedSize(210, 80)
        self.under_button_2.setFixedSize(210, 80)
        self.under_button_3.setFixedSize(210, 80)
        self.under_button_4.setFixedSize(210, 80)
        self.under_button_5.setFixedSize(210, 80)

        self.under_button_0.setIconSize(QSize(32, 32))
        self.under_button_1.setIconSize(QSize(32, 32))
        self.under_button_2.setIconSize(QSize(32, 32))
        self.under_button_3.setIconSize(QSize(32, 32))
        self.under_button_4.setIconSize(QSize(32, 32))
        self.under_button_5.setIconSize(QSize(32, 32))

        self.under_button_0.setObjectName('under_button')
        self.under_button_1.setObjectName('under_button')
        self.under_button_2.setObjectName('under_button')
        self.under_button_3.setObjectName('under_button')
        self.under_button_4.setObjectName('under_button')
        self.under_button_5.setObjectName('under_button')

        self.under_layout.addWidget(self.under_button_0, 0, 0, 1, 1)
        self.under_layout.addWidget(self.under_button_1, 0, 1, 1, 1)
        self.under_layout.addWidget(self.under_button_2, 0, 2, 1, 1)
        self.under_layout.addWidget(self.under_button_3, 0, 3, 1, 1)
        self.under_layout.addWidget(self.under_button_4, 0, 4, 1, 1)
        self.under_layout.addWidget(self.under_button_5, 0, 5, 1, 1)

        self.under_button_0.clicked.connect(self.useinfo)
        self.under_button_1.clicked.connect(self.reference_Clicked)
        self.under_button_2.clicked.connect(self.run_Clicked)
        self.under_button_3.clicked.connect(self.check_keyboard_clicked)
        self.under_button_4.clicked.connect(self.clearlog)
        self.under_button_5.clicked.connect(self.outputlog)

        self.close_btn.setStyleSheet('''QPushButton{background:#F76677;border-radius:5px;}QPushButton:hover{
                background:red;}''')
        self.max_btn.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{
                background:yellow;}''')
        self.mini_btn.setStyleSheet('''QPushButton{background:#6DDF6D;border-radius:5px;}QPushButton:hover{
                background:green;}''')

        self.left_widget.setStyleSheet('''
                QWidget#left_widget{
                    background:rgba(0,0,0,0%);
                    border-top-left-radius:10px;
                    border-bottom-left-radius:10px;
                }
            ''')
        self.left2_widget.setStyleSheet('''
                QWidget#left2_widget{
                    background:rgba(0,0,0,0%);
                }
            ''')

        self.on_widget.setStyleSheet('''
                    QWidget#on_widget{
                    background:rgba(0,0,0,0%);
                    border-top-right-radius:10px;
                    border-bottom-right-radius:10px;
                }
                ''')

        self.right_widget.setStyleSheet('''
                QWidget{border:none;color:white;}
                QWidget#right_widget{
                    background:rgba(0,0,0,0%);
                    border-top-right-radius:10px;
                    border-bottom-right-radius:10px;
                }
                QLabel{
                    border:none;
                    font-size:20px;
                    font-weight:700;
                    font-family: "Microsoft YaHei";
                    font-weight:bold;
                }
            ''')

        self.mid_widget.setStyleSheet('''
                QWidget#mid_widget{
                    background:rgba(7, 34, 71, 20%);
                    border-top-right-radius:10px;
                    border-bottom-right-radius:10px;
                    border-top-left-radius:10px;
                    border-bottom-left-radius:10px;
                }
            ''')
        self.statearea.setStyleSheet('''
            background:rgba(41, 57, 85,20%);
            font-size:18px;
            font-family: "Microsoft YaHei";
            color:white;
            border:none;
        ''')

        self.te.setStyleSheet('''
            background:rgba(41, 57, 85,20%);
            font-size:18px;
            font-family: "Microsoft YaHei";
            color:white;
            border:none;
        ''')

        self.under_widget.setStyleSheet('''
                QPushButton{
                    background:rgba(14, 33, 63, 40%);
                    border:none;
                    color:white;
                    font-size:20px;
                    font-family: "Microsoft YaHei";
                    border-top-right-radius:10px;
                    border-bottom-right-radius:10px;
                    border-top-left-radius:10px;
                    border-bottom-left-radius:10px;
                }
                QPushButton#under_button:hover{
                    border-left:4px solid white;
                    border-right:4px solid white;
                }
                QWidget#under_widget{
                    background:rgba(0,0,0,00%);
                    border-top-right-radius:10px;
                    border-bottom-right-radius:10px;
                    border-top-left-radius:10px;
                    border-bottom-left-radius:10px;
                }
            ''')

        # 主界面美化
        palette1 = QtGui.QPalette()
        palette1.setBrush(self.backgroundRole(), QBrush(QPixmap('./art/bg.png')))  # 设置背景图片
        self.setPalette(palette1)
        # self.setWindowOpacity(0.5)  # 设置窗口透明度
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 隐藏边框

        self.main_layout.setSpacing(20)

    # 鼠标长按事件
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

    # 鼠标移动事件
    def mouseMoveEvent(self, QMouseEvent):
        if QtCore.Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    # 鼠标释放事件
    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    # def keyPressEvent(self, keyevent):
    #     # print(f"键盘按键: {keyevent.text()},0X{keyevent.key():X} 被按下")
    #     print(keyevent.text(), self.last_input)

    # 检测键盘布局按钮被按下
    def check_keyboard_clicked(self):
        self.check_keyboard_flag = True

    # 窗口最大化与恢复
    def slot_max_or_recv(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def useinfo(self):
        # str = self.te.toPlainText()
        # for each in str:
        #     print(int(each))
        QMessageBox.information(self, '使用说明', '1. 用户首先需要点击“参数设置”按钮，选择开启本地摄像头还是外接摄像头（可默认）；\n'
                                              '2. 当摄像头拍摄到键盘后，点击“键盘检测”，软件就能读入键盘的按键布局坐标。'
                                              '可以选择打开左上角的“键盘检测AR显示”选项，键盘标注点就会显示在实时图像上。\n'
                                              '3. 打开“手部检测AR显示”之后，软件会在实时图像中框出手部区域。\n'
                                              '4. 打开“手部关键点AR显示”之后，将会在实时图像中显示手部关键点和手的骨架。\n'
                                              '5. 用户在左下角的输入框中练习打字，对应的指法判断将会显示在右上角的示意图中。\n'
                                              '如果用户指法正确，对应按键和手指将在右上角示意图中标绿，错误则标红。\n'
                                              '6. 右下角会打印对应操作的日志信息，可以通过“重置日志”来清空日志栏，按下“导出日志”按钮将日志导出。\n'
                                              '7. 本程序仅针对ANSI标准布局的主键盘区，要求英文状态下输入，另外，fn,caps无法识别\n'
                                              '', QMessageBox.Ok)

    def run_Clicked(self):
        self._timer.start()

    def reference_Clicked(self):
        value, ok = QInputDialog.getInt(self, "参数设置", "1. 摄像头编号\n请输入整数:", 0, 0, 1, 1)
        self.camera = cv2.VideoCapture(value, cv2.CAP_DSHOW)

    def clearlog(self):
        self.set_label_Iamge(self.ori_pic)
        self.statearea.clear()

    def outputlog(self):
        str = self.statearea.toPlainText()
        fileName, filetype = QFileDialog.getOpenFileName(self, "选择文件", os.getcwd())
        if fileName != '':
            fp = open(fileName, "w")
            fp.write(str)
            fp.close()

    # 输出提示图像的函数
    def set_label_Iamge(self, image):
        img_rows, img_cols, channels = image.shape
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
        bytesPerLine = channels * img_cols
        QImg = QImage(image.data, img_cols, img_rows, bytesPerLine, QImage.Format_RGB888)
        self.labelImage.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelImage.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    @QtCore.pyqtSlot()
    def _queryFrame(self):
        # QApplication.processEvents()
        ret, self.frame = self.camera.read()
        if not ret:
            print('摄像头读取错误')
            exit()
        img_rows, img_cols, channels = self.frame.shape
        self.frame = self.change_image(self.frame)
        cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB, self.frame)  # 是否需要在传入模型前先转RGB?

        bytesPerLine = channels * img_cols
        QImg = QImage(self.frame.data, img_cols, img_rows, bytesPerLine, QImage.Format_RGB888)
        self.labelCamera.setPixmap(QPixmap.fromImage(QImg).scaled(
            self.labelCamera.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # 这里调用main_project的函数，来对img进行改变
    # 具体来说，每一帧进行手部检测和关键点识别，当refresh_flag时也进行“纠正提示”
    def change_image(self, img):
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, 180, 1)
        img = cv2.warpAffine(img, M, (w, h))

        img0 = img.copy()
        img1 = img.copy()
        img2 = img.copy()

        if self.check_keyboard_flag:
            self.check_keyboard_flag = False
            text = self.main_project.check_keyboard(img0)
            self.textshow(text)
        if self.switchBtn_2.checked or self.switchBtn_3.checked or self.te.refresh_flag:
            self.main_project.check_hands(img1)
        if self.switchBtn_3.checked or self.te.refresh_flag:
            self.main_project.check_hands_points(img2)

        if self.switchBtn_1.checked:
            if len(self.main_project.M) != 0:
                img = self.main_project.draw_keyboard(img)
        if self.switchBtn_2.checked:
            img = self.main_project.draw_hands(img)
        if self.switchBtn_3.checked:
            img = self.main_project.draw_hands_points(img)
        if self.te.refresh_flag:
            self.te.refresh_flag = False
            if len(self.main_project.M) == 0:
                self.textshow('请先检测键盘再进行指法判断')
            else:
                print('进入指法纠正处理图像')
                # 这里判决是否调用“纠正提示”
                self.main_project.last_input = self.te.last_input
                img_right_wrong, text = self.main_project.gesture_correction(img)
                # 返回的是文字提示和图片提示，分别放到日志区域和image显示区域
                self.textshow(text)
                self.set_label_Iamge(img_right_wrong)
        return img

    # 追加写入字符串到日志区域
    def textshow(self, text):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.statearea.append(current_time + '  ' + text)


def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
