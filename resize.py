import cv2
#from PIL import Image
'''
일단 판만 잘린 상태로 온다는 가정으로 짜인 코드.
본인이 잘 다룰 자신이 있다면 하단에 있는 four point transform 함수를 사용해서 판의 이미지만 가져오는 기능을 추가할 수도 있음.
'''


#def OpenCV2PIL(opencv_image):
#    color_coverted = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
#    pil_image = Image.fromarray(color_coverted)
#    return pil_image

def find_piece(image, template_path, i2=0):
    
    for i in range(0,i2+1):
        
        # 이미지와 템플릿 로드
        template = cv2.imread(template_path[i], cv2.IMREAD_GRAYSCALE)
        
        # 이미지에서 템플릿 매칭 수행
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 매칭된 위치에서 임계값보다 큰 값이 있는지 확인
        threshold = 0.8  # 임계값 (0과 1 사이의 값)
        #print(round(max_val,2), end=" ")#각 값의 매칭률이 궁금하다면 발동
        if max_val > threshold:
            return template_path[i].split("_")[1][0]  # 매칭된 패턴이 있음
        if i == i2:
            return 'm'  # 매칭된 패턴이 없음

def replacem(string, num=9):
    repst = "m"*num
    for i in range(num):
        string = string.replace(repst[:num-i],f"{num-i}")
    return(string)

def save_to_fen_file(content, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"입력된 내용이 '{file_path}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")

def slice_image(fname, piece):
    src = cv2.imread(fname)
    y, x, c = src.shape
    y = 553*y//x
    x = 553

    image = cv2.resize(src, (x,y), interpolation=cv2.INTER_LINEAR)
    for j in range(10):
        for i in range(9):
            #cv2.imwrite(f"tst/test2/{j}_{i}.jpg",image[(j*y//10):(j+1)*y//10, i*x//9:(i+1)*x//9])
            #result = find_piece(cv2.cvtColor(image[(j*y//10):(j+1)*y//10, i*x//9:(i+1)*x//9], cv2.COLOR_RGB2GRAY), piece, 12)
            #print(result, end = " ")
	    result += find_piece(cv2.cvtColor(image[(j*y//10):(j+1)*y//10, i*x//9:(i+1)*x//9], cv2.COLOR_RGB2GRAY), piece, 12)
            
        #print()
        if j!= 9:
	    result += '/'
    if 'k' in result[0:30]:#코드 간결성을 위해 넓은 범위 탐색함..
        result = result[0:30].replace('A','a') + result[30:]
    else :
        result = result[0:-30] + result[-30:].replace('A', 'a')
        result = result[::-1]# 초를 아래로 고정하는 코드.
    resultfen = replacem(result)
    save_to_fen_file(resultfen+" w 0 1", fname.split('.')[0]+'w'+'.fen')
    save_to_fen_file(resultfen+" b 1 1", fname.split('.')[0]+'b'+'.fen')

piece_image_path =[
'icon/resize/icon_A.jpg', #'icon/resize/icon_a2.jpg',
'icon/resize/icon_C.jpg', 'icon/resize/icon_c2.jpg',
'icon/resize/icon_E.jpg', 'icon/resize/icon_e2.jpg', 
'icon/resize/icon_H.jpg', 'icon/resize/icon_h2.jpg', 
'icon/resize/icon_K.jpg', 'icon/resize/icon_k2.jpg', 
'icon/resize/icon_P.jpg', 'icon/resize/icon_p2.jpg', 
'icon/resize/icon_R.jpg', 'icon/resize/icon_r2.jpg'
]

nameen = input("name : ").split(", ")

for _ in range(len(nameen)):
    image_path = f"{nameen[_]}.png"
    slice_image(image_path, piece_image_path)

'''
fname = input("파일명 : ")
try : 
    src = cv2.imread(fname)
    y, x, c = src.shape
    y = 553*y//x
    x = 553

    INTER_LINEAR = cv2.resize(src, (x,y), interpolation=cv2.INTER_LINEAR)
    for j in range(9):
        for i in range(8):
        #cv2.imshow('', INTER_LINEAR[(j*y//10):(j+1)*y//10, i*x//9:(i+1)*x//9])
        #time.sleep(5)

    #cv2.imwrite(fname, INTER_LINEAR)
    #print("변경 완료")
except:
    print("오류")
input()
#cv2.waitKey()
#cv2.destroyAllWindows()
'''

'''
def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped
'''
