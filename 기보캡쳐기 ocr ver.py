import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
                             QDesktopWidget, QTabWidget, QLineEdit, QSlider, QDoubleSpinBox, QMessageBox, QCheckBox, QSpinBox, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pynput import mouse
import time
import mss
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"

from PIL import Image
import numpy as np

class CoordinateListener(QThread):
    coordinate_selected = pyqtSignal(str, int, int)

    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            self.coordinate_selected.emit(self.name, int(x), int(y))
            return False

class CoordinateGetter(QWidget):
    def __init__(self):
        super().__init__()
        self.load_settings()
        self.initUI()
        self.current_listener = None
        self.giboname = ""
        self.speed = 0.55
        self.use_gibo_number = False
        self.gibo_number = 0
        
    def load_settings(self):
        self.coordinate_dict = {
            'left_up': ['판의 좌상단', None],
            'right_down': ['판의 우하단', None],
            'n_ext': ['> 버튼', None],
            'numx': ['숫자(기보 장 수)의 좌상단', None],
            'numy': ['숫자(기보 장 수)의 우하단', None],
            'gozero': ['|<< 버튼', None],
            'goback': ['기보창 나가기', None],
            'gibo1': ['1번째 기보 클릭', None],
            'gibo6': ['6번째 기보 클릭', None],
            'gumto': ['검토 버튼', None],
            'gumtoLU': ['검토창 판의 좌상단', None],
            'gumtoRD': ['검토창 판의 우하단', None]
        }
        if os.path.exists('setting.txt'):
            with open('setting.txt', 'r') as f:
                saved_dict = json.load(f)
                for key, value in saved_dict.items():
                    if key in self.coordinate_dict:
                        self.coordinate_dict[key][1] = tuple(value)

    def save_settings(self):
        save_dict = {k: v[1] for k, v in self.coordinate_dict.items() if v[1] is not None}
        with open('setting.txt', 'w') as f:
            json.dump(save_dict, f)
        QMessageBox.information(self, "저장 완료", "설정이 저장되었습니다.")

    def initUI(self):
        self.setWindowTitle('기보추출기')
        self.setGeometry(300, 300, 500, 700)

        main_layout = QVBoxLayout()
        
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)        
        
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        
        giboname_layout = QHBoxLayout()
        giboname_label = QLabel("기보 명 :")
        self.giboname_input = QLineEdit()
        giboname_layout.addWidget(giboname_label)
        giboname_layout.addWidget(self.giboname_input)
        settings_layout.addLayout(giboname_layout)
        
        speed_layout = QHBoxLayout()
        speed_label = QLabel("속도 간격 :")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(30)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(55)
        self.speed_slider.setTickInterval(5)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.3, 1.5)
        self.speed_spinbox.setSingleStep(0.05)
        self.speed_spinbox.setValue(0.55)
        
        self.speed_slider.valueChanged.connect(self.update_speed_from_slider)
        self.speed_spinbox.valueChanged.connect(self.update_speed_from_spinbox)
        
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_spinbox)
        settings_layout.addLayout(speed_layout)

        gibo_number_layout = QHBoxLayout()
        self.gibo_number_checkbox = QCheckBox("OCR인식이 작동하지 않을 시 사용, 기보의 장 수:")
        self.gibo_number_input = QSpinBox()
        self.gibo_number_input.setRange(0, 200)
        self.gibo_number_input.setEnabled(False)
        
        self.gibo_number_checkbox.stateChanged.connect(self.toggle_gibo_number_input)
        
        gibo_number_layout.addWidget(self.gibo_number_checkbox)
        gibo_number_layout.addWidget(self.gibo_number_input)
        settings_layout.addLayout(gibo_number_layout)
        
        settings_tab.setLayout(settings_layout)
        self.tab_widget.addTab(settings_tab, "실행")

        coord_tab = QWidget()
        coord_layout = QVBoxLayout()
        
        for name, (title, coords) in self.coordinate_dict.items():
            hbox = QHBoxLayout()
            button = QPushButton(f'{title}')
            button.clicked.connect(lambda _, n=name: self.get_coordinate(n))
            hbox.addWidget(button)
            
            label = QLabel('Not set' if coords is None else f'({coords[0]}, {coords[1]})')
            setattr(self, f'{name}_label', label)
            hbox.addWidget(label)
            
            coord_layout.addLayout(hbox)

        coord_tab.setLayout(coord_layout)
        self.tab_widget.addTab(coord_tab, "설정")

        button_layout = QHBoxLayout()
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_main)
        button_layout.addWidget(self.start_button)

        self.save_button = QPushButton('Save Settings')
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

        self.setLayout(main_layout)

    def get_coordinate(self, name):
        if self.current_listener:
            self.current_listener.terminate()
        self.current_listener = CoordinateListener(name)
        self.current_listener.coordinate_selected.connect(self.update_coordinate)
        self.current_listener.start()
        self.showMinimized()

    def update_coordinate(self, name, x, y):
        self.coordinate_dict[name][1] = (x, y)
        label = getattr(self, f'{name}_label')
        label.setText(f'({x}, {y})')
        self.showNormal()
        self.activateWindow()

    def update_speed_from_slider(self, value):
        speed = value / 100
        self.speed_spinbox.setValue(speed)
        self.speed = speed

    def update_speed_from_spinbox(self, value):
        self.speed_slider.setValue(int(value * 100))
        self.speed = value

    def toggle_gibo_number_input(self, state):
        self.gibo_number_input.setEnabled(state == Qt.Checked)

    def start_main(self):
        self.giboname = self.giboname_input.text()
        self.use_gibo_number = self.gibo_number_checkbox.isChecked()
        self.gibo_number = self.gibo_number_input.value()

        if self.use_gibo_number and (self.gibo_number < 0 or self.gibo_number > 200):
            QMessageBox.warning(self, "Invalid Input", "Gibo number must be between 0 and 200.")
            return

        self.run_main()

    def tryint(self, maxn=100, s=""):
        try:
            a = int(input(s))
            if 0 <= a <= maxn or a == -1:
                return a
            else:
                self.log("메뉴에 있는 번호를 선택해 주세요.")
                return self.tryint(maxn, s)
        except ValueError:
            self.log("숫자를 입력해 주세요.")
            return self.tryint(maxn, s)

    def tryint2(self, txt, least=30):
        txt = txt.replace('\n','')
        try:
            a = int(txt)
            if least<a<=200:
                return a
            else :
                self.log(f"범위 외. 입력값 : {a}")
                return 0
        except:
            self.log(f"숫자 인식 불가. 입력값 : {txt}")
            return 0

    def chkdup(self, input_list):
        counts = {}
        for item in input_list:
            counts[item] = counts.get(item, 0) + 1
        
        renamed_list = []
        for item in input_list:
            if counts[item] > 1:
                renamed_list.append(f"{item}_({counts[item]})")
                counts[item] -= 1
            else:
                renamed_list.append(item)
        return renamed_list

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        scale_percent = 300
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        image = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)
        
        _, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        processed_image = cv2.medianBlur(binary_image, 3)
        
        return processed_image

    def capture_screenshot(self, region, output_path):
        with mss.mss() as sct:
            img = sct.grab(region)
            mss.tools.to_png(img.rgb, img.size, output=output_path)

    def chkmode(self, imgP):
        tmpA = cv2.imread("icon/resize/@@@@.png", cv2.IMREAD_GRAYSCALE)
        tmpM = cv2.imread("icon/resize/----2.png", cv2.IMREAD_GRAYSCALE)
        tmpM2 = cv2.imread("icon/resize/----.png", cv2.IMREAD_GRAYSCALE)
        image = np.fromfile(imgP, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)

        result = cv2.matchTemplate(image, tmpA, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.7
        if max_val > threshold:
            self.log("한수쉼 감지")
            return 1
        result = cv2.matchTemplate(image, tmpM, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            self.log("댓글 감지")
            return 1
        result = cv2.matchTemplate(image, tmpM2, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            self.log("댓글 감지")
            return 1
        else :
            return 0

    def run_main(self):
        gibox = (self.coordinate_dict['left_up'][1][0] + self.coordinate_dict['right_down'][1][0]) // 2
        giboy = (self.coordinate_dict['gibo6'][1][1] - self.coordinate_dict['gibo1'][1][1]) // 5
        region = {
            'top': self.coordinate_dict['left_up'][1][1], 
            'left': self.coordinate_dict['left_up'][1][0], 
            'width': self.coordinate_dict['right_down'][1][0] - self.coordinate_dict['left_up'][1][0],
            'height': self.coordinate_dict['right_down'][1][1] - self.coordinate_dict['left_up'][1][1]
        }
        region2 = {
            'top': self.coordinate_dict['gumtoLU'][1][1], 
            'left': self.coordinate_dict['gumtoLU'][1][0], 
            'width': self.coordinate_dict['gumtoRD'][1][0] - self.coordinate_dict['gumtoLU'][1][0],
            'height': self.coordinate_dict['gumtoRD'][1][1] - self.coordinate_dict['gumtoLU'][1][1]
        }
        numera = {
            'top': self.coordinate_dict['numx'][1][1], 
            'left': self.coordinate_dict['numx'][1][0], 
            'width': self.coordinate_dict['numy'][1][0] - self.coordinate_dict['numx'][1][0],
            'height': self.coordinate_dict['numy'][1][1] - self.coordinate_dict['numx'][1][1]
        }

        least = 23
        m = mouse.Controller()
        mouse_left = mouse.Button.left
        giboname = self.chkdup(self.giboname.split(", "))
        
        for name in giboname:
            if name[0]=='0':
                continue
            if self.use_gibo_number:
                self.log(f"Using gibo number: {self.gibo_number}")
                num = 1
                page = self.gibo_number+1
            else:
                num = 1
                m.position = (gibox, self.coordinate_dict['gibo1'][1][1] + giboy*giboname.index(name))
                time.sleep(0.5)
                m.click(mouse_left)
                time.sleep(1)
                self.capture_screenshot(numera, 'tmpnum.png')
                processed_image = self.preprocess_image('tmpnum.png')
                cv2.imwrite('tmpnum.png', processed_image)
                page = pytesseract.image_to_string('tmpnum.png',config='--oem 3 --psm 6 outputbase digits')
                page = self.tryint2(page, least)+1
                if page <= least:
                    m.position = self.coordinate_dict['goback'][1]
                    m.click(mouse_left)
                    time.sleep(1)
                    continue
            title = f"gibo_img/{name}"
            if not(os.path.isdir(title)):
                os.mkdir(os.path.join(title))
            try:
                m.position = self.coordinate_dict['gozero'][1]
                m.click(mouse_left)
                while num <= page:
                    time.sleep(self.speed)
                    self.capture_screenshot(region, f'{title}/img_{str(num).zfill(4)}.png')
                    if self.chkmode(f'{title}/img_{str(num).zfill(4)}.png') == 1:
                        m.position = self.coordinate_dict['gumto'][1]
                        m.click(mouse_left)
                        time.sleep(1)
                        self.capture_screenshot(region2, f'{title}/img_{str(num).zfill(4)}.png')
                        m.position = self.coordinate_dict['goback'][1]
                        m.click(mouse_left)
                        time.sleep(1)
                    m.position = self.coordinate_dict['n_ext'][1]
                    m.click(mouse_left)
                    num += 1
                m.position = self.coordinate_dict['goback'][1]
                m.click(mouse_left)
                time.sleep(1)
            except Exception as e:
                self.log(f'예외 발생. {e}')

    def log(self, message):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoordinateGetter()
    ex.show()
    sys.exit(app.exec_())
