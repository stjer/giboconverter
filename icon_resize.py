import os
import json
from PIL import Image

# setting.txt 파일에서 좌표 읽기
with open('setting.txt', 'r') as f:
    settings = json.load(f)

left_up = settings["left_up"]
right_down = settings["right_down"]

# 배율 계산
scale = (left_up[1] - right_down[1]) / 552

# icon/resize 폴더 경로
folder_path = 'icon/resize'

# 폴더 내의 모든 파일에 대해 반복
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        file_path = os.path.join(folder_path, filename)
        
        # 이미지 열기
        with Image.open(file_path) as img:
            # 원본 크기
            original_width, original_height = img.size
            
            # 새로운 크기 계산
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # 이미지 크기 조정
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # 조정된 이미지 저장
            resized_img.save(file_path)

print("모든 이미지의 크기가 조정되었습니다.")
