from ultralytics import YOLO
import os
import cv2
import numpy as np
import time
from traffic_logic import TrafficLightController  


def main():
    model_path = 'yolov8n.pt'
    
    video_path = os.path.join('TestVideo', 'test_video.mp4')

    print(f"Loading model from {model_path}...")
    model = YOLO(model_path)
    print("Model loaded successfully.")

    lane_roi = np.array([
        [394, 366], 
        [486, 358], 
        [499, 717],  
        [209, 713]
    ], np.int32)

    light_controller = TrafficLightController()
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Video opened: {frame_width}x{frame_height} @ {fps} FPS")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Video finished or frame read error.")
            break
            

        results = model(frame, verbose=False) 
        
        vehicle_count_in_roi = 0
        
        for box in results[0].boxes:

            class_id = int(box.cls)
            class_name = model.names[class_id]
            
            if class_name in ['car', 'truck', 'bus', 'motorcycle']:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                is_in_roi = cv2.pointPolygonTest(lane_roi, (center_x, center_y), False) >= 0
                
                if is_in_roi:
                    vehicle_count_in_roi += 1
                    color = (0, 0, 255) 
                else:
                    color = (255, 0, 0) 
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{class_name} {box.conf[0]:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        light_controller.update(vehicle_count_in_roi)
        
        light_color = light_controller.get_state_color()
        timer_display = light_controller.get_timer_display()

        cv2.polylines(frame, [lane_roi], isClosed=True, color=(0, 255, 0), thickness=2)

        cv2.putText(frame, f"Vehicles in ROI: {vehicle_count_in_roi}", 
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
        cv2.circle(frame, (frame_width - 100, 100), 50, light_color, -1)
        
        cv2.putText(frame, str(timer_display), 
                    (frame_width - 125, 115), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

        cv2.imshow("Smart Traffic AI - Press 'q' to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Video processing finished. Resources released.")

if __name__ == "__main__":
    main()