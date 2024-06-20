import os
import time
import mss
import mss.tools
import pyautogui

from pynput import mouse
from pynput.keyboard import Key, Controller
from PIL import Image


def tryint(maxn=100, s=""):
    try:
        a = int(input(s))
        if 0 <= a <= maxn or a == -1:
            return a
        else:
            print("메뉴에 있는 번호를 선택해 주세요.")
            return tryint(maxn, s)
    except ValueError:
        print("숫자를 입력해 주세요.")
        return tryint(maxn, s)

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
    left_up = (684, 98)
    right_down = (1237, 650)
    n_ext = (1109, 679)
    gozero = (714, 683)
    goback = (716, 66)
    page = 1
    speed = 0.45
    region = {}
    print("default : 0, change : 1")
    changxy = tryint(1,"좌표 변경 : ")
    if changxy == 1:
        print("좌상단 : ", end = "")
        xy()#left_up
        left_up = (x1,y1)
        print("우하단 : ", end = "")
        xy()#right_down
        right_down = (x1,y1)
        print("다음 : ", end = "")
        xy()#next
        n_ext = (x1,y1)
        print("맨앞으로 : ", end = "")
        xy()#gozero
        gozero = (x1, y1)
        print("뒤로가기 : ", end = "")
        xy()#goback
        goback = (x1, y1)
    page = tryint(201, "페이지 수 : ")
    giboname = input("생성할 기보의 이름을 입력하세요.")
    
    #pos_x, pos_y = pyautogui.position()
    title = f"gibo_img/{giboname}"
    if not(os.path.isdir(title)):
        os.mkdir(os.path.join(title))

    # The screen part to capture
    region = {'top': left_up[1], 'left': left_up[0], 'width': right_down[0] - left_up[0],
        'height': right_down[1] - left_up[1]}

    m = mouse.Controller()
    mouse_left = mouse.Button.left

    try:
        m.position = gozero
        m.click(mouse_left)
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
            m.position = n_ext
            m.click(mouse_left)
            

            num += 1

        print("캡쳐 완료!")
        m.position = goback
        m.click(mouse_left)
        
    except Exception as e:
        print('오류 발생. ', e)

