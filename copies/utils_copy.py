import string
import easyocr
import re

# Initialize the OCR reader
reader = easyocr.Reader(['en'],gpu=True)

# Mapping dictionaries for character conversion
dict_char_to_int = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}

dict_int_to_char = {'0': 'O',
                    '1': 'I',
                    '3': 'J',
                    '4': 'A',
                    '6': 'G',
                    '5': 'S'}

def write_file(results, output_path, license_plate_detection, track_ids):
    """
    Write the results to a txt file.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output txt file.
    """
    with open(output_path, 'w') as f:
        '''
        structure of a flie.txt:

        it consists of 3 columns:
        1st column - car_id
        2nd column - license plate text
        3rd column - license plate text confidence score
        
        '''

        xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate_detection, track_ids)


        for frame_nmr in results.keys():
            for car_id in frame_nmr.keys():
                if 'car' in results[frame_nmr][car_id].keys() and \
                   'license_plate' in results[frame_nmr][car_id].keys() and \
                   'text' in results[frame_nmr][car_id]['license_plate'].keys():
                    
                    print("idk lmao: ",car_id)
                    f.write('{},{},{}\n'.format(f'{car_id}', 
                                                results[car_id].get('license_plate').get('text'), 
                                                f'{results[car_id].get('license_plate').get('text_confidence')}'))
            
        f.close()

def read_cars_file():
    file_text_ready_to_use = []

    with open('./outputs/file.txt', 'r') as f:

        for line in f:
            line = line.strip()
            file_text_ready_to_use.append(line.split(','))

        f.close()
        
    return file_text_ready_to_use

def get_old_car_from_file(car_id):

    file_text = read_cars_file()
    car = []
    for car_info in file_text:
        if float(car_info[0]) == car_id:
            car = [float(car_info[0]), car_info[1], float(car_info[2])]
            break

    return car

def license_complies_format(text):
    """
    Check if the license plate text complies with the required format.

    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with the format, False otherwise.
    """
    if len(text) != 7:
        return False

    if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char.keys()) and \
       (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char.keys()) and \
       (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in dict_char_to_int.keys()) and \
       (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int.keys()) and \
       (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char.keys()) and \
       (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char.keys()) and \
       (text[6] in string.ascii_uppercase or text[6] in dict_int_to_char.keys()):
        return True
    else:
        return False


def format_license(text):
    """
    Format the license plate text by converting characters using the mapping dictionaries.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text.
    """
    license_plate_ = ''
    mapping = {0: dict_int_to_char, 1: dict_int_to_char, 4: dict_int_to_char, 5: dict_int_to_char, 6: dict_int_to_char,
               2: dict_char_to_int, 3: dict_char_to_int}
    for j in [0, 1, 2, 3, 4, 5, 6]:
        if text[j] in mapping[j].keys():
            license_plate_ += mapping[j][text[j]]
        else:
            license_plate_ += text[j]

    return license_plate_

def check_license(text):
    regex = re.compile('[@_!#$"%^&*()<>?/|\}{~:\']')

    return regex.sub('', text)

def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """

    detections = reader.readtext(license_plate_crop, allowlist ='0123456789ABCDEFGHIJKLMNOPRSTUWZ')
    print(detections)
    for detection in detections:
        bbox, text, confidence = detection
        text = text.upper().replace(' ', '')
        text = check_license(text)

        if len(text) > 3:
            return text, confidence

    return None, None


def get_car(license_plate_detection, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate_detection (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, confidence, class_id = license_plate_detection

    found = False
    for j in range(len(vehicle_track_ids)):
        x_car_1, y_car_1, x_car_2, y_car_2, car_id = vehicle_track_ids[j]

        if (x1 > x_car_1 and y1 > y_car_1) and (x2 < x_car_2 and y2 < y_car_2):
            car_index = j
            found = True
            break

    if found:
        return vehicle_track_ids[car_index]

    return -1, -1, -1, -1, -1