import os
import sys
import time
import mss
import mss.tools
import pyautogui
import natsort
import shutil

from pynput import mouse
from pynput.keyboard import Key, Controller
from PIL import Image

#from PySide6.QtCore import QSize, Qt
#from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMainWindow, QVBoxLayout, \
#    QHBoxLayout, QSlider

def tryint(maxn = 100,s=""):
    try : 
        a = int(input(s))
        if (0<=a<=maxn):
            return a
        elif a== -1:
            return a
        else:
            print("메뉴에 있는 번호를 선택해 주세요.")
            a = tryint()
            return a
    except: 
        print("숫자를 입력해 주세요.")
        a = tryint()
        return a

def xy():
    def on_click(x, y, button, pressed):
        if pressed:
            global x1
            global y1
            x1 = int(x)
            y1 = int(y)
            print('Button: %s, Position: (%s, %s), Pressed: %s ' % (button, x, y, pressed))
        #return posX,posY
        if not pressed:
            return False
        

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

x1 = 0
y1 = 0

def main():

    num = 1
    posX1 = 684
    posY1 = 98
    posX2 = 1237
    posY2 = 650
    posX3 = 1109
    posY3 = 679
    page = 201
    speed = 0.45
    region = {}
    print("default : 0, change : 1")
    changxy = tryint(1,"좌표 변경 : ")
    if changxy == 1:
        #print("")
        xy()#left_up
        posX1, posY1 = x1,y1
        xy()#right_down
        posX2, posY2 = x1,y1
        xy()#next
        posX3, posY3 = x1,y1
    changp = tryint(1,"페이지 수 변경 : ")
    if changp == 1:
        page = tryint(201, "페이지 수 : ")
    giboname = input("생성할 기보의 이름을 입력하세요.")
    
    #pos_x, pos_y = pyautogui.position()
    title = f"gibo_img/{giboname}"
    if not(os.path.isdir(title)):
        os.mkdir(os.path.join(title))

    # The screen part to capture
    region = {'top': posY1, 'left': posX1, 'width': posX2 - posX1,
              'height': posY2 - posY1}

    m = mouse.Controller()
    mouse_left = mouse.Button.left
    kb_control = Controller()

    try:
        # 화면 전환 위해 한번 클릭
        #time.sleep(2)
        #m.position = (posX1, posY1)

        #time.sleep(2)
        #m.click(mouse_left)
        #time.sleep(2)
        #m.position = (pos_x, pos_y)

        # 파일 저장
        while num <= page:

            time.sleep(speed)

            # 캡쳐하기
            with mss.mss() as sct:
                # Grab the data
                img = sct.grab(region)
                # Save to the picture file
                mss.tools.to_png(img.rgb, img.size, output=f'{title}/img_{str(num).zfill(4)}.png' )

            # 페이지 넘기기
            m.position = (posX3, posY3)

            #time.sleep(1)
            m.click(mouse_left)
            #time.sleep(1)

            num += 1

        print("캡쳐 완료!")
        
    except Exception as e:
        print('예외 발생. ', e)
        stat.setText('오류 발생. 종료 후 다시 시도해주세요.')

        
main()

