import os
import time
import mss
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"

from pynput import mouse
from PIL import Image
import numpy as np

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

def tryint2(txt, least=30):
    txt = txt.replace('\n','')
    try:
        a = int(txt)
        if least<a<=200:
            return a
        else :
            print("범위 외. 입력값 :",a)
            return 0
    except:
        print("숫자 인식 불가. 입력값 :", txt)
        return 0

def xy():
    def on_click(x, y, button, pressed):
        if pressed:
            global x1, y1
            x1, y1 = int(x), int(y)
            print('Button: %s, Position: (%s, %s), Pressed: %s ' % (button, x, y, pressed))
        #return posX,posY
        #if not pressed:
            return False
        
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

def chkdup(input_list):
    # 입력된 값들을 딕셔너리로 변환하여 각 값의 출현 횟수를 세기
    counts = {}
    for item in input_list:
        counts[item] = counts.get(item, 0) + 1
    
    # 중복된 값에 대해 이름 변경
    renamed_list = []
    for item in input_list:
        if counts[item] > 1:
            renamed_list.append(f"{item}_({counts[item]})")
            counts[item] -= 1
        else:
            renamed_list.append(item)
    return renamed_list

def preprocess_image(image_path):
    # 이미지 로드
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # 이미지 확대
    scale_percent = 300  # 이미지 크기를 300%로 확대
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)
    
    # 이진화
    _, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 잡음 제거
    processed_image = cv2.medianBlur(binary_image, 3)
    
    return processed_image

def capture_screenshot(region, output_path):
    with mss.mss() as sct:
        img = sct.grab(region)
        mss.tools.to_png(img.rgb, img.size, output=output_path)

def chkmode(imgP):
    tmpA = cv2.imread("icon/resize/@@@@.png", cv2.IMREAD_GRAYSCALE)
    tmpM = cv2.imread("icon/resize/----2.png", cv2.IMREAD_GRAYSCALE)
    tmpM2 = cv2.imread("icon/resize/----.png", cv2.IMREAD_GRAYSCALE)
    image = np.fromfile(imgP, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    #image = cv2.imread(imgP, cv2.IMREAD_GRAYSCALE) 한글경로에러 발생 가능.

    result = cv2.matchTemplate(image, tmpA, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    threshold = 0.7
    # 일치율 (0과 1 사이의 값) # 아이콘 생성 애니메이션 때문에 감지되지 않는 경우들이 생겨서 조금 넉넉하게 잡음.
    # 그런데도 검출되지 않는 것들이 종종 생겨서 그냥 speed를 0.6? 정도로 조정하는 게 맞을지도?
    if max_val > threshold:
        print("한수쉼 감지")
        return 1
    result = cv2.matchTemplate(image, tmpM, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > threshold:
        print("댓글 감지")
        return 1
    result = cv2.matchTemplate(image, tmpM2, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > threshold:
        print("댓글 감지")
        return 1
    else :
        return 0

x1 = 0
y1 = 0

def main(changxy=1):
    
    left_up = (684, 98)
    right_down = (1237, 650)
    n_ext = (1109, 679)
    numx, numy = (930,655), (980,680)
    #namex, namey = (766,99), (1136, 1020)
    gozero, goback = (714, 683), (716, 66)
    gibo1, gibo6 = 160, 940
    gibox, giboy = (left_up[0]+right_down[0])//2, (gibo6 - gibo1)//5 # 한 화면에 뜨는 기보가 6개가 아니라 n개면 //(n-1)로 하면 됨. 
    gumto = (960, 740) #검출모드에서 한수쉼이(@@@@)나 댓글(----)가 검출되면 눌러서 깨끗한 버전 캡쳐할 용도
    gumtoLU = (684,200) #검토창의 좌상단
    gumtoRD = (1237,752) #검토창의 우하단
    speed = 0.55 #기보 넘기는 속도
    least = 23 #일정 수순 이하 기보는 무시
    region = {}
    m = mouse.Controller()
    mouse_left = mouse.Button.left
    
    #'''
    #처음 세팅 받아서 하드코딩 용도.
    #그냥 xy()를 일일이 호출해서 설정하는 게 더 빠를지도...?
    if changxy==1:
        print("default : 0, change : 1")
        changxy = tryint(1,"좌표 변경 : ")
    if changxy == 1:
        print("첫 기보 : ", end = "")
        xy()
        gibo1 = y1
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
        print("6번째 기보 : ", end = "")
        xy()
        gibo6 = y1
        print("숫자 좌상단 : ", end = "")
        xy()
        numx = (x1, y1)
        print("숫자 우하단 : ", end = "")
        xy()
        numy = (x1, y1)
        print("검토 : ", end = "")
        xy()
        gumto = (x1, y1)
        print("좌상단 : ", end = "")
        xy()#left_up
        gumtoLU = (x1,y1)
        print("우하단 : ", end = "")
        xy()#right_down
        gumtoRD = (x1,y1)
    #'''
    
    # 스크린샷 범위
    region = {'top': left_up[1], 'left': left_up[0], 'width': right_down[0] - left_up[0],
        'height': right_down[1] - left_up[1]}
    region2 = {'top': gumtoLU[1], 'left': gumtoLU[0], 'width': gumtoRD[0] - gumtoLU[0],
        'height': gumtoRD[1] - gumtoLU[1]}
    #namera = {'top': namex[1], 'left': namex[0], 'width': namey[0] - namex[0],
        #'height': namey[1] - namex[1]}
    numera = {'top': numx[1], 'left': numx[0], 'width': numy[0] - numx[0],
        'height': numy[1] - numx[1]}
        
    giboname = chkdup(input("생성할 기보의 이름을 입력하세요.").split(", "))
    #pagelist = input("각 기보의 장 수를 입력하세요.").split(", ")
    
    for name in giboname:
        #page = int(pagelist[_])
        if name[0]=='0':
            continue
        num = 1
        m.position = (gibox, gibo1 + giboy*giboname.index(name))
        time.sleep(0.5)
        m.click(mouse_left)
        time.sleep(1)
        capture_screenshot(numera, 'tmpnum.png')
        processed_image = preprocess_image('tmpnum.png')
        cv2.imwrite('tmpnum.png', processed_image)
        page = pytesseract.image_to_string('tmpnum.png',config='--oem 3 --psm 6 outputbase digits')
        page = tryint2(page, least)+1
        if page <= least:
            m.position = goback
            m.click(mouse_left)
            time.sleep(1)
            continue
        title = f"gibo_img/{name}"
        if not(os.path.isdir(title)):
            os.mkdir(os.path.join(title))
        try:
            m.position = gozero
            m.click(mouse_left)
            # 파일 저장
            while num <= page:

                time.sleep(speed)

                # 캡쳐하기
                capture_screenshot(region, f'{title}/img_{str(num).zfill(4)}.png')
                # 검출모드인데 살짝 아쉬움이 있긴 함. (speed가 빠르면 애니메이션으로 인해 검출이 잘 되지 않음.)
                if chkmode(f'{title}/img_{str(num).zfill(4)}.png') == 1:
                    m.position = gumto
                    m.click(mouse_left)
                    time.sleep(1)#화면 전환 대기
                    capture_screenshot(region2, f'{title}/img_{str(num).zfill(4)}.png')
                    m.position = goback
                    m.click(mouse_left)
                    time.sleep(1)#화면 전환 대기
                
                # 페이지 넘기기
                m.position = n_ext
                m.click(mouse_left)

                num += 1

            #print("캡쳐 완료!")
            m.position = goback
            m.click(mouse_left)
            time.sleep(1)
        
        except Exception as e:
            print('예외 발생. ', e)


main()
