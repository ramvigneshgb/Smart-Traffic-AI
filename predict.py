from ultralytics import YOLO
import cv2
import numpy as np
from traffic_logic import IntersectionController  

def main():
    model = YOLO('yolov8n.pt') 
    master_controller = IntersectionController()

    camera_feeds = {
        "North": "TestVideo/north_cam.mp4",
        "South": "TestVideo/south_cam.mp4",
        "East":  "TestVideo/east_cam.mp4",
        "West":  "TestVideo/west_cam.mp4"
    }

    caps = {}
    for lane, path in camera_feeds.items():
        caps[lane] = cv2.VideoCapture(path)

    rois = {
        "North": np.array([[100, 200], [500, 200], [600, 400], [50, 400]], np.int32),
        "South": np.array([[100, 200], [500, 200], [600, 400], [50, 400]], np.int32),
        "East":  np.array([[100, 200], [500, 200], [600, 400], [50, 400]], np.int32),
        "West":  np.array([[100, 200], [500, 200], [600, 400], [50, 400]], np.int32)
    }

    print("System Online. Monitoring for Traffic Flow and Accidents...")

    while True:
        current_counts = {"North": 0, "South": 0, "East": 0, "West": 0}
        current_accidents = {"North": False, "South": False, "East": False, "West": False}
        frames_for_display = {}

        for lane, cap in caps.items():
            success, frame = cap.read()
            if not success:
                continue 

            results = model(frame, verbose=False)
            
            for box in results[0].boxes:
                class_name = model.names[int(box.cls)]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Verify object is inside the lane ROI
                if cv2.pointPolygonTest(rois[lane], (center_x, center_y), False) >= 0:
                    
                    # 1. Standard Vehicle Counting
                    if class_name in ['car', 'truck', 'bus', 'motorcycle']:
                        current_counts[lane] += 1
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    
                    # 2. Accident Detection Override
                    elif class_name == 'accident':
                        current_accidents[lane] = True
                        # Draw a thick, highly visible Orange box around the crash
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 5)
                        cv2.putText(frame, "CRASH DETECTED", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 3)

            # Draw HUD
            light_color = master_controller.get_state_color(lane)
            cv2.polylines(frame, [rois[lane]], True, (0, 255, 255), 2)
            cv2.putText(frame, f"State: {master_controller.states[lane]}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, light_color, 2)
            cv2.putText(frame, f"Queue: {current_counts[lane]}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # If blocked, flash a big warning on that camera feed
            if current_accidents[lane]:
                cv2.putText(frame, "LANE BLOCKED", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 4)

            frames_for_display[lane] = cv2.resize(frame, (640, 480))

        # Feed counts AND accident reports to the Master Brain
        master_controller.update(current_counts, current_accidents)

        if len(frames_for_display) == 4:
            top_row = np.hstack((frames_for_display["North"], frames_for_display["South"]))
            bottom_row = np.hstack((frames_for_display["East"], frames_for_display["West"]))
            dashboard = np.vstack((top_row, bottom_row))
            
            cv2.putText(dashboard, f"Active ({master_controller.active_lane}): {master_controller.get_timer_display()}s", 
                        (500, 480), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            
            cv2.imshow("Smart Traffic Control Center", dashboard)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for cap in caps.values():
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()