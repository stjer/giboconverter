import os
import time
import mss
import cv2
#import mss.tools
#import pyautogui
#import easyocr
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"

from pynput import mouse
#from pynput.keyboard import Key, Controller
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

def tryint2(txt):
    txt = txt.replace('\n','')
    try:
        a = int(txt)
        if 30<a<=200:
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

x1 = 0
y1 = 0

def main(changxy=1):
    
    #reader = easyocr.Reader(['ko','en'])
    #result = reader.readtext(img, detail = 0)
    '''흐름 : 전체 찍고
s= []
for i in result:
    if i.find("단 ")!=-1 or i.find("급 ")!=-1:
        s.append(i)
를 통해서 상대 닉네임들 추출. #승급, 승단시 걸리는지는 아직 ㅁㄹ #승급했다는 걸로 통일되서 출력됨.
걸림. 예시. ['13급 기권', '14급 기권', '14급 기권', '16급 부심', '14급 별간외봉', '시간 전 , 16급 김가네 마작']
하지만 if 0<=i.find("단 ")<=3 or 0<=i.find("급 ")<=3: 으로 바꾸면 걸러짐.
그렇게 하고 보정값(gibo 클릭)을 넣은 게 좋을지 말지는 고민이 됨... detail 부분을 어떻게 처리하면 그런 위치도 나오려나??

이후 gibo1~6을 클릭
숫자 영역 찍고 img = tmp.png 같은 거로 저장.
num = result = reader.readtext(img, detail = 0)[0]
num = tryint2(num)
if num <= 30: 이면 다음 기보로, 아니면 num+=1

'''
    #num = 1
    posX1, posY1, posX2, posY2, posX3, posY3 = 684, 98, 1237, 650, 1109, 679
    numx, numy = (930,655), (980,680)
    #namex = (766,99)
    #namey = (1136, 1020)
    gozero, goback = (714, 683), (716, 66)
    gibo1, gibo6 = 160, 940
    gibox, giboy = 960, (gibo6 - gibo1)//5
    #page = 201
    speed = 0.45
    region = {}
    m = mouse.Controller()
    mouse_left = mouse.Button.left
    #kb_control = Controller()
    if changxy==1:
        print("default : 0, change : 1")
        changxy = tryint(1,"좌표 변경 : ")
    if changxy == 1:
        print("좌상단 : ", end = "")
        xy()#left_up
        posX1, posY1 = x1,y1
        print("우하단 : ", end = "")
        xy()#right_down
        posX2, posY2 = x1,y1
        print("다음 : ", end = "")
        xy()#next
        posX3, posY3 = x1,y1
        print("맨뒤로 : ", end = "")
        xy()#gozero
        gozero = (x1, y1)
        print("뒤로가기 : ", end = "")
        xy()#goback
        goback = (x1, y1)
    # The screen part to capture
    region = {'top': posY1, 'left': posX1, 'width': posX2 - posX1,
        'height': posY2 - posY1}
    #namera = {'top': namex[1], 'left': namex[0], 'width': namey[0] - namex[0],
        #'height': namey[1] - namex[1]}
    numera = {'top': numx[1], 'left': numx[0], 'width': numy[0] - numx[0],
        'height': numy[1] - numx[1]}
    #changp = tryint(1,"페이지 수 변경 : ")
    #if changp == 1:
        #page = tryint(201, "페이지 수 : ")
        
    giboname = chkdup(input("생성할 기보의 이름을 입력하세요.").split(", "))
    #giboname = chkdup(giboname)
    # 이 기능은 num 값을 받아올 수 있는 기능을 구현한 뒤에 적용이 가능함.
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
        page = tryint2(page)+1
        if page <= 30:
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
                # 페이지 넘기기
                m.position = (posX3, posY3)
                m.click(mouse_left)
            

                num += 1

        #print("캡쳐 완료!")
            m.position = goback
            m.click(mouse_left)
            time.sleep(1)
        
        except Exception as e:
            print('예외 발생. ', e)


main()
