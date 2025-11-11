# Smart Traffic AI: Adaptive Traffic Light Controller

![Smart Traffic AI running](https://i.imgur.com/example.png)
*(Recommended: Replace this line with a real screenshot of your script running, like `image_158549.png`)*

## 🚀 The Concept

**Smart Traffic AI** is a computer vision project that re-imagines traffic management. Traditional traffic lights run on static, inefficient timers, leading to needless congestion. This project scraps that idea in favor of a "smart," adaptive system.

Using a YOLOv8 object detection model and OpenCV, this system analyzes a live video feed of an intersection. It identifies and counts vehicles in designated "counting zones" (ROIs) and uses that real-time data to make intelligent decisions about which lane should get the green light.

The ultimate goal is to create a fully autonomous, 4-way intersection controller that dynamically adapts to traffic flow, minimizing wait times and clearing congestion.

## ✨ Key Features

* **🧠 Adaptive Timer Logic:** The "brain" of the system. The traffic light's state is not fixed; it is determined by real-time data.
* **🚗 Real-time Vehicle Counting:** A [YOLOv8](https://ultralytics.com/) model detects cars, trucks, buses, and motorcycles on a frame-by-frame basis.
* **🛣️ Custom Counting Zones (ROIs):** You can draw any custom-shaped polygon on the video feed to define exactly where the AI should count vehicles.
* **📊 Live Visual Feedback:** The output window provides a complete visual dashboard, showing:
    * The `GREEN` counting zones (ROIs).
    * `RED` boxes for vehicles *inside* a zone.
    * `BLUE` boxes for vehicles *outside* a zone.
    * A live `Vehicles in ROI: [number]` count.
    * The current "smart" light state (a `RED` or `GREEN` circle) and its active timer.

## 🔮 Full Project Vision (Future Plans)

The current code is a powerful proof-of-concept for a single lane. The final vision is a complete intersection manager.

* [ ] **Full 4-Way Intersection Controller:** The next step is to build a "master brain" (`IntersectionController`) that manages 4 separate `TrafficLightController` instances. This master brain will analyze the queue length from all 4 lanes and decide which lane gets priority, ensuring only one light is green at a time.
* [ ] **Emergency Vehicle Priority:** The model will be trained to detect emergency vehicles (ambulances, police cars). When one is detected, the master controller will give it an immediate green light and turn all other lanes red.
* [ ] **Time-of-Day Adaptation:** The logic will adapt, using different rules for peak rush hour versus late at night.
* [ ] **Improved Custom Model:** The current system uses the generic `yolov8n.pt` model. A key future step is to train a new custom model on a *massive* dataset (thousands of images of rain, snow, night, and day) to create a highly accurate, all-weather "traffic eye."

## 💻 Tech Stack

* **Language:** [Python](https://www.python.org/)
* **AI / Vision:** [Ultralytics YOLOv8](https://ultralytics.com/)
* **Video Processing:** [OpenCV (`opencv-python`)](https://opencv.org/)
* **Math/Arrays:** [NumPy](https://numpy.org/)

## 🏁 How to Run This Project

1.  **Clone the repository:**
    ```bash
    git clone [your-repository-url]
    cd [your-repository-name]
    ```

2.  **Install the required libraries:**
    ```bash
    pip install ultralytics opencv-python numpy
    ```

3.  **Download a Video:**
    * Add any traffic video file (e.g., `my_video.mp4`) to the `TestVideo/` folder.

4.  **Find Your Lane Coordinates (ROI):**
    * Open `roi_selector.py`.
    * Change the `new_video_filename` variable (around line 34) to your video's name (e.g., `'my_video.mp4'`).
    * Run the script: `python roi_selector.py`
    * Click the 4 corners of your desired lane and write down the `(x, y)` coordinates from the terminal.

5.  **Configure the Main Script:**
    * Open `predict.py`.
    * Change the `video_path` variable (around line 19) to your new video file's name.
    * Paste your new coordinates into the `lane_roi = np.array([...])` variable (around line 28).

6.  **Run the Smart Traffic AI!**
    ```bash
    python predict.py
    ```
    A window will pop up showing the smart traffic system in action. Press **'q'** to quit.