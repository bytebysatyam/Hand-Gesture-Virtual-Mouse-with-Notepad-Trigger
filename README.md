# Hand Gesture Virtual Mouse with Notepad Trigger

A computer-vision desktop interaction project that uses real-time hand tracking to control mouse actions through webcam gestures.

The application detects hand landmarks with MediaPipe, maps finger coordinates to screen coordinates, smooths cursor movement, and triggers mouse or desktop actions with PyAutoGUI.

## What It Does

- Move the mouse cursor using the index finger
- Left-click using a thumb + index gesture
- Right-click using a thumb + middle-finger gesture
- Scroll up and down using relative index/middle-finger movement
- Open Windows Notepad once after the right-click gesture
- Type a predefined message into Notepad automatically
- Display live hand landmarks through the webcam feed

## Tech Stack

- Python
- OpenCV
- MediaPipe
- NumPy
- PyAutoGUI
- Python `subprocess`

## How It Works

```text
Webcam Feed
    ↓
OpenCV Frame Capture
    ↓
MediaPipe Hand Detection
    ↓
21 Hand Landmarks
    ↓
Index / Thumb / Middle Finger Coordinates
    ↓
Gesture Detection + Coordinate Mapping
    ↓
PyAutoGUI Mouse / Scroll Actions
    ↓
Optional Notepad Trigger
```

### Cursor Movement

The index-finger tip is tracked continuously. Its webcam coordinates are mapped to the current screen resolution using NumPy interpolation.

A smoothing factor is applied before calling `pyautogui.moveTo()` so cursor movement is less abrupt.

### Gesture Mapping

| Gesture | Action |
| --- | --- |
| Move index finger | Move cursor |
| Thumb close to index finger | Left click |
| Thumb close to middle finger | Right click |
| Index above middle finger | Scroll up |
| Index below middle finger | Scroll down |
| First detected right-click gesture | Open Notepad and type a message |

A short click delay is used to reduce repeated click events from a single gesture.

## Project Structure

```text
.
├── handgestures.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.x
- Webcam
- Windows is required for the current Notepad-trigger feature

### Clone the repository

```bash
git clone https://github.com/bytebysatyam/Hand-Gesture-Virtual-Mouse-with-Notepad-Trigger.git
cd Hand-Gesture-Virtual-Mouse-with-Notepad-Trigger
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python handgestures.py
```

Press **Esc** to close the application.

## Main Implementation Details

The current implementation uses:

- MediaPipe detection confidence: `0.7`
- MediaPipe tracking confidence: `0.7`
- Cursor smoothing factor: `5`
- Click delay: `1 second`
- Reduced active frame boundary for screen-coordinate mapping

These constants are defined near the top of `handgestures.py` and can be tuned for different webcams, screen sizes, and user preferences.

## Current Limitations

- The Notepad trigger is Windows-specific.
- Gesture recognition uses simple coordinate thresholds rather than a trained gesture classifier.
- Lighting and webcam quality can affect landmark detection.
- Scroll gestures may be sensitive because they are determined using the relative vertical position of the index and middle fingers.
- Cursor behavior may require tuning for different screen resolutions.

## Possible Improvements

- Add a proper gesture-state machine to prevent accidental actions
- Replace coordinate-only gesture rules with angle/distance-based recognition
- Add configurable gesture mappings
- Add cross-platform application launching
- Add calibration for different users and camera setups
- Add a real recorded demo or GIF
- Add automated tests for gesture helper functions

## Author

**Satyam Shukla**

- GitHub: https://github.com/bytebysatyam
- LinkedIn: https://www.linkedin.com/in/satyamshukla10/
- Portfolio: https://satyam-shukla-portfolio-jet.vercel.app/
- Email: shuklasatyam48890@gmail.com
