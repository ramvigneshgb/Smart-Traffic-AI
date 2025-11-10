import os
import cv2

def click_event(event, x, y, flags, params):
    """
    Callback function to capture mouse clicks.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Point clicked: (x={x}, y={y})")
        
        frame = params['frame']
        
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        cv2.imshow("Select ROIs - Click points, press 'q' to quit", frame)

def main():
    """
    Main function to load the video, read the first frame,
    and wait for user clicks.
    """
    print("Click on the image to get coordinates.")
    print("Imagine you are drawing polygons for each lane.")
    print("Press 'q' to close the window.")
    
    new_video_filename = 'Test_Video.mp4' 
    
    video_path = os.path.join('TestVideo', new_video_filename)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    success, frame = cap.read()
    if not success:
        print(f"Error: Could not read the first frame from {video_path}")
        cap.release()
        return
        
    print("Video frame loaded. Please click on the window.")

    params = {'frame': frame}

    window_name = "Select ROIs - Click points, press 'q' to quit"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_event, params)


    cv2.imshow(window_name, frame)

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("ROI selector finished.")

if __name__ == "__main__":
    main() 