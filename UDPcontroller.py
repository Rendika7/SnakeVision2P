import cv2
import imutils
import numpy as np
from collections import deque
import time
import socket
from threading import Thread

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_ADDRESS = ('localhost', 9999)

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

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
blueLower = (100, 150, 0)
blueUpper = (140, 255, 255)

buffer = 20
pts_green = deque(maxlen=buffer)
pts_blue = deque(maxlen=buffer)

counter = 0

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

def detect_direction(pts, counter):
    if counter >= 10 and len(pts) > 10:
        if pts[-10] is not None and pts[1] is not None:
            dX = pts[-10][0] - pts[1][0]
            dY = pts[-10][1] - pts[1][1]
            dirX, dirY = '', ''
            if np.abs(dX) > 50:
                dirX = 'left' if np.sign(dX) == 1 else 'right'
            if np.abs(dY) > 50:
                dirY = 'up' if np.sign(dY) == 1 else 'down'
            return dirX if dirX else dirY
    return ''

vs = WebcamVideoStream().start()
time.sleep(2)

while True:
    frame = vs.read()
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    (h, w) = hsv.shape[:2]
    middle_x = w // 2

    hsv_left = hsv[:, :middle_x]
    hsv_right = hsv[:, middle_x:]

    center_green = process_color(hsv_left, greenLower, greenUpper)
    center_blue = process_color(hsv_right, blueLower, blueUpper)

    if center_green is not None:
        pts_green.appendleft(center_green)
        # Gambar lingkaran hijau di posisi center objek hijau
        cv2.circle(frame, center_green, 15, (0, 255, 0), 2)
    else:
        pts_green.clear()

    if center_blue is not None:
        shifted_center = (center_blue[0] + middle_x, center_blue[1])
        pts_blue.appendleft(shifted_center)
        # Gambar lingkaran biru di posisi center objek biru (dengan offset)
        cv2.circle(frame, shifted_center, 15, (255, 0, 0), 2)
    else:
        pts_blue.clear()

    direction_green = detect_direction(pts_green, counter)
    direction_blue = detect_direction(pts_blue, counter)

    if direction_green:
        msg = f"player1:{direction_green}"
        sock.sendto(msg.encode(), SERVER_ADDRESS)
        print(f"Sent: {msg}")

    if direction_blue:
        msg = f"player2:{direction_blue}"
        sock.sendto(msg.encode(), SERVER_ADDRESS)
        print(f"Sent: {msg}")

    # Gambar garis jejak untuk objek hijau
    for i in range(1, len(pts_green)):
        if pts_green[i - 1] is None or pts_green[i] is None:
            continue
        thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
        cv2.line(frame, pts_green[i - 1], pts_green[i], (0, 255, 0), thickness)

    # Gambar garis jejak untuk objek biru
    for i in range(1, len(pts_blue)):
        if pts_blue[i - 1] is None or pts_blue[i] is None:
            continue
        thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
        cv2.line(frame, pts_blue[i - 1], pts_blue[i], (255, 0, 0), thickness)

    # Garis bantu vertikal pemisah kamera kiri & kanan
    for y in range(0, h, 20):
        if (y // 20) % 2 == 0:
            cv2.line(frame, (middle_x, y), (middle_x, y + 10), (160, 160, 160), 2)

    # Label area player 1 dan 2
    cv2.putText(frame, "Player 1 Area [Green]", (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.putText(frame, "Player 2 Area [Blue]", (middle_x + 20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 0, 0), 2, cv2.LINE_AA)

    cv2.imshow("Controller", frame)
    counter += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.stop()
cv2.destroyAllWindows()
sock.close()