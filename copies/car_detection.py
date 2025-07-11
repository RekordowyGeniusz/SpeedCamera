from ultralytics import YOLO
import cv2
import easyocr
import numpy as np
from tracker import Tracker
from utils import read_license_plate
import time

#loading car detection model
car_detection_model = YOLO('./models/car_detector.pt')

reader = easyocr.Reader(['en'])

vid_speed_measurement = cv2.VideoCapture('./test_videos/fast.mp4')

scale = 1

#id numbers for: car, motorbike, bus, truck
vehicles_class = [2, 3, 5, 7, 0.0]

#loading Tracker for tracking cars
tracker = Tracker()

#dictionaries for speed measurements
car_speed_measurements = {}
cars_ended_speed_measurement = {}

ret = True

while ret:
    ret, frame_speed_measuerment = vid_speed_measurement.read()

    if not ret:
        print("Plik nie zawiera więcej klatek!")
        break
        
    #detecting a car
    detections = car_detection_model(frame_speed_measuerment)[0]
    detections_ = []

    for detection in detections.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = detection
        w, h = x2 - x1, y2 - y1

        if int(class_id) in vehicles_class:
            detections_.append((([x1, y1, w,h]),class_id, score))


    #assigning ids for each car
    tracking_ids, bboxes = tracker.track(detections_, frame_speed_measuerment) 

    for tracking_id, bbox in zip(tracking_ids, bboxes):
        x1, y1, x2, y2 = bbox

        pt1 = (int(x1), int(y1))
        pt2 = (int(x2), int(y2))

        #visualizing car and its id
        cv2.rectangle(frame_speed_measuerment, pt1, pt2, (0,0,255), 2)
        cv2.putText(frame_speed_measuerment, str(tracking_id), pt1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

    #visualization
    smaller_frame_speed_measurement = cv2.resize(frame_speed_measuerment, (0,0), fx=scale, fy=scale)
    cv2.imshow("visualization1", smaller_frame_speed_measurement)    
    if cv2.waitKey(30) == ord('q'):
        break


vid_speed_measurement.release()
cv2.destroyAllWindows()