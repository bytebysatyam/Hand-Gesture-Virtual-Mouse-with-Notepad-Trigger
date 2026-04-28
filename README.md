# 🖐️ Hand Gesture Virtual Mouse with Notepad Trigger

## 📌 Description

This project allows users to control the computer mouse using hand gestures captured through a webcam. It uses computer vision techniques to detect hand landmarks and converts them into mouse actions such as cursor movement, clicking, scrolling, and application triggering.

---

## 🚀 Features

* 🖱️ Cursor control using index finger
* 👆 Left click (Thumb + Index gesture)
* 👉 Right click (Thumb + Middle gesture)
* 🔄 Scroll up/down using finger movement
* 📝 Automatic Notepad opening using gesture
* 🎯 Smooth and stable cursor movement

---

## 🛠️ Tech Stack

* Python
* OpenCV
* MediaPipe
* NumPy
* PyAutoGUI

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python hand_gesture.py
```

---

## 🎥 Demo

(Add your demo video or GIF here)

---

## 📚 Working Principle

* MediaPipe detects 21 hand landmarks
* Specific landmarks (thumb, index, middle fingers) are tracked
* Distance between landmarks is calculated to detect gestures
* Coordinates are mapped to screen resolution
* PyAutoGUI performs mouse operations

---

## ⚠️ Limitations

* Requires good lighting conditions
* Accuracy decreases with fast hand movement
* Background noise may affect detection

---

## 🔮 Future Scope

* Add gesture-based keyboard typing
* Add voice commands
* Improve accuracy using AI models
* Cross-platform support (Linux/Mac)

---

## 👨‍💻 Author

Satyam Shukla
