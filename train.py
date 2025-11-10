from ultralytics import YOLO

def main():

    model = YOLO('yolov8s.pt')

    print("Starting model training...")
    results = model.train(
        data='VehiclesDetectionDataset/dataset.yaml', 
        epochs=25,         
        imgsz=640,         
        project='runs',     
        name='traffic_detector_run1' 
    )
    print("Training finished!")
    print(f"Model saved to: {results.save_dir}")

if __name__ == '__main__':
    main()