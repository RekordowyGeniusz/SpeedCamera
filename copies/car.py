from ultralytics import YOLO
import cv2
from tracker import Tracker
import time

#loading car detection model
car_detection_model = YOLO('./models/yolov8n.pt')

#loading the video
video = cv2.VideoCapture('./test_videos/top_down.mp4')

#scaling the video
scale = 1

#id numbers for: car, motorbike, bus, truck
vehicles_class = [2, 3, 5, 7]

#loading Tracker for tracking cars
tracker = Tracker()

#dictionaries for speed measurements
car_speed_measurements = {}
cars_ended_speed_measurement = {}

ret = True
while ret:
    ret, frame = video.read()

    if not ret:
        break
        
    #detecting a car
    detections = car_detection_model(frame)[0]
    detections_ = []

    for detection in detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = detection
        w, h = x2 - x1, y2 - y1
        
        if int(class_id) in vehicles_class:
            detections_.append((([x1, y1, w,h]),class_id, score))

    #assigning ids for each car
    tracking_ids, bboxes = tracker.track(detections_, frame) 
    
    for tracking_id, bbox in zip(tracking_ids, bboxes):
        x1, y1, x2, y2 = bbox

        pt1 = (int(x1), int(y1))
        pt2 = (int(x2), int(y2))

        #visualizing car and its id
        cv2.rectangle(frame, pt1, pt2, (0,0,255), 2)
        cv2.putText(frame, str(tracking_id), pt1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

        #speed measurement
        start = [(170,370), (270,370)]
        end = [(150,700), (340,700)]
        
        #visualizing speed measurement thresholds
        cv2.line(frame, start[0], start[1], (255,255,0), 2)
        cv2.rectangle(frame, end[0], end[1], (255,0,255), 2)

        #start of speed measurement
        if x1 >= start[0][0] and x2 <= start[1][0] and y1 >= start[0][1] and y2 >= start[1][1] and tracking_id not in car_speed_measurements:
            start_counting_time = time.time() 
            car_speed_measurements[tracking_id] = start_counting_time

        #end of speed measurement
        if x1 >= end[0][0] and x2 <= end[1][0] and y1 >= end[0][1] and y2 >= end[1][1] and tracking_id in car_speed_measurements:
            end_counting_time = time.time()
            time_ = end_counting_time - car_speed_measurements[tracking_id]
            cars_ended_speed_measurement[tracking_id] = str(time_)[:4]
        
    print(cars_ended_speed_measurement)

    #visualization
    smaller_frame = cv2.resize(frame, (0,0), fx=scale, fy=scale)
    cv2.imshow("visualization", smaller_frame)
    if cv2.waitKey(35) == ord('q'):
        break


video.release()
cv2.destroyAllWindows()