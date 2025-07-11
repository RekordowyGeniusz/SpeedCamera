import easyocr
import math

# Defining the EasyOCR reader
reader = easyocr.Reader(['en'], gpu=True)

# funcion for checking if an index exists
def check_index(array, index):
    try:
        array[index]
    except Exception:
        return False
    return True

# function for calculating the closest distance between two points
def euclidean_distance(pt1, pt2):
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

# function for writing the speed measurement results to a file
def write_file(output_path, results, max_velocity=90):
    """
    Write the results to a txt file.

    Args:
        results (dict): Dictionary containing the results of the program to save into a file.
        output_path (str): Path to the output file.
    """

    with open(output_path, 'w', encoding="utf-8") as f:
        
        for car_id in results.keys():
            verdict = "No ticket!"
            percent = results[car_id][2] * 100
            velocity = results[car_id][3] * 3.6

            if velocity > float(max_velocity):
                verdict = "Ticket!"

            f.write("'{}.jpg',\ntravel speed:{} seconds,\nlicense plate number:{},\ntext confidence:{}%,\nvehicle's velocity:{} km/h,\n{}\n".format(car_id, 
                                                                                                                                                results[car_id][0], 
                                                                                                                                                results[car_id][1], 
                                                                                                                                                round(percent, 1), 
                                                                                                                                                round(velocity,2), 
                                                                                                                                                verdict))

        f.close()

# function for reading the license plate
def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """

    detections = reader.readtext(license_plate_crop, allowlist='0123456789ABCDEFGHIJKLMNOPRSTUWZQX ', low_text=0.3, mag_ratio=3, width_ths=100)
    for detection in detections:
        bbox, text, confidence = detection
        text = text.upper()

        if len(text) > 3:
            return text, confidence
    
    return None, None