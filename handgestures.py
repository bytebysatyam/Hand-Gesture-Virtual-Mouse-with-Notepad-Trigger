import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import subprocess
import time

SMOOTHENING = 5
CLICK_DELAY = 1
FRAME_REDUCTION = 100


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)

prev_x, prev_y = 0, 0
last_click_time = 0
app_opened = False


def get_screen_coordinates(x, y, w, h):
    screen_x = np.interp(x, (FRAME_REDUCTION, w - FRAME_REDUCTION), (0, screen_w))
    screen_y = np.interp(y, (FRAME_REDUCTION, h - FRAME_REDUCTION), (0, screen_h))
    return screen_x, screen_y


def smooth_movement(curr_x, curr_y, prev_x, prev_y):
    new_x = prev_x + (curr_x - prev_x) / SMOOTHENING
    new_y = prev_y + (curr_y - prev_y) / SMOOTHENING
    return new_x, new_y


def is_close(x1, y1, x2, y2, threshold=20):
    return abs(x1 - x2) < threshold and abs(y1 - y2) < threshold



while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Landmarks
            lm = hand_landmarks.landmark

            index = lm[8]
            thumb = lm[4]
            middle = lm[12]

            ix, iy = int(index.x * w), int(index.y * h)
            tx, ty = int(thumb.x * w), int(thumb.y * h)
            mx, my = int(middle.x * w), int(middle.y * h)

            # Cursor Movement
            screen_x, screen_y = get_screen_coordinates(ix, iy, w, h)
            curr_x, curr_y = smooth_movement(screen_x, screen_y, prev_x, prev_y)

            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            current_time = time.time()

            # LEFT CLICK (Thumb + Index)
            if is_close(tx, ty, ix, iy):
                if current_time - last_click_time > CLICK_DELAY:
                    pyautogui.click()
                    last_click_time = current_time
                    print("Left Click")

            # RIGHT CLICK (Thumb + Middle)
            elif is_close(tx, ty, mx, my):
                if current_time - last_click_time > CLICK_DELAY:
                    pyautogui.rightClick()
                    last_click_time = current_time
                    print("Right Click")

                    # Open Notepad once
                    if not app_opened:
                        subprocess.Popen(['notepad.exe'])
                        time.sleep(1)
                        pyautogui.write("Gesture Controlled Notepad Opened!", interval=0.05)
                        app_opened = True

            # SCROLL (Index up/down relative to middle)
            elif iy < my:
                pyautogui.scroll(20)
                print("Scroll Up")

            elif iy > my:
                pyautogui.scroll(-20)
                print("Scroll Down")

    cv2.imshow("Virtual Mouse", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()