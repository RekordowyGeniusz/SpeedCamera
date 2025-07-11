from ultralytics import YOLO
import cv2
import easyocr
import numpy as np
from utils import read_license_plate

#loading licene plate detection model
license_plate_detection_model = YOLO('./models/license_plate_detector.pt')

#loading Reader for reading license plates
reader = easyocr.Reader(['en']) #specifying the language  

#video stuff
video = cv2.VideoCapture('./test_videos/license_plate_view.mp4')
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
fps = int(video.get(cv2.CAP_PROP_FPS))
scale = 0.8

res = True
while res:
    
    res, frame = video.read()

    if res:
        #detecting license plate
        license_plate_detections = license_plate_detection_model(frame)[0]

        for license_plate_detection in license_plate_detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate_detection

            #displaying bounding box of a license plate
            frame = cv2.rectangle(frame, np.uint64((x1, y1)), np.uint64((x2, y2)), (255, 255, 0), 5)

            #preparing image crop for reading
            license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
            license_plate_crop_grayscale = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_grayscale, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

            #license plate threshold visualization
            cv2.imshow('',license_plate_crop_grayscale)

            #reading license plate
            text, confidence = read_license_plate(license_plate_crop_grayscale)
            print(text, confidence)
            #displaying text on window
            position = np.uint64((x1, y1))
            cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)

                    
        #visualization
        smaller_frame = cv2.resize(frame, (0,0), fx=scale, fy=scale)
        cv2.imshow("visualization", smaller_frame)
        if cv2.waitKey(1) == ord('q'):
            break



video.release()
cv2.destroyAllWindows()