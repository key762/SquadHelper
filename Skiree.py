import os
import wx
import cv2
import math
import win32con
import win32gui
import win32ui
import threading
from sympy import *
from pynput import keyboard, mouse


class SquadHelper(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, pos=(1670, 0), size=(250, 20), style=wx.STAY_ON_TOP)
        # 标尺
        self.ruler = wx.StaticText(parent=self, id=id, label="标尺", pos=(0, 0), size=(50, 20),
                                   style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.ruler.SetBackgroundColour(''), self.ruler.SetForegroundColour('red')
        # 距离
        self.distance = wx.StaticText(parent=self, id=id, label="距离", pos=(50, 0), size=(50, 20),
                                      style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.distance.SetBackgroundColour(''), self.distance.SetForegroundColour('blue')
        # 方位
        self.position = wx.StaticText(parent=self, id=id, label="方位", pos=(100, 0), size=(50, 20),
                                      style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.position.SetBackgroundColour(''), self.position.SetForegroundColour('black')
        # 目标
        self.target = wx.StaticText(parent=self, id=id, label="目标", pos=(150, 0), size=(50, 20),
                                    style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.target.SetBackgroundColour(''), self.target.SetForegroundColour('purple')
        # 当前
        self.current = wx.StaticText(parent=self, id=id, label="当前", pos=(200, 0), size=(50, 20),
                                     style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.current.SetBackgroundColour(''), self.current.SetForegroundColour('orange')
        # 设置
        self.SetTransparent(230)
        self.Show()

    def setRuler(self, ruler):
        self.ruler.SetLabel(ruler)

    def setDistance(self, distance):
        self.distance.SetLabel(distance)

    def setPosition(self, position):
        self.position.SetLabel(position)

    def setTarget(self, target):
        self.target.SetLabel(target)

    def setCurrent(self, current):
        self.current.SetLabel(current)


def mouseThreading(frm):
    listener = mouse.Listener(on_move=lambda x, y: mouse_move(x, y, frm=frm))
    listener.start()


def mouse_move(x, y, frm):
    frm.setCurrent(str(y))


def winThreading(appWin):
    appWin.MainLoop()


def mainThreading(frm):
    listener = keyboard.Listener(on_press=lambda key: on_press(key, frm=frm))
    listener.start()


def window_capture(filename):
    hwnd = 0
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, 1304, 20)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (1304, 20), mfcDC, (560, 975), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)


def get_pix_avg(x: int, y: int):
    img = cv2.imread('./compare.jpg')
    blue = int(img[y, x, 0])
    green = int(img[y, x, 1])
    red = int(img[y, x, 2])
    return blue + green + red


def on_press(key, frm):
    global mouse_num
    global ruler_current
    global self_x
    global self_y
    global target_x
    global target_y
    global distance_current
    if key == keyboard.Key.f4:
        window_capture("compare.jpg")
        frm.setRuler('点自己')
        pix = get_pix_avg(1270, 2)
        if pix == 0:
            ruler_current = 900
            frm.setRuler('900m')
        elif pix < 10:
            pixTwo = get_pix_avg(1271, 1)
            if pixTwo == 252:
                ruler_current = 900
                frm.setRuler('900m')
            else:
                ruler_current = 300
                frm.setRuler('300m')
        elif pix > 10:
            ruler_current = 100
            frm.setRuler('100m')
        mouse_num = 0
        self_x = 0
        self_y = 0
        target_x = 0
        target_y = 0
        distance_current = 0
        frm.setDistance('点自己')
        mouseCheck(frm)
        os.remove("compare.jpg")


def mouseCheck(frm):
    with mouse.Listener(on_click=lambda x, y, button, pressed: mouse_click(x, y, button, pressed, frm=frm)) as listener:
        listener.join()


def getPixelDistance():
    p = 0
    for i in range(1304)[::-1]:
        if get_pix_avg(i, 19) == 0:
            p += 1
        else:
            break
    return p


def calc_angle(x1, y1, x2, y2):
    angle = 0
    x2 = x2 - x1
    y2 = y2 - y1
    x1 = 0
    y1 = 0
    dy = y2 - y1
    dx = x2 - x1
    if dx == 0 and dy > 0:
        angle = 0
    if dx == 0 and dy < 0:
        angle = 180
    if dy == 0 and dx > 0:
        angle = 90
    if dy == 0 and dx < 0:
        angle = 270
    if dx > 0 and dy > 0:
        angle = 180 - math.atan(dx / dy) * 180 / math.pi
    elif dx < 0 < dy:
        angle = 180 - math.atan(dx / dy) * 180 / math.pi
    elif dx < 0 and dy < 0:
        angle = 360 - math.atan(dx / dy) * 180 / math.pi
    elif dx > 0 > dy:
        angle = - math.atan(dx / dy) * 180 / math.pi
    return round(angle, 1)


def mouse_click(x, y, button, pressed, frm):
    global mouse_num
    global self_x
    global self_y
    global target_x
    global target_y
    global ruler_current
    global distance_current
    if pressed:
        if button == mouse.Button.left:
            if mouse_num == 2:
                return False
            else:
                if mouse_num == 0:
                    self_x = x
                    self_y = y
                    frm.setDistance("点目标")
                if mouse_num == 1:
                    target_x = x
                    target_y = y
                    distance_yuan = (((self_x - target_x) ** 2 + (self_y - target_y) ** 2) ** 0.5)
                    ruler_yuan = getPixelDistance()
                    if ruler_yuan == 0:
                        frm.setDistance("error")
                        return False
                    distance_current = round(((distance_yuan * ruler_current) / ruler_yuan), 1)
                    frm.setDistance(str(distance_current) + "m")
                    # 显示方位
                    frm.setPosition(str(calc_angle(self_x, self_y, target_x, target_y)) + '°')
                    # 显示仰角
                    if 274.35 <= distance_current <= 623.1:
                        x = Symbol('x')
                        a = solve([(-0.01) * x * x + (3.7 * x) + 268.3 - distance_current])
                        b = 0
                        for i in a:
                            if i.get(x) <= 180:
                                b = round(i.get(x), 1)
                        frm.setTarget(str(b))
                    else:
                        frm.setTarget(str('out'))
                    return False
                # 直接计算
                mouse_num += 1


if __name__ == '__main__':
    # 鼠标点击次数
    mouse_num = 0
    # 记录标尺
    ruler_current = 0
    # 记录自己的坐标
    self_x = 0
    self_y = 0
    # 记录目标的坐标
    target_x = 0
    target_y = 0
    # 记录距离
    distance_current = 0
    app = wx.App()
    frame = SquadHelper(None, -1, "SquadHelper")
    frame.setRuler("按F4")
    # 鼠标监控线程
    mouseThread = threading.Thread(target=mouseThreading(frame))
    mouseThread.start()
    # 键盘监控线程
    mainThread = threading.Thread(target=mainThreading(frame))
    mainThread.start()
    # 显示栏控件线程
    winThread = threading.Thread(target=winThreading(app))
    winThread.start()
    # 线程归束
    mainThread.join()
    winThread.join()
    mouseThread.join()
