import pyautogui
import cv2
import math
import threading
import win32con
import win32gui
import win32ui
from pynput import keyboard, mouse
from wx import *
import pydirectinput
from sympy import *

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
    elif dx < 0 and dy > 0:
        angle = 180 - math.atan(dx / dy) * 180 / math.pi
    elif dx < 0 and dy < 0:
        angle = 360 - math.atan(dx / dy) * 180 / math.pi
    elif dx > 0 and dy < 0:
        angle = - math.atan(dx / dy) * 180 / math.pi
    return round(angle, 1)


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


def mouse_click(x, y, button, pressed, frm):
    global mousenum
    global self_x
    global self_y
    global target_x
    global target_y
    global distancet_st
    global ruler_st
    global now_target_y
    if pressed:
        if button == mouse.Button.left:
            if mousenum == 2:
                return False
            else:
                if mousenum == 0:
                    self_x = x
                    self_y = y
                    frm.distancetext("点目标")
                if mousenum == 1:
                    target_x = x
                    target_y = y
                    frm.distancetext("Waiting")
                    distancet_yuan = (((self_x - target_x) ** 2 + (self_y - target_y) ** 2) ** 0.5)
                    ruler_yuan = getnowdistance()
                    if ruler_yuan == 0:
                        frm.distancetext("Exception")
                        return False
                    distancet_st = round(((distancet_yuan * ruler_st) / ruler_yuan), 1)
                    frm.distancetext(str(distancet_st))
                    # 显示方位
                    frm.positiontext(str(calc_angle(self_x, self_y, target_x, target_y)) + '°')
                    # 显示仰角
                    now_target_y = round(((distancet_st - 290.16) / 4.57), 1)
                    if distancet_st >= 274.35 and distancet_st <= 623.1:
                        x = Symbol('x')
                        a = solve([(-0.01) * x * x + (3.7 * x) + 268.3 - distancet_st])
                        b = 0
                        for i in a:
                            if i.get(x) <= 180:
                                b = round(i.get(x), 1)
                        frm.elevationtext(str(b))
                    else:
                        frm.elevationtext(str('out'))
                    return False
                #     直接计算
                mousenum += 1


def on_press(key, frm):
    global mousenum
    global self_x
    global self_y
    global target_x
    global target_y
    global distancet_st
    global ruler_st
    global now_y
    global now_target_y
    if key == keyboard.Key.f4:
        window_capture("compare.jpg")
        frm.distancetext('点自己')
        frm.positiontext('Waiting')
        if get_pix_avg(1270, 2) == 0:
            ruler_st = 900
            frm.rulertext('900m')
        elif get_pix_avg(1270, 2) < 10:
            ruler_st = 300
            frm.rulertext('300m')
        elif get_pix_avg(1270, 2) > 10:
            ruler_st = 100
            frm.rulertext('100m')
        mousenum = 0
        self_x = 0
        self_y = 0
        target_x = 0
        target_y = 0
        distancet_st = 0
        mousecode(frm)
    # if key == keyboard.Key.f5:
    #     if now_target_y != -1:
    #         now_target_y_flag = int(now_target_y)
    #         move_y = now_target_y_flag - now_y
    #         move_y_now = int(move_y)
    #         # print("f5  " +  str(move_y_now) + "   TARGET "+ str(now_target_y_flag))
    #         pydirectinput.moveRel(0, move_y_now, relative=True)
    #         x2, y2 = pydirectinput.position()
    #         frm.elevationnowtext(str(y2))
    if key == keyboard.Key.f5:
        pydirectinput.moveRel(0, 10, relative=True)
    if key == keyboard.Key.f6:
        pydirectinput.moveRel(0, 5, relative=True)
    if key == keyboard.Key.f7:
        pydirectinput.moveRel(0, 1, relative=True)
    if key == keyboard.Key.f8:
        pydirectinput.moveRel(0, -1, relative=True)
    if key == keyboard.Key.f11:
        pydirectinput.moveRel(0, 10, relative=True)
    # if key == keyboard.Key.f8:
    #     x = Symbol('x')
    #     a = solve([(-0.01) * x * x + (3.7 * x) + 268.3 - 525.2])
    #     b = 0
    #     for i in a:
    #         if i.get(x) <= 180:
    #             b = round(i.get(x), 1)
    #     print(b)

def get_pix_avg(x: int, y: int):
    img = cv2.imread('./compare.jpg')
    blue = int(img[y, x, 0])
    green = int(img[y, x, 1])
    red = int(img[y, x, 2])
    return blue + green + red


def listen_key_nblock(frm):
    listener = keyboard.Listener(on_press=lambda key: on_press(key, frm=frm))
    listener.start()


def maincode(frm):
    listen_key_nblock(frm)


class Trans(Frame):
    def __init__(self, parent, id, title):
        Frame.__init__(self, parent, id, title, pos=(1460, 0), size=(460, 20), style=STAY_ON_TOP)
        # Frame.__init__(self, parent, id, title, pos=(1430, 0), size=(500, 20), style=STAY_ON_TOP)
        # 设置标尺
        self.ruleritle = TextCtrl(self, value='标尺', style=TE_CENTER|TE_READONLY, pos=(0, 0), size=(40, 20))
        self.ruleritle.SetBackgroundColour(''), self.ruleritle.SetForegroundColour('Steel Blue')
        self.ruler = TextCtrl(self, style=TE_CENTER + TE_READONLY, pos=(40, 0), size=(60, 20))
        self.ruler.SetBackgroundColour(''), self.ruler.SetForegroundColour('Steel Blue')
        # 设置距离
        self.distancetitle = TextCtrl(self, value='距离', style=TE_CENTER + TE_READONLY, pos=(100, 0), size=(40, 20))
        self.distancetitle.SetBackgroundColour(''), self.distancetitle.SetForegroundColour('Steel Blue')
        self.distance = TextCtrl(self, style=TE_CENTER + TE_READONLY, pos=(140, 0), size=(60, 20))
        self.distance.SetBackgroundColour(''), self.distance.SetForegroundColour('Steel Blue')
        # 设置方位
        self.positiontitle = TextCtrl(self, value='方位', style=TE_CENTER + TE_READONLY, pos=(200, 0), size=(40, 20))
        self.positiontitle.SetBackgroundColour(''), self.positiontitle.SetForegroundColour('Steel Blue')
        self.position = TextCtrl(self, style=TE_CENTER + TE_READONLY, pos=(240, 0), size=(60, 20))
        self.position.SetBackgroundColour(''), self.position.SetForegroundColour('Steel Blue')

        # 设置仰角
        self.elevationtitle = TextCtrl(self, value='仰角', style=TE_CENTER + TE_READONLY, pos=(300, 0), size=(40, 20))
        self.elevationtitle.SetBackgroundColour(''), self.elevationtitle.SetForegroundColour('Steel Blue')
        self.elevation = TextCtrl(self, style=TE_CENTER + TE_READONLY, pos=(340, 0), size=(60, 20))
        self.elevation.SetBackgroundColour(''), self.elevation.SetForegroundColour('Steel Blue')

        self.elevationnow = TextCtrl(self, style=TE_CENTER + TE_READONLY, pos=(400, 0), size=(60, 20))
        self.elevationnow.SetBackgroundColour(''), self.elevationnow.SetForegroundColour('Steel Blue')

        self.SetTransparent(200)  # 设置透明
        self.Show()

    def distancetext(self, distance):
        self.distance.SetValue(distance)

    def rulertext(self, ruler):
        self.ruler.SetValue(ruler)

    def positiontext(self, position):
        self.position.SetValue(position)

    def elevationnowtext(self, elevationnow):
        self.elevationnow.SetValue(elevationnow)

    def elevationtext(self, elevation):
        self.elevation.SetValue(elevation)


def wincode(app):
    app.MainLoop()


def mouse_move(x, y, frm):
    global now_y
    now_y = y
    #     old_y = frm.elevation.GetValue()
    #     # if old_y != '':
    #     #     print("旧的" + old_y + "/" + str(y) + "     " + str(int(old_y) - y))
    # frm.elevationtext(str(y))
    frm.elevationnowtext(str(y))
    # if y == 540:
    #     frm.elevationnowtext("0°")
    # elif y < 540:
    #     updata = y - 540
    #     upjiao = round((updata / 6), 1)
    #     frm.elevationnowtext(str(-upjiao) + "°")
    # elif y > 540:
    #     downdata = y - 540
    #     downjiao = round((downdata / 6), 1)
    #     frm.elevationnowtext("-" + str(downjiao) + "°")


def mousecode(frm):
    with mouse.Listener(on_click=lambda x, y, button, pressed: mouse_click(x, y, button, pressed, frm=frm)) as listener:
        listener.join()


def mousemovecode(frm):
    listener = mouse.Listener(on_move=lambda x, y: mouse_move(x, y, frm=frm))
    listener.start()


def getvalue(x: int, y: int):
    img = cv2.imread('./compare.jpg')
    blue = int(img[y, x, 0])
    green = int(img[y, x, 1])
    red = int(img[y, x, 2])
    return blue + green + red


def getnowdistance():
    p = 0
    for i in range(1304)[::-1]:
        if getvalue(i, 19) == 0:
            p += 1
        else:
            break
    return p


if __name__ == '__main__':
    mousenum = 0
    self_x = 0
    self_y = 0
    target_x = 0
    target_y = 0
    distancet_st = 0
    ruler_st = 0
    now_target_y = -1
    now_y = 0
    app = App()
    frm = Trans(None, 1, "Squad Helper")
    frm.rulertext('点F4')

    test_3 = threading.Thread(target=mousemovecode(frm))
    test_3.start()

    test_1 = threading.Thread(target=maincode(frm))
    test_1.start()

    test_2 = threading.Thread(target=wincode(app))
    test_2.start()

    test_1.join()
    test_2.join()
    test_3.join()
