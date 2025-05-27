import cv2
import imutils
import numpy as np
from collections import deque
import time
import pyautogui
from threading import Thread

class WebcamVideoStream:
    def __init__(self):
        self.stream = cv2.VideoCapture(1)
        self.ret, self.frame = self.stream.read()
        self.stopped = False
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return
            self.ret, self.frame = self.stream.read()
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True

# HSV color range untuk dua objek warna berbeda
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

blueLower = (100, 150, 0)
blueUpper = (140, 255, 255)

buffer = 20
pts_green = deque(maxlen=buffer)
pts_blue = deque(maxlen=buffer)

counter = 0
direction_green = ''
direction_blue = ''
last_pressed_green = ''
last_pressed_blue = ''
flag = 0

time.sleep(2)
width, height = pyautogui.size()
vs = WebcamVideoStream().start()
pyautogui.click(int(width/2), int(height/2))

# Buat window yang bisa diresize dan set ukuran awal
cv2.namedWindow("Game Control", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Game Control", 960, 720)


def process_color(hsv, lower, upper):
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M['m00'] != 0:
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            if radius > 10:
                return center
    return None

while True:
    frame = vs.read()
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    (h, w) = hsv.shape[:2]
    middle_x = w // 2

    # Potong sisi kiri dan kanan frame
    hsv_left = hsv[:, :middle_x]   # kiri untuk player 1
    hsv_right = hsv[:, middle_x:]  # kanan untuk player 2

    # Deteksi masing-masing warna di sisi area yang sesuai
    center_green = process_color(hsv_left, greenLower, greenUpper)
    center_blue = process_color(hsv_right, blueLower, blueUpper)

    # Tambahkan titik jika terdeteksi
    if center_green is not None:
        pts_green.appendleft(center_green)
    else:
        pts_green.clear()  # Hapus jejak hijau jika objek hilang

    if center_blue is not None:
        # Geser koordinat X karena ini berasal dari sisi kanan
        shifted_center = (center_blue[0] + middle_x, center_blue[1])
        pts_blue.appendleft(shifted_center)
    else:
        pts_blue.clear()  # Hapus jejak biru jika objek hilang


    def detect_direction(pts):
        if counter >= 10 and len(pts) > 10:
            if pts[-10] is not None and pts[1] is not None:
                dX = pts[-10][0] - pts[1][0]
                dY = pts[-10][1] - pts[1][1]
                dirX, dirY = '', ''
                if np.abs(dX) > 50:
                    dirX = 'LEFT' if np.sign(dX) == 1 else 'RIGHT'
                if np.abs(dY) > 50:
                    dirY = 'UP' if np.sign(dY) == 1 else 'DOWN'
                return dirX if dirX else dirY
        return ''


    direction_green = detect_direction(pts_green)
    direction_blue = detect_direction(pts_blue)

    green_key_mapping = {
        'left': 'a',
        'right': 'd',
        'up': 'w',
        'down': 's'
    }

    if direction_green and direction_green.lower() != last_pressed_green:
        pyautogui.press(green_key_mapping[direction_green.lower()])  # Player 1 control remapped
        last_pressed_green = direction_green.lower()
        print(f"Player 1: {direction_green}")


    if direction_blue and direction_blue.lower() != last_pressed_blue:
        pyautogui.press(f"{direction_blue.lower()}")  # Player 2 control (with remapping)
        last_pressed_blue = direction_blue.lower()
        print(f"Player 2: {direction_blue}")


    # Garis pelacakan untuk objek hijau
    for i in range(1, len(pts_green)):
        if pts_green[i - 1] is None or pts_green[i] is None:
            continue
        thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
        cv2.line(frame, pts_green[i - 1], pts_green[i], (0, 255, 0), thickness)

    # Garis pelacakan untuk objek biru
    for i in range(1, len(pts_blue)):
        if pts_blue[i - 1] is None or pts_blue[i] is None:
            continue
        thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
        cv2.line(frame, pts_blue[i - 1], pts_blue[i], (255, 0, 0), thickness)



    # Bagi layar kamera dua sisi
    (h, w) = frame.shape[:2]
    middle_x = w // 2

    # Garis bantu putus-putus vertikal di tengah
    for y in range(0, h, 20):
        if (y // 20) % 2 == 0:
            cv2.line(frame, (middle_x, y), (middle_x, y + 10), (160, 160, 160), 2)

    # Tambahkan teks label sisi kiri dan kanan
    cv2.putText(frame, "Player 1 Area [RED]", (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.putText(frame, "Player 2 Area [BLUE]", (middle_x + 20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2, cv2.LINE_AA)


    cv2.imshow("Game Control", frame)
    counter += 1

    if flag == 0:
        pyautogui.click(int(width/2), int(height/2))
        flag = 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.stop()
cv2.destroyAllWindows()