from PIL import Image
import os
import shutil
import cv2
import matplotlib.pyplot as plt
import numpy as np
import re

def PIL2OpenCV(pil_image):
    numpy_image= np.array(pil_image)
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    return opencv_image

def target(folder_path="gibo_img"):
    # 주어진 경로의 모든 파일 목록 얻기
    files = os.listdir(folder_path)
    st = []
    # 파일 목록 출력
    print("폴더 내 파일 목록:")
    for file in files:
        if file[0] != "_":
            print(file, end=', ')
            st.append(file)
    print('')
    return st

def convert2pychess(fen):#liground 유저용
    fen = fen.replace(['w ', 'b ', 'H', 'h', 'E', 'e'],['w - - ', 'b - - ', 'N', 'n', 'B', 'b'])
    return fen

def slice_image(image_path, rows, columns):
    # 이미지 열기
    img = Image.open(image_path)
    width, height = img.size

    # 잘라낼 이미지의 크기 계산
    slice_width = width // columns
    slice_height = height // rows

    slices = []
    for row in range(rows):
        for col in range(columns):
            # 잘라낼 영역의 좌표 계산
            left = col * slice_width
            upper = row * slice_height
            right = left + slice_width
            lower = upper + slice_height

            # 이미지 잘라내기
            slice_img = img.crop((left, upper, right, lower))
            slices.append(slice_img)

    return slices

def find_piece(image, template_path, i2=0):
    #image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    for i in range(0,i2+1):
        
        # 이미지와 템플릿 로드
        template = cv2.imread(template_path[i], cv2.IMREAD_GRAYSCALE)

        # 이미지에서 템플릿 매칭 수행
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 매칭된 위치에서 임계값보다 큰 값이 있는지 확인
        threshold = 0.8  # 임계값 (0과 1 사이의 값)
        if max_val > threshold:
            return template_path[i].split("_")[1][0]  # 매칭된 패턴이 있음
        if i == i2:
            return 'm'  # 매칭된 패턴이 없음

def replacem(string, num=9):
    repst = "m"*num
    for i in range(num):
        string = string.replace(repst[:num-i],f"{num-i}")
    return(string)

def delete_folder(folder_path):
    # 해당 경로에 있는 폴더 삭제
    try:
        shutil.rmtree(folder_path)
        print(f"폴더 '{folder_path}'와 내부의 모든 파일이 삭제되었습니다.")
    except FileNotFoundError:
        print(f"폴더 '{folder_path}'를 찾을 수 없습니다.")
    except OSError as e:
        print(f"폴더와 파일 삭제 중 오류가 발생했습니다: {e}")

def create_folder(folder_path):
    # 해당 경로에 폴더 생성
    try:
        os.mkdir(folder_path)
        print(f"폴더 '{folder_path}'가 생성되었습니다.")
    except FileExistsError:
        delete_folder(folder_path)# 폴더 삭제 함수 호출
        print(f"폴더 '{folder_path}'를 재생성합니다.")
        create_folder(folder_path)
    except Exception as e:
        print(f"폴더 생성 중 오류가 발생했습니다: {e}")

def count_files_in_directory(st=[]):
    print("0을 입력시, 탐색된 폴더 전체를 변환합니다. 폴더 앞에 _를 붙이면 탐색에서 제외됩니다.")
    fpl = input("폴더 경로 : ").split(", ")
    if fpl == ['0']:
        fpl = st
    #fpl = folder_path_list
    for i in range(len(fpl)):
        try:
            files = os.listdir("gibo_img/"+fpl[i])
            fpl[i] = [fpl[i], len(files)]
        except FileNotFoundError:
            print(f"폴더 '{fpl}'를 찾을 수 없습니다.")
        except Exception as e:
            print(f"파일 개수 세기 중 오류가 발생했습니다: {e}")
    return fpl, len(fpl)

def save_file(content, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"입력된 내용이 '{file_path}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")

def find_changed_positions(old_fen, new_fen):
    changed_positions = []
    old_rows = old_fen.split()[0].split('/')
    new_rows = new_fen.split()[0].split('/')
    for i in range(len(old_rows)):
        for j in range(len(old_rows[i])):
            if old_rows[i][j] != new_rows[i][j]:
                changed_positions.append((i, j, new_rows[i][j]))
    return changed_positions

def convert_to_pgn(cp):
    abc = 'abcdefghi'
    if cp[1][2] == 'm':
        pgn = abc[cp[1][1]]+ str(9-cp[1][0]) + abc[cp[0][1]] + str(9-cp[0][0])
    elif cp[0][2] == 'm':
        pgn = abc[cp[0][1]]+ str(9-cp[0][0]) + abc[cp[1][1]] + str(9-cp[1][0])
    else :
        print("catch", end='')
        print(cp)
    return pgn

def convert_to_gib(cp):
    if cp[1][2] == 'm':
        gib = str((cp[1][0]+1)%10) + str(cp[1][1]+1) +cp[0][2].upper() + str((cp[0][0]+1)%10) + str(cp[0][1]+1)
    elif cp[0][2] == 'm':
        gib = str((cp[0][0]+1)%10) + str(cp[0][1]+1) +cp[1][2].upper() + str((cp[1][0]+1)%10) + str(cp[1][1]+1)
    return en2ko(gib)

def en2ko(gib):
    en = 'ACEHKPR'
    ko = '사포상마장졸차'
    for i in range(len(en)):
        gib = gib.replace(en[i],ko[i])
    return gib

def restorem(string, num=9):
    for i in range(1,num+1):
        repst = "m"*i
        string = string.replace(f'{i}',repst)
    return(string)

def gib_position(cp):
    cp = cp.lower().replace("eh","상마").replace("he","마상")
    kostr = re.sub(r"[^ㄱ-ㅣ가-힣]","",cp) # 한글만 남기기
    cp = f'[초차림 "{kostr[4:]}"]\n[한차림 "{kostr[:4]}"]'
    return cp


chk = 1
save = 0
tmp = ''
save = int(input("1.fen 저장\n저장하지 않고 진행\n : "))
chk = int(input("1. pgn\n2. gib\n12. 둘 다\n"))

while chk==1 or chk==2 or chk==12:

    st = target()
    name, fpnum = count_files_in_directory(st)
    for _ in range(fpnum):
        nameen = name[_][0].split('\\')[-1]
        num = name[_][1]
        Opgn = '[Variant "janggicasual"]\n[VariantFamily "janggi"]\n'
        Ogib = ''
    
        create_folder(f"tst/{nameen}")
        if save == 1:
        
            create_folder(f"tst/{nameen}/fen")
        
        for i in range(1,num+1):

            # 이미지 파일 경로 설정
            image_path = f"gibo_img/{nameen}/img_{str(i).zfill(4)}.png"    
            # 잘라낼 행과 열의 수 설정
            rows = 10
            columns = 9

            # 이미지 잘라내기 함수 호출
            sliced_images = slice_image(image_path, rows, columns)

            piece_image_path =[
            'icon/resize/icon_P.jpg', 'icon/resize/icon_p2.jpg', 
            'icon/resize/icon_A.jpg', #'icon/resize/icon_a2.jpg',
            'icon/resize/icon_C.jpg', 'icon/resize/icon_c2.jpg',
            'icon/resize/icon_E.jpg', 'icon/resize/icon_e2.jpg', 
            'icon/resize/icon_H.jpg', 'icon/resize/icon_h2.jpg', 
            'icon/resize/icon_R.jpg', 'icon/resize/icon_r2.jpg',
            'icon/resize/icon_K.jpg', 'icon/resize/icon_k2.jpg'
            ]

            # 잘라낸 이미지들을 저장
            originfen = ''
        
            for i2, image in enumerate(sliced_images):
                originfen += find_piece(cv2.cvtColor(PIL2OpenCV(image), cv2.COLOR_RGB2GRAY), piece_image_path, 12)
                if (i2+2)%9 == 1 and i2!=89:
                    originfen+="/"
            if 'k' in originfen[0:30]:#코드 간결성을 위해 넓은 범위 탐색함..
                originfen = originfen[0:30].replace('A','a') + originfen[30:]
            else :
                originfen = originfen[0:-30] + originfen[-30:].replace('A', 'a')
                originfen = originfen[::-1]# 초를 아래로 고정하는 코드.
        
            if i==1:
                tmp = originfen
                if chk == 1 or chk ==12:
                    Opgn += f'[FEN "{replacem(originfen)} w 0 1"]'
                if chk == 2 or chk ==12:
                    Ogib += gib_position(tmp)
        
            if tmp == originfen and i!=1:
                pgn = '@@@@'
                gib = '한수쉼'
                if i%2 != 1:
                    Opgn += f'\n{i//2}.'
                Opgn += ' ' + pgn
                Ogib += f'\n{(i-1)}. {gib}'
            elif i!=1:
                changed_positions = find_changed_positions(tmp, originfen)
                if chk == 1 or chk ==12:
                    pgn = convert_to_pgn(changed_positions)
                if chk == 2 or chk ==12:
                    gib = convert_to_gib(changed_positions)
                if chk == 1 or chk ==12:
                    if i%2 != 1:
                        Opgn += f'\n{i//2}.'
                    Opgn += ' ' + pgn
                if chk == 2 or chk ==12:
                    Ogib += f'\n{(i-1)}. {gib}'
            tmp = originfen
            
            if save ==1:#fen 파일 저장. 
            
                resultfen = replacem(originfen)
                if i%2 == 1:
                    resultfen += " w 0 1"
                else :
                    resultfen += " b 1 1"
                #resultfen = convert2pychess(resultfen) #liground 유저는 각주해제해서 쓰세요.
                fen_save_path = f"tst/{nameen}/fen/fen_{str(i).zfill(4)}.fen"
                save_file(resultfen, fen_save_path)
            else:
                print(f"\r{str(i).zfill(len(str(num)))}/{num}", end='')
        print()
        if chk == 1 or chk ==12:
            save_file(Opgn, f"tst/{nameen}/{nameen}.pgn")
        if chk == 2 or chk ==12:
            save_file(Ogib, f"tst/{nameen}/{nameen}.gib")
    chk = int(input("\n\n1, 2, 12 : 다른 파일 나누기(pgn, gib)\nelse : 종료\n"))
    
