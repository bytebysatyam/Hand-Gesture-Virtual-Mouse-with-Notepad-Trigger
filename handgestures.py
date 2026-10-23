import platform
import subprocess
import time

import cv2
import mediapipe as mp
import numpy as np
import pyautogui

from gesture_logic import classify_gesture

SMOOTHENING = 5
CLICK_DELAY = 0.75
SCROLL_DELAY = 0.20
FRAME_REDUCTION = 100
SCROLL_AMOUNT = 5

pyautogui.FAILSAFE = True
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


def get_screen_coordinates(x: int, y: int, w: int, h: int) -> tuple[float, float]:
    x_min = min(FRAME_REDUCTION, max(0, w // 3))
    y_min = min(FRAME_REDUCTION, max(0, h // 3))
    x_max = max(x_min + 1, w - x_min)
    y_max = max(y_min + 1, h - y_min)

    clipped_x = min(max(x, x_min), x_max)
    clipped_y = min(max(y, y_min), y_max)

    screen_x = np.interp(clipped_x, (x_min, x_max), (0, screen_w))
    screen_y = np.interp(clipped_y, (y_min, y_max), (0, screen_h))
    return float(screen_x), float(screen_y)


def smooth_movement(curr_x: float, curr_y: float, prev_x: float, prev_y: float) -> tuple[float, float]:
    new_x = prev_x + (curr_x - prev_x) / SMOOTHENING
    new_y = prev_y + (curr_y - prev_y) / SMOOTHENING
    return new_x, new_y


def open_notepad_once() -> None:
    if platform.system() != "Windows":
        print("Notepad trigger skipped: this feature is Windows-only.")
        return

    subprocess.Popen(["notepad.exe"])
    time.sleep(0.7)
    pyautogui.write("Gesture Controlled Notepad Opened!", interval=0.04)


def main() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError(
            "Could not open webcam. Check camera permissions, close other camera apps, and try again."
        )

    prev_x, prev_y = screen_w / 2, screen_h / 2
    last_click_time = 0.0
    last_scroll_time = 0.0
    app_opened = False

    try:
        with mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        ) as hands:
            while True:
                success, frame = cap.read()
                if not success:
                    print("Webcam frame could not be read. Exiting.")
                    break

                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(rgb_frame)

                action = "none"

                if result.multi_hand_landmarks:
                    hand_landmarks = result.multi_hand_landmarks[0]
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    lm = hand_landmarks.landmark

                    thumb = (lm[4].x, lm[4].y)
                    index_tip = (lm[8].x, lm[8].y)
                    index_pip = (lm[6].x, lm[6].y)
                    middle_tip = (lm[12].x, lm[12].y)
                    middle_pip = (lm[10].x, lm[10].y)
                    wrist = (lm[0].x, lm[0].y)
                    middle_mcp = (lm[9].x, lm[9].y)

                    action = classify_gesture(
                        thumb=thumb,
                        index_tip=index_tip,
                        index_pip=index_pip,
                        middle_tip=middle_tip,
                        middle_pip=middle_pip,
                        wrist=wrist,
                        middle_mcp=middle_mcp,
                    )

                    current_time = time.time()

                    if action == "move":
                        ix, iy = int(index_tip[0] * w), int(index_tip[1] * h)
                        screen_x, screen_y = get_screen_coordinates(ix, iy, w, h)
                        curr_x, curr_y = smooth_movement(screen_x, screen_y, prev_x, prev_y)
                        pyautogui.moveTo(curr_x, curr_y, duration=0)
                        prev_x, prev_y = curr_x, curr_y

                    elif action == "left_click" and current_time - last_click_time >= CLICK_DELAY:
                        pyautogui.click()
                        last_click_time = current_time

                    elif action == "right_click" and current_time - last_click_time >= CLICK_DELAY:
                        pyautogui.rightClick()
                        last_click_time = current_time

                        if not app_opened:
                            open_notepad_once()
                            app_opened = True

                    elif action == "scroll_up" and current_time - last_scroll_time >= SCROLL_DELAY:
                        pyautogui.scroll(SCROLL_AMOUNT)
                        last_scroll_time = current_time

                    elif action == "scroll_down" and current_time - last_scroll_time >= SCROLL_DELAY:
                        pyautogui.scroll(-SCROLL_AMOUNT)
                        last_scroll_time = current_time

                cv2.putText(
                    frame,
                    f"Action: {action}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    frame,
                    "ESC to exit | Move: index only | Click: thumb+index | Right: thumb+middle",
                    (20, max(60, h - 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

                cv2.imshow("Virtual Mouse", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
