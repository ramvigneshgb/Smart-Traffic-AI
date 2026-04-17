import cv2
import numpy as np
from ultralytics import YOLO
from traffic_logic import TrafficLightController
import os

# --- CONFIGURATION ---
# Check if you have a trained model from your 'runs' folder, otherwise use default
custom_model_path = "runs/detect/train/weights/best.pt"
MODEL_PATH = custom_model_path if os.path.exists(custom_model_path) else "yolov8n.pt"
VIDEO_PATH = "TestVideo/Test_Video.mp4"

# --- VISUALS ---
BLUE = (50, 50, 50)  # Dark Background
TEXT_COLOR = (255, 255, 255)

# --- GLOBAL VARS ---
roi_points = []
drawing = False

def draw_roi_event(event, x, y, flags, params):
    """Mouse callback to define the polygon zone."""
    global roi_points
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_points.append((x, y))

def is_inside_roi(box_center, polygon):
    result = cv2.pointPolygonTest(polygon, box_center, False)
    return result >= 0

def draw_dashboard(frame, controller, vehicle_count, is_emergency):
    """Draws a professional Dark Mode UI overlay."""
    h, w, _ = frame.shape
    
    # 1. Glassmorphism Background (Top Right)
    overlay = frame.copy()
    cv2.rectangle(overlay, (w - 350, 0), (w, 180), (20, 20, 20), -1)
    alpha = 0.8
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # 2. Status Light Indicator
    color = controller.get_state_color() # (B, G, R)
    status_text = "PRIORITY" if is_emergency else controller.state
    
    # Draw glowing light
    cv2.circle(frame, (w - 300, 60), 25, color, -1)
    if is_emergency:
        cv2.circle(frame, (w - 300, 60), 30, (0, 0, 255), 2) # Extra ring for emergency
    else:
        cv2.circle(frame, (w - 300, 60), 27, (255, 255, 255), 2) # White rim

    # 3. Text Info
    timer_val = controller.get_timer_display()
    
    cv2.putText(frame, f"STATUS: {status_text}", (w - 260, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, TEXT_COLOR, 2)
    cv2.putText(frame, f"TIME: {timer_val}s", (w - 260, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
    cv2.putText(frame, f"VEHICLES: {vehicle_count}", (w - 260, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

def main():
    print(f"[INFO] Loading Model: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(VIDEO_PATH)
    controller = TrafficLightController()
    
    # --- STEP 1: DEFINE ROI ---
    ret, first_frame = cap.read()
    if not ret:
        print("[ERROR] Cannot read video.")
        return

    cv2.namedWindow("Select Lane")
    cv2.setMouseCallback("Select Lane", draw_roi_event)
    
    print("[INFO] Click 4 points to define the lane. Press 'SPACE' to start.")
    while True:
        temp_frame = first_frame.copy()
        if len(roi_points) > 0:
            pts = np.array(roi_points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(temp_frame, [pts], True, (0, 255, 255), 2)
            
        cv2.imshow("Select Lane", temp_frame)
        if cv2.waitKey(1) == 32 and len(roi_points) > 2: # Space bar
            break
    
    cv2.destroyWindow("Select Lane")
    polygon = np.array(roi_points, np.int32)

    # --- STEP 2: MAIN LOOP ---
    while True:
        ret, frame = cap.read()
        if not ret: 
            break
            
        # Detect
        results = model(frame, stream=True)
        
        vehicle_count = 0
        emergency_detected = False

        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Get Class ID
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                
                # Check for Emergency Vehicle (Customize 'ambulance' string if needed)
                if "ambulance" in label.lower() or "police" in label.lower() or "fire" in label.lower():
                    emergency_detected = True
                    color = (0, 0, 255) # Red Box
                elif cls_id in [2, 3, 5, 7]: # Car, Bike, Bus, Truck
                    color = (0, 255, 0) # Green Box
                else:
                    continue # Skip detection if it's not a vehicle

                # Box Coords
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Check ROI
                if is_inside_roi((cx, cy), polygon):
                    vehicle_count += 1
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Update Brain
        controller.update(vehicle_count, is_emergency=emergency_detected)
        
        # Draw Visuals
        cv2.polylines(frame, [polygon], True, (0, 255, 255), 2)
        draw_dashboard(frame, controller, vehicle_count, emergency_detected)
        
        cv2.imshow("Smart Traffic AI", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()