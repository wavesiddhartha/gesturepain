# GesturePaint // ScribbleFlow 🎨🤖

A futuristic, gesture-controlled digital art canvas that lets you paint in the air using your webcam, calibrate your strokes with sub-pixel precision, and collaborate with Kimi AI to transform raw scribbles into clean vector masterpieces.

Designed using the high-contrast **NEXUS cybernetic style system**, this app is optimized for both standalone creative play and integration as a **Virtual Camera** in video call platforms like WhatsApp, Messenger, Zoom, and Google Meet.

---

## 🌟 Core Features

### 1. 👌 Pinch-to-Draw Gesture Engine
* **Intuitive Controls**: Touch your **Thumb and Index finger** together to paint, and separate them to stop drawing and enter **Hover Mode**.
* **Depth-Invariant Calibration**: Gesture detection is normalized against hand scale (wrist-to-knuckle distance). The sensitivity behaves consistently whether you are sitting right up at your webcam or standing across the room.
* **Smart Jitter Stabilization**: Features an **exponential moving average coordinate filter** that eliminates hand-tremor jitters, delivering sleek vector paths.
* **Cursor HUD Feedback Ring**: A glowing outer ring around the cursor dynamically shrinks as your fingers get closer, turning from amber to cyan and displaying `PINCH ACTIVE` when you start drawing.

### 2. 🔮 Kimi AI Redraw & Text Generation
* **Multi-Modal Redraw**: Draw a rough sketch (like a flower or cat) and click **🔮 REDRAW SCRIBBLE** (or press `G`). The app captures your canvas, sends it to the Flask backend running the **`moonshotai/kimi-k2.6`** model, and redraws your scribble as a detailed vector outline.
* **Text-to-Drawing Engine**: Type a prompt (e.g. `butterfly`, `castle`, `spaceship`) in the text box. Kimi AI will solve the prompt (and even solve/render math equations like `2+2=4`) and draw the clean line-art vector version for you.
* **Redraw Animations**: Generated vectors don't just appear—they **animate themselves drawing** onto the canvas in real time using SVG path stroke-dashoffset transitions.

### 3. 📐 Object Edit Mode (Interactive Matrix Transforms)
* Before placing any AI-generated drawing permanently onto your canvas, the app enters **Object Edit Mode**.
* A dotted purple bounding box with grab handles appears around the vector.
* Use the sidebar sliders to **Translate (Move X/Y)**, **Scale (Size)**, and **Rotate (0° - 360°)** the drawing to place it exactly where you want it.

### 4. 🎓 Tracing Guides (Study Mode)
* Perfect for learning how to draw in the air. 
* Select from built-in vector tracing templates (Cute Cat, Spaceship, Coffee Cup, Butterfly) to overlay a low-opacity guide path on your camera stream. Trace over it, clear the guide, and practice your stroke muscle memory!

### 5. 🖥️ Zen Mode (OBS & Stream Friendly)
* Press **`F`** to hide all sidebar menus, header controls, and HUD elements, leaving a clean, fullscreen drawing canvas.
* Connects seamlessly with **OBS Studio's Window Capture** and **Virtual Camera** so you can stream your live air-doodling straight to WhatsApp, Discord, or Zoom.

---

## 🎮 Gesture Quick-Reference

| Gesture | Action | Visual HUD Feedback |
|:---:|:---|:---|
| **👌 Pinch (Index + Thumb)** | **Draw Stroke** | Cyan glowing ring + `PINCH ACTIVE` label |
| **🖐️ Open Hand / Separate Fingers** | **Hover Cursor** | Amber fading ring + `PINCH TO DRAW` label |
| **✌️ Index + Middle Raised** | **Eraser Cursor** | Red circle indicating eraser radius |

---

## 🛠️ Architecture & Tech Stack

* **Frontend**: HTML5 Canvas, Vanilla Javascript, MediaPipe Hands (Browser CDN), and Tailwind-influenced Nexus Dark CSS.
* **Backend**: Flask API (Python) managing CORS headers and routing image payload requests.
* **AI Model**: `moonshotai/kimi-k2.6` via the NVIDIA API (NIM).
* **Virtual Camera Bridge**: OBS Studio Window Capture.

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.9+
* Webcam
* An active internet connection (to stream MediaPipe WASM and call the Kimi AI API)

### 1. Clone & Setup Venv
```bash
git clone https://github.com/wavesiddhartha/gesturepain.git
cd gesturepain

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Requirements include `opencv-python`, `mediapipe`, `numpy`, `flask`, `flask-cors`, and `requests`)*.

### 3. Run the Servers
We provide a unified shell script to start both the Flask backend API (port `5001`) and the static HTTP server (port `8080`):
```bash
chmod +x run.sh
./run.sh
```

Open your web browser and navigate to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 📹 Streaming to WhatsApp / Zoom / Messenger (Virtual Camera)

To show your hand-drawn art to friends or colleagues during a live call:

1. Keep **ScribbleFlow** running in your browser at `http://localhost:8080`.
2. Open **OBS Studio**.
3. Under the **Sources** panel, click **`+`** > **Window Capture** > select your browser window running ScribbleFlow.
4. *(Optional)* Hold the **`Option` (⌥)** key and drag the red bounding box edges in OBS to crop out the sidebar and show only your canvas feed.
5. In OBS, click **Start Virtual Camera** in the bottom-right controls.
6. Open **WhatsApp** or your calling app, go to **Settings** > **Camera**, and select **OBS Virtual Camera** as your webcam input!

---

## ⌨️ Keyboard Shortcuts
* **`C`**: Wipe canvas clean.
* **`F`**: Toggle Zen Mode (Fullscreen, hides UI).
* **`G`**: Redraw current scribble with Kimi AI.
* **`1` - `9`**: Quick-select paint color swatches.
