import numpy as np
import cv2
import base64
from pathlib import Path


from master import logger


# ---------------------- #
# image based
# ---------------------- #
def convert_jpg_to_base64(roi_file_path, curent_index_value):
    image = cv2.imread(image_path)
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer)

    return jpg_as_text



def convert_base64_to_jpg(jpg_as_text_base64):
    # TODO oytput path
    jpg_original = base64.b64decode(jpg_as_text_base64)
    with open('alfa.jpg', 'wb') as f_out:
        f_out.write(jpg_original)



# ---------------------- #
# numpy array base
# ---------------------- #
def convert_numpy_ndarray_to_base64(numpy_nd_array_logo):
    try:
        obj_base64string = codecs.encode(pickle.dumps(logo, protocol=pickle.HIGHEST_PROTOCOL), "base64")
    except Exception as e:
        logger.debug(str(e))
        return None
    else:
        return obj_base64string



def convert_base64_from_numpy_to_jpg(base64_str):
    try:
        obj_reconstituted = pickle.loads(codecs.decode(base64_str, "base64"))
    except Exception as e:
        logger.debug(str(e))
    else:
        return obj_reconstituted


def extract_logo(image_path, logo_parameters, directory_logos_path):

    # get parameters
    logo_quadrant = logo_parameters['logo_quadrant']
    logo_in_quadrant_location = logo_parameters['logo_in_quadrant_location']


    image = cv2.imread(str(image_path))
    file_name = image_path.name
    h, w, _ = image.shape

    mid_x, mid_y = w // 2, h // 2

    # Extract quadrants
    top_left = image[0:mid_y, 0:mid_x]
    top_right = image[0:mid_y, mid_x:w]
    bottom_left = image[mid_y:h, 0:mid_x]
    bottom_right = image[mid_y:h, mid_x:w]

    # Combine to form halves
    top_half = np.hstack((top_left, top_right))
    bottom_half = np.hstack((bottom_left, bottom_right))
    left_half = np.vstack((top_left, bottom_left))
    right_half = np.vstack((top_right, bottom_right))

    mapper = {
        'top_left' : top_left,
        'top_right' : top_right,
        'bottom_left' : bottom_left,
        'bottom_right' : bottom_right,
        'top_half' : top_half,
        'bottom_half' : bottom_half,
        'left_half' : left_half,
        'right_half' : right_half
    }

    target_area = mapper[logo_quadrant]

    gray = cv2.cvtColor(target_area, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create horizontal rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # sort contours based on logo_in_quadrant_location
    if logo_in_quadrant_location == 'top':
        # first when sorted on y axis
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    elif logo_in_quadrant_location == 'bottom':
        # last when sorted on y axis
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1], reverse=True)
    elif logo_in_quadrant_location == 'left':
        # first when sorted on y axis
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])

    elif logo_in_quadrant_location == 'right':
        # last when sorted on y axis
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0], reverse=True)
    else:
        # not implement or a spelling mistake
        # TODO - defaulting to top case as of now
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    logo = None

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        # if w > relative_width_contour_min and w < relative_width_contour_max and h > layout_logo_height:
        if h > 10:
            cv2.rectangle(target_area, (x, y), (x + w, y + h), (36, 255, 12), 2)
            logo = target_area[y:y+h,x:x+w]
            break

    if logo is not None:
        logger.info('successfully extracted logo')
        # convert to base64 
        retval, buffer = cv2.imencode('.jpg', logo)
        
        logo_as_base64 = base64.b64encode(buffer)
        logo_as_base64_str = logo_as_base64.decode('utf-8')

        # convert back to image and write to file
        jpg_original = base64.b64decode(logo_as_base64)

        logo_out_file_path = directory_logos_path / file_name
        with open(logo_out_file_path, 'wb') as logo_out_handler:
            logo_out_handler.write(jpg_original)

        area_logo_out_file_path = directory_logos_path / f'area_{file_name}'
        cv2.imwrite(str(area_logo_out_file_path), target_area)

        return logo_as_base64_str, str(logo_out_file_path)
    else:
        logger.debug('could not extract logo')
        return None, None


if __name__ == "__main__":
    extract_logo()