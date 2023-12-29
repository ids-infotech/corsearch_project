import cv2
import fitz
import numpy as np
from pathlib import Path


# def add_white_area_to_top(image_array, height_of_white_area):
#     # Shape of the original image
#     rows, cols, channels = image_array.shape

#     # Create a white area (all pixel values set to 255)
#     white_area = np.ones((height_of_white_area, cols, channels), dtype=image_array.dtype) * 255

#     # Concatenate the white area with the original image
#     new_image_array = np.concatenate((white_area, image_array), axis=0)

#     return new_image_array


def resize_images_to_same_width(images, target_width):
    resized_images = []
    for img in images:
        # Calculate the new height to maintain the aspect ratio
        aspect_ratio = img.shape[0] / img.shape[1]
        new_height = int(target_width * aspect_ratio)

        # Resize the image
        resized_image = cv2.resize(img, (target_width, new_height))
        resized_images.append(resized_image)

    return resized_images


def extend_top_border(image_array, extension_height=100, extension_color=[255, 255, 255]):
    # Create an extension area filled with the specified color
    extension_area = np.ones((extension_height, image_array.shape[1], image_array.shape[2]), 
                             dtype=image_array.dtype) * np.array(extension_color, dtype=image_array.dtype)

    # Concatenate the extension area with the original image
    extended_image = np.concatenate((extension_area, image_array), axis=0)

    return extended_image


def draw_horizontal_line(image_array, y_position, line_color, line_length, line_thickness=1):

    image_array_for_padding = np.copy(image_array)
    # image_array_padded = add_white_area_to_top(image_array_for_padding, 50)
    image_array_padded = extend_top_border(image_array_for_padding)
    image_array_new = np.copy(image_array_padded)
    
    if y_position + line_thickness > image_array_new.shape[0]:
        raise ValueError("Y-position plus line thickness exceeds image height.")
    if line_length > image_array_new.shape[1]:
        raise ValueError("Line length exceeds image width.")

    start_x = (image_array_new.shape[1] - line_length) // 2
    end_x = start_x + line_length

    image_array_new[y_position:y_position + line_thickness, start_x:end_x] = line_color
    return image_array_new



def get_cropped_image(page, header_height: 55, footer_height: None):
    
    # Get the pixmap of the page
    pix = page.get_pixmap()  

    # Access the raw image data directly from the pixmap
    img_data = pix.samples

    # Convert the raw data to a NumPy array
    img_np = np.frombuffer(img_data, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

    # If the image is in CMYK format (4 channels), convert it to BGR
    if pix.n == 4:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_CMYK2BGR)
    
    if footer_height == None:
        cropped_image = img_np[header_height:img_np.shape[0], :]
    else:
        cropped_image = img_np[header_height:footer_height, :]

    return cropped_image


def detect_lines(image, min_line_length = 400):
    image = image
    # Convert image to grayscale
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    
    # Use canny edge detection
    edges = cv2.Canny(gray,50,150,apertureSize=3)
    
    # apply HoughLinesP - probabilistic method to 
    # to directly obtain line end points
    lines_list =[]
    
    lines = cv2.HoughLinesP(
                edges, # Input edge image
                1, # Distance resolution in pixels
                np.pi/180, # Angle resolution in radians
                threshold=100, # Min number of votes for valid line
                minLineLength=min_line_length, # Min allowed length of line
                maxLineGap=1 # Max allowed gap between line for joining them
                )
    
    if lines is not None:
        # Iterate over points
        for points in lines:
            # Extracted points nested in the list
            x1,y1,x2,y2=points[0]
            # Draw the lines joing the points
            # On the original image
            cv2.line(image,(x1,y1),(x2,y2),(0,255,0),2)
            # Maintain a simples lookup list for points
            lines_list.append([(x1,y1),(x2,y2)])
    
    if len(lines_list) > 0:
        return image, lines_list
    else:
        return image, []



def get_rois(bb_image, bb_lines_list):
    
    if len(bb_lines_list) == 0:
        return bb_image, bb_image
    else:
        sorted_lines = sorted(bb_lines_list, key=lambda x: x[0][1])

        rois = []
        # Iterate over the sorted lines to calculate the gap between each line and extract ROIs
        for i in range(len(sorted_lines) - 1):
            # Current line y-coordinate
            _, y1 = sorted_lines[i][0]
            # Next line y-coordinate
            _, y2 = sorted_lines[i + 1][0]
            
            # Define the region of interest between two horizontal lines
            roi = bb_image[y1:y2, :]

            # roi must be greater than 10 pixels in height
            # used to disregard lines themselves being identiied as rois
            if roi.shape[0] > 10:
                # Store the ROI
                rois.append(roi)

        last_line = sorted_lines[-1]
        _, last_line_y = last_line[0]
        area_beyond_last_line = bb_image[last_line_y:, :]

    return rois, area_beyond_last_line



def get_roi_page_top_first_line(bb_image, bb_lines_list):
    if len(bb_lines_list) == 0:
        return bb_image
    else:
        sorted_lines = sorted(bb_lines_list, key=lambda x: x[0][1])

        first_line = sorted_lines[0]
        _, first_line_y = first_line[0]
        area_before_first_line = bb_image[:first_line_y, :]
        
        return area_before_first_line



def main(pdf_path, layout_parameters: dict, output_directory_path: str):
    try:
        doc = fitz.open(str(pdf_path))
    except:
        print('could not read pdf')
        return False, None
    else:

        section_directory = Path(output_directory_path)

        section_directory_page_images = Path.joinpath(section_directory, 'page_images')
        section_directory_page_images.mkdir(parents=True, exist_ok=True)

        section_directory_roi =  Path.joinpath(section_directory, 'rois')
        section_directory_roi.mkdir(parents=True, exist_ok=True)


        for page_number, page in enumerate(doc, start=0):

            print(f'current page: {page_number}')

            if page_number == 0:
                
                current_page_cropped_image = get_cropped_image(page, layout_parameters['target_pages_first']['header_height'], layout_parameters['target_pages_first']['footer_height'])
                current_page_cropped_image = draw_horizontal_line(current_page_cropped_image, 10, [0, 0, 0] , line_length=500, line_thickness=2)
                current_page_with_bb, bb_lines_list = detect_lines(current_page_cropped_image, layout_parameters['horizontal_delimiter_min_width'])

            else:
                current_page_cropped_image = get_cropped_image(page, layout_parameters['target_pages_middle']['header_height'], layout_parameters['target_pages_middle']['footer_height'])
                current_page_with_bb, bb_lines_list = detect_lines(current_page_cropped_image, layout_parameters['horizontal_delimiter_min_width'])

            if len(bb_lines_list) == 0:
                continue
            
            current_page_rois = []
            current_page_perfect_rois, current_page_area_beyond_last_line = get_rois(current_page_with_bb, bb_lines_list)

            current_page_with_bb_img_path = section_directory_page_images / f'{page_number}.jpg'
            cv2.imwrite(str(current_page_with_bb_img_path), current_page_with_bb)

            # cv2.imwrite(f'dev_out/last_area_{page_number}.jpg', current_page_area_beyond_last_line)

            for index, i in enumerate(current_page_perfect_rois):
                if i.shape[1] > i.shape[0]:
                    # cv2.imwrite(f'dev_out/roi_{page_number}_{index}.jpg', i)
                    last_index_this_page = index + 1
                    perfect_roi_path = section_directory_roi / f'{page_number}_{index}.jpg'
                    cv2.imwrite(str(perfect_roi_path), i)


            stacker = []
            stacker.append(current_page_area_beyond_last_line)
            counter = page_number + 1

            while True: # TODO must stop before end of doc
                # get area for next page till the first line

                if counter == doc.page_count:
                    break

                next_page_cropped_image = get_cropped_image(doc[counter], layout_parameters['target_pages_middle']['header_height'], layout_parameters['target_pages_middle']['footer_height'])
                # cv2.imwrite(f'dev_out/NEXTPAGE{page_number+1}.jpg', next_page_cropped_image)

                next_page_with_bb, next_page_bb_lines_list = detect_lines(next_page_cropped_image, layout_parameters['horizontal_delimiter_min_width'])

                if len(next_page_bb_lines_list) == 0:
                    stacker.append(next_page_with_bb)
                    counter = counter + 1
                    continue
                else:
                    next_page_area_before_first_line = get_roi_page_top_first_line(next_page_with_bb, next_page_bb_lines_list)
                    stacker.append(next_page_area_before_first_line)
                    counter = counter + 1
                    break
            
            
            resized_images = resize_images_to_same_width(stacker, target_width=700)
            last_roi_stacked = np.vstack(resized_images)

            # cv2.imwrite(f'dev_out/roi_{page_number}_{last_index_this_page}.jpg', last_roi_stacked)

            try:
                current_page_last_index_roi = section_directory_roi / f'{page_number}_{last_index_this_page}.jpg'
                cv2.imwrite(str(current_page_last_index_roi), last_roi_stacked)
            except:
                pass
            
        return True, section_directory_roi





if __name__ == "__main__":

    pdf_path = 'input_docs/vc/VC20221212-30.pdf'
    output_directory_path = 'dev_test'

    layout_parameters = {
        "nos_columns": 1,
        "is_tabular_format": False,
        "horizontal_delimiter_min_width": 300,
        "target_pages_first": {
            "header_height": 300,
            "footer_height": 750
        },
        "target_pages_last": {
            "header_height": 100,
            "footer_height": 750
        },
        "target_pages_middle": {
            "header_height": 120,
            "footer_height": 750
        }
    }


    main(pdf_path, layout_parameters, output_directory_path)


