from ultralytics import YOLO
import cv2
import numpy as np
from tracker import Tracker
from utils import read_license_plate, write_file, euclidean_distance, check_index
import time

def detection(scale, start1, end1, speed_measurement_length, max_velocity, speed_measurement_path, license_plate_path):

    #loading car detection model
    car_detection_model = YOLO('./models/car_detector.pt')
    license_plate_detection_model = YOLO('./models/license_plate_detector.pt')

    #loading the videos
    vid_speed_measurement = cv2.VideoCapture(speed_measurement_path)
    vid_license_plate = cv2.VideoCapture(license_plate_path)

    lp_vid_height, lp_vid_width = int(vid_license_plate.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(vid_license_plate.get(cv2.CAP_PROP_FRAME_WIDTH))

    #id numbers for: car, motorbike, bus, truck, etc.
    vehicles_class = [2, 3, 5, 7, 0.0]

    #loading Tracker for tracking cars
    tracker1 = Tracker()
    tracker2 = Tracker()

    #dictionaries
    car_speed_measurements = {}
    cars_ended_speed_measurement = {}
    license_plate_info = {}
    info_to_save = {}

    ret = True
    while ret:
        #reading the video's frames
        ret, frame_speed_measurement = vid_speed_measurement.read()
        ret, frame_license_plate = vid_license_plate.read()

        # if there's an error while reading a file
        if not ret:
            print("The video file has ended or an error occurred during loading of the file")
            break
            
        # detecting vehicles
        detections = car_detection_model(frame_speed_measurement)[0]
        detections_ = []

        # preaparing data for tracking vehicles
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            w, h = x2 - x1, y2 - y1
            
            if int(class_id) in vehicles_class:
                detections_.append((([x1, y1, w,h]),class_id, score))

        # assigning ids for each vehicle
        tracking_ids, bboxes = tracker1.track(detections_, frame_speed_measurement) 

        # detecting license plates
        detections_license_plate = license_plate_detection_model(frame_license_plate)[0]
        lp_detections_ = []

        # prepring data for tracking license plate detections
        for license_plate_detection in detections_license_plate.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate_detection
            w, h = x2 - x1, y2 - y1

            lp_detections_.append((([x1, y1, w,h]), class_id, score))

        # assigning ids for each license plate
        lp_tracking_ids, lp_bboxes = tracker2.track(lp_detections_, frame_license_plate) 

        # applying ANPR system
        for lp_tracking_id, lp_bbox in zip(lp_tracking_ids, lp_bboxes):
                x1, y1, x2, y2 = lp_bbox
                
                # preparing image crop for reading text on a license palte
                license_plate_crop = frame_license_plate[int(y1):int(y2), int(x1):int(x2), :]

                # checking if license plate crop has any data in it
                if x1 > 0 and x2 > 0 and y1 > 0 and y2 > 0 and len(license_plate_crop) != 0:
                    # displaying bounding box of a license plate
                    frame_license_plate = cv2.rectangle(frame_license_plate, np.uint64((x1, y1)), np.uint64((x2, y2)), (255, 255, 0), 5)

                    license_plate_crop_grayscale = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                    _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_grayscale, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                    # visualizing thresholding output
                    cv2.imshow('License plate detection', license_plate_crop_thresh)

                    # reading license plate text
                    text, confidence = read_license_plate(license_plate_crop_thresh)

                    if text is not None:
                        
                        # updating license plate readings
                        if lp_tracking_id not in license_plate_info or license_plate_info[lp_tracking_id][1] < float(confidence):
                            # it switches the reading values of the license plate with lower confidence scores
                            license_plate_info[lp_tracking_id] = [text, 
                                                                float(confidence), 
                                                                [float(x1), float(x2), float(y1), float(y2)], 
                                                                license_plate_crop.copy()]

                        # visualizing the license plat edetection
                        position = np.uint64((x1, y1))
                        cv2.putText(frame_license_plate, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)


        # applying the speed measurement calculations and other stuff
        for tracking_id, bbox in zip(tracking_ids, bboxes):
            x1, y1, x2, y2 = bbox

            pt1 = (int(x1), int(y1))
            pt2 = (int(x2), int(y2))

            #visualizing car and its id
            cv2.rectangle(frame_speed_measurement, pt1, pt2, (0,0,255), 2)
            cv2.putText(frame_speed_measurement, str(tracking_id), pt1, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            
            #visualizing speed measurement threshold lines
            cv2.rectangle(frame_speed_measurement, start1[0], start1[1], (255,255,0), 2)
            cv2.rectangle(frame_speed_measurement, end1[0], end1[1], (255,0,255), 2)

            # checking if a vehicle has passed the speed measurement starting threshold line
            if x1 >= start1[0][0] and x2 <= start1[1][0] and y1 >= start1[0][1] and y2 >= start1[1][1] and tracking_id not in car_speed_measurements:
                if not (x1 >= end1[0][0] and x2 <= end1[1][0] and y1 >= end1[0][1] and y2 >= end1[1][1]):
                    # taking a snapshot of time and saving it for later calculations
                    start_counting_time = time.time() 
                    car_speed_measurements[tracking_id] = [start_counting_time, "", 0.0]

            # checking if a vehicle has passed the speed measurement ending threshold line
            ids_to_remove = []
            if x1 >= end1[0][0] and x2 <= end1[1][0] and y1 >= end1[0][1] and y2 >= end1[1][1] and tracking_id in car_speed_measurements:
                
                # calculating the center of the vehicle
                car_x_center = (0 + lp_vid_width) / 2
                car_y_center = lp_vid_height

                pt1 = (car_x_center, car_y_center)

                # connecting the vehicle to the license plate recognition
                distances = []
                for lp_key in license_plate_info.keys():
                    text, confidence, bboxes, lp_crop = license_plate_info[lp_key]
                    lp_x1, lp_x2, lp_y1, lp_y2 = bboxes
                    
                    # calculating the center of the license plate
                    lp_x_center = (lp_x1 + lp_x2) / 2
                    lp_y_center = (lp_y1 + lp_y2) / 2     

                    pt2 = (lp_x_center, lp_y_center)

                    # calculating the distance between the center of the vehicle and the license plate center
                    distance = euclidean_distance(pt1, pt2)   

                    if distance < 0:
                        distance = euclidean_distance(pt2, pt1) 

                    # choosing the most fitting license plate data
                    distances.append([lp_key, text, confidence, distance, lp_crop])
                    
                    closest_detection = min(distances, key=lambda x: x[3])

                # preparing data of speed measurement and saving it for later usage
                ids_to_remove.append(closest_detection[0])
                end_counting_time = time.time()
                time_ = end_counting_time - car_speed_measurements[tracking_id][0]
                if check_index(license_plate_info, closest_detection[0]):
                    cars_ended_speed_measurement[tracking_id] = [float(str(time_)[:4]), 
                                                                closest_detection[1], 
                                                                license_plate_info[closest_detection[0]][1],
                                                                closest_detection[4]]
        
            # saving data of speed measurement to a file
            if cars_ended_speed_measurement != {}:
                for tracking_id in cars_ended_speed_measurement.keys():
                    # calculating the vehicles speed
                    car_velocity = (speed_measurement_length / cars_ended_speed_measurement[tracking_id][0])

                    # saving data that is to be saved to a file
                    info_to_save[tracking_id] = [cars_ended_speed_measurement[tracking_id][0], 
                                                cars_ended_speed_measurement[tracking_id][1], 
                                                round(cars_ended_speed_measurement[tracking_id][2], 3), 
                                                round(car_velocity, 2)]

                # saving the data
                cv2.imwrite(f"./outputs/{tracking_id}.jpg", cars_ended_speed_measurement[tracking_id][3])
                write_file("./outputs/file.txt", info_to_save, max_velocity)

                #deleting the cars from dictionaries after the speed measurement
                for lp_id in ids_to_remove:
                    license_plate_info.pop(lp_id)

                car_speed_measurements.clear()
                cars_ended_speed_measurement.clear()

        # displaying the fps for each camera
        speed_measurement_fps = vid_speed_measurement.get(cv2.CAP_PROP_FPS)
        license_plate_fps = vid_license_plate.get(cv2.CAP_PROP_FPS)
        cv2.putText(frame_speed_measurement, f"FPS: {int(speed_measurement_fps)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.putText(frame_license_plate, f"FPS: {int(license_plate_fps)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        # visualization
        smaller_frame_speed_measurement = cv2.resize(frame_speed_measurement, (0,0), fx=scale, fy=scale)
        smaller_frame_license_plate = cv2.resize(frame_license_plate, (0,0), fx=scale, fy=scale)
        cv2.imshow("Speed Measurement", smaller_frame_speed_measurement)    
        cv2.imshow("License Plate", smaller_frame_license_plate)    

        # after pressing 'q' key on the keyboard the program ends and exits
        if cv2.waitKey(1) == ord('q'):
            break

    # releasing the memory resources
    vid_speed_measurement.release()
    vid_license_plate.release()
    cv2.destroyAllWindows()