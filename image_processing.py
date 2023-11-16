import cv2
import json
import pdfplumber
import fitz
import os
import base64
from PIL import Image
import re
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\nitika.s\AppData\Local\Programs\Tesseract-OCR"



# for image folder
def create_image_folder(pdf_file_path):
    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
    # Creating a folder name based on the PDF file name
    output_folder = f"{pdf_filename}_images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder


# Define a function to process a page and return its text and page number
def process_page(page):
    page_text = page.get_text("text")
    return page_text, page.number

def correct_text_segmentation(content_data, delimiter):
    corrected_data = []
    for page_text in content_data:
        # Split the text using the delimiter
        split_texts = page_text['text'].split(delimiter)

        # The first part goes to the current page
        corrected_data.append({
            'text_on_page': page_text['text_on_page'],
            'text': split_texts[0]
        })

        # If there's more content after the split, it goes to the next page
        # Remove the 'delimiter +' from the following line to exclude the heading when saving to the JSON
        if len(split_texts) > 1:
            corrected_data.append({
                'text_on_page': page_text['text_on_page'] + 1,
                'text': split_texts[1]
            })
    return corrected_data


def merge_duplicate_pages(content_data):
    # Create a dictionary to store consolidated texts
    consolidated_data = {}

    for entry in content_data:
        page_num = entry["text_on_page"]
        text = entry["text"].strip()  # Remove any leading/trailing white spaces
        
        # Skip the entry if the text is empty
        if not text:
            continue

        if page_num not in consolidated_data:
            consolidated_data[page_num] = text
        else:
            # Add a space before appending the next text
            consolidated_data[page_num] += " " + text

    # Convert the consolidated data dictionary back to a list format
    merged_data = [{"text_on_page": k, "text": v} for k, v in consolidated_data.items()]
    
    # Optionally, sort the list by 'text_on_page' if needed
    merged_data.sort(key=lambda x: x["text_on_page"])

    return merged_data



def preprocess_image(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to enhance 
    _, thresholded_image = cv2.threshold(
        gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Further noise reduction using morphological transformations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_image = cv2.morphologyEx(
        thresholded_image, cv2.MORPH_CLOSE, kernel)

    return processed_image




'''def define_coordinates_from_pdf(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
    print(extracted_text_json_path,"47---------")
    
    # Load the JSON file containing the previously extracted text (if it exists)
    try:
        with open(extracted_text_json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        # Handle the case where the file is not found
        print("[-] Existing file not found")
        return
    except Exception as e:
        # Handle other exceptions (e.g., file read errors) and print the error message
        print(e,"--------------59")
        return

    # Extract text from the PDF and store it in extracted_text_dict
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize variables to store the minimum and maximum coordinates
        min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

        # Iterate through each page in the PDF
        for page_number, page in enumerate(pdf.pages, start=1):
            # Initialize a dictionary to store extracted text for the current page
            extracted_text_dict[str(page_number)] = {
                "page_number": page_number,
                "extracted_texts": []
            }
            # print("[*] page number:", page_number)
            print("74----------------------")

            # Retrieve the current page (0-based index)
            page = pdf.pages[page_number - 1]  # Pages are 0-based index

            # Extract words from the page with their bounding box coordinates
            words_with_bounding_box = page.extract_words()
            print("81------------")

            # Initialize a dictionary to group words into lines based on y-coordinates
            lines = {}
            for word in words_with_bounding_box:
                # Round y-coordinate to handle floating-point inaccuracies
                y0 = round(word["top"], 2)
                y1 = round(word["bottom"], 2)
                if (y0, y1) in lines:
                    # Append word data to an existing line
                    lines[(y0, y1)]["text"].append(word["text"])
                    lines[(y0, y1)]["x0"].append(word["x0"])
                    lines[(y0, y1)]["x1"].append(word["x1"])
                else:
                    # Create a new line entry
                    lines[(y0, y1)] = {
                        "text": [word["text"]],
                        "x0": [word["x0"]],
                        "x1": [word["x1"]],
                    }

            # Sort lines by y-coordinates
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])
            print("105-----------")

            # Iterate through existing data entries
            for page_data_key, page_data in existing_data.items():
                # Skip this entry if it has no 'content_data'
                if not page_data.get("content_data"):
                    continue
                print("112")

                # Iterate through content entries for the current page
                for content_entry in page_data["content_data"]:
                    # Get the start and end patterns
                    start = content_entry["text"][0]
                    end = content_entry["text"][-1]
                    print("118")
                    

                    # Initialize a flag to track if a match is found
                    match = False

                    # Initialize variables to calculate the minimum and maximum coordinates
                    min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

                    # Iterate through sorted lines
                    for (y0, y1), line_info in sorted_lines:
                        text = " ".join(line_info["text"])

                        if match:
                            # to get the maximum coordinates of the text
                            # determine the smallest x0 and y0 coordinates (the top-left corner) and 
                            # largest x1 and y1 coordinates (the bottom-right corner) for a text block
                            # These are then used to calculate the overall coordinates for the entire text extracted between the "start" and "end" patterns.
                            min_x0 = min(min_x0, min(line_info["x0"]))
                            min_y0 = min(min_y0, y0)
                            max_x1 = max(max_x1, max(line_info["x1"]))
                            max_y1 = max(max_y1, y1)

                         # Compare text to the start pattern
                        start_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in start.split(" ") if i]

                        # Mark a match when the start pattern is found
                        if start_found and not match:
                            match = True

                        # Compare text to the end pattern
                        end_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in end.split(" ") if i]

                        if end_found and match:
                            # Add the extracted text and its coordinates to the dictionary
                            extracted_text_dict[str(page_number)]["extracted_texts"].append({
                                "extracted_text": content_entry['text'],
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1,
                            })
                            # Print a message indicating that the text has been successfully extracted
                            match = False
                            print("[+] extracted the text => ",
                                  '\n'.join(content_entry['text']), "\n")

                            # Update the content_data entry with coordinates
                            content_entry["coordinates"] = {
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1
                            }
                            break'''

def define_coordinates_from_pdf(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
    print(extracted_text_json_path,"47---------")
    # Load the JSON file containing the previously extracted text (if it exists)
    try:
        with open(extracted_text_json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        print("[-] Exiting file not found")
        return
    except Exception as e:
        print(e)
        return

    # Extract text from the PDF and store it in extracted_text_dict
    with pdfplumber.open(pdf_path) as pdf:

        min_x0, min_y0, max_x1, max_y1 = float('inf'), float(
            'inf'), -float('inf'), -float('inf')

        for page_number, page in enumerate(pdf.pages, start=1):

            extracted_text_dict[str(page_number)] = {
                "page_number": page_number, "extracted_texts": []}

            page = pdf.pages[page_number-1]  # Pages are 0-based index

            # Extract words with bounding box coordinates
            words_with_bounding_box = page.extract_words()

            # Group words into lines based on y-coordinates
            lines = {}
            for word in words_with_bounding_box:
                # Round y-coordinate to handle floating-point inaccuracies
                y0 = round(word["top"], 2)
                y1 = round(word["bottom"], 2)
                if (y0, y1) in lines:
                    lines[(y0, y1)]["text"].append(word["text"])
                    lines[(y0, y1)]["x0"].append(word["x0"])
                    lines[(y0, y1)]["x1"].append(word["x1"])
                else:
                    lines[(y0, y1)] = {
                        "text": [word["text"]],
                        "x0": [word["x0"]],
                        "x1": [word["x1"]],
                    }

            # Sort lines by y-coordinates
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])

            for i, v in existing_data.items():

                # extracting the key and text from the pages based on final.json
                if not v.get("content"):
                    continue

                # extracting the start and end sentences of the content to be serahced
                start = v["content"][0]
                end = v["content"][-1]

                match = False

                min_x0, min_y0, max_x1, max_y1 = float('inf'), float(
                    'inf'), -float('inf'), -float('inf')

                for (y0, y1), line_info in sorted_lines:
                    text = " ".join(line_info["text"])

                    if match:
                        # to get the maximum coordinates of the text
                        min_x0 = min(min_x0, min(line_info["x0"]))
                        min_y0 = min(min_y0, y0)
                        max_x1 = max(max_x1, max(line_info["x1"]))
                        max_y1 = max(max_y1, y1)

                    # comparing texts
                    start_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                        i.replace("\n", '').lower() for i in start.split(" ") if i]

                    if start_found and not match:
                        match = True
                        min_x0 = min(min_x0, min(line_info["x0"]))
                        min_y0 = min(min_y0, y0)
                        max_x1 = max(max_x1, max(line_info["x1"]))
                        max_y1 = max(max_y1, y1)

                    # comparing texts
                    end_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                        i.replace("\n", '').lower() for i in end.split(" ") if i]

                    if end_found and match:
                        min_x0 = min(min_x0, min(line_info["x0"]))
                        min_y0 = min(min_y0, y0)
                        max_x1 = max(max_x1, max(line_info["x1"]))
                        max_y1 = max(max_y1, y1)

                        temp_dict = {
                            "extracted_text": v.get("content"),
                            "x0": min_x0,
                            "y0": min_y0,
                            "x1": max_x1,
                            "y1": max_y1,
                        }

                        match = False

                        temp_dict["logo"] = {}

                        # find the text-based logo
                        logo = ""
                        middle = (min_x0 + max_x1) // 2

                        cur_min_x0, cur_min_y0, cur_max_x1, cur_max_y1 = min_x0, min_y0, max_x1, max_y1

                        min_x0, min_y0, max_x1, max_y1 = float('inf'), float(
                            'inf'), -float('inf'), -float('inf')

                        for (y0, y1), line_info in sorted_lines:
                            if min(line_info["x0"]) >= middle and max(line_info["x1"]) <= cur_max_x1 and y0 >= cur_min_y0 and y1 <= cur_max_y1:
                                logo += "".join(line_info["text"])
                                min_x0 = min(min_x0, min(line_info["x0"]))
                                min_y0 = min(min_y0, y0)
                                max_x1 = max(max_x1, max(line_info["x1"]))
                                max_y1 = max(max_y1, y1)

                        # extracting the text based logo
                        if logo:
                            # removing characters within curly braces in the logo

                            logo = re.sub(r"\(.*?\)|:", " ", logo).strip()

                            if logo:
                                temp_dict["logo"]["text_logo"] = {
                                    "logo": logo,
                                    "x0": min_x0,
                                    "y0": min_y0,
                                    "x1": max_x1,
                                    "y1": max_y1,

                                }

                        # FINDING IMAGE LOGOS
                        # image logos will be avilable on the right part of the section, so we check the images starting from the middle of the section

                        cropped_page = page.crop(
                            (cur_min_x0//2, cur_min_y0, cur_max_x1, cur_max_y1))

                        page_height = page.height

                        if len(cropped_page.images):
                            temp_dict["logo"]["image_logo"] = []

                            for j, img in enumerate(cropped_page.images):

                                image_bbox = (img['x0'], page_height - img['y1'],
                                              img['x1'], page_height - img['y0'])

                                cropped_page = page.crop(image_bbox)

                                temp_dict["logo"]["image_logo"].append({
                                    "x0": img['x0'],
                                    "y0": page_height - img['y0'],
                                    "x1": img['x1'],
                                    "y1": page_height - img['y1'],

                                })

                        extracted_text_dict[str(
                            page_number)]["extracted_texts"].append(temp_dict)

                        break

                    

    # print(json.dumps(extracted_text_dict, indent=4))
    json.dumps(extracted_text_dict, indent=4)
    # Save the defined coordinates to a new JSON file with formatting
    with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
        # with open("output.json", "w", encoding="utf-8") as output_json_file:
        json.dump(extracted_text_dict, output_json_file,
                  indent=4, separators=(',', ': '))
        # Save the modified JSON file with coordinates added

        
    # with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
    #     json.dump(existing_data, json_file, indent=4, separators=(',', ': '))

    # # Save the defined coordinates to a new JSON file with formatting
    # with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
    #     json.dump(extracted_text_dict, output_json_file, indent=4, separators=(',', ': '))

        


def extract_text_from_image(image_path):
    processed_image = preprocess_image(image_path)

    # Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(processed_image)

    print("Text from image is", "bad" if not text else "good")
    return text


# output ---> corrdinates into the final json file


def extract_and_save_image(pdf_file, coordinates_file, output_folder, resolution=200):
    padding = 5
    if True:
        # try:
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Open the PDF file
        pdf_document = fitz.open(pdf_file)
        pdf_document_pdf_plumber = pdfplumber.open(pdf_file)
        # Load coordinates from the JSON file
        with open(coordinates_file, "r") as json_file:
            coordinates_data = json.load(json_file)
        # Initialize a list to store extracted image data for each page
        extracted_images_per_page = {}
        for key, entry in coordinates_data.items():
            page_number = entry["page_number"]
            for i, text in enumerate(entry["extracted_texts"]):
                x0 = text["x0"] - padding
                y0 = text["y0"] - padding
                x1 = text["x1"] + padding
                y1 = text["y1"] + padding
                page = pdf_document[page_number - 1]
                rect = fitz.Rect(x0, y0, x1, y1)
                image = page.get_pixmap(
                    matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect
                )
                # SAVE THE EXTRACTED IMAGE
                image_filename = os.path.join(
                    output_folder, f"page_{page_number}_section_{i}.png")
                image.save(image_filename)
                print(f"Extracted image saved as {image_filename}")
                # Now, convert the PNG image to GIF format using Pillow
                gif_filename = os.path.join(
                    output_folder, f"page_{page_number}_section_{i}.gif")
                image_pil = Image.open(image_filename)
                image_pil.save(gif_filename, "GIF")
                print(f"Converted PNG to GIF: {gif_filename}")
                # Encode the image as a base64 string
                with open(image_filename, "rb") as image_file:
                    base64_image = base64.b64encode(
                        image_file.read()).decode('utf-8')
                # Get just the filename without the path
                base_filename = os.path.basename(image_filename)
                # Create a dictionary with the base filename as the key and base64 data as the value
                image_data = {
                    base_filename: base64_image,
                }
                # Save the base64 data in a JSON file
                base64_filename = os.path.join(
                    output_folder, f"page_{page_number}_section_{i}.json")
                with open(base64_filename, "w") as json_file:
                    json.dump(image_data, json_file, indent=4)
                # Append the base64 data to the original coordinates_data
                text["base64"] = base64_image

                
                # FINDING THE LOGO COORDINARTES AND EXTRACTING THE LOGO

                if text.get("logo", None):
                    logo_bbox = text["logo"].get("text_logo", None)

                    if logo_bbox is not None:

                        rect = fitz.Rect(
                            logo_bbox["x0"], logo_bbox["y0"], logo_bbox["x1"], logo_bbox["y1"])
                        image = page.get_pixmap(
                            matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect
                        )
                        # SAVE THE EXTRACTED TEXT LOGO
                        image_filename = os.path.join(
                            output_folder, f"page_{page_number}_section_{i}_logo.png")
                        image.save(image_filename)
                        print(
                            f"Extracted image logo saved as {image_filename}")

                        # Now, convert the PNG image to GIF format using Pillow
                        gif_filename = os.path.join(
                            output_folder, f"page_{page_number}_section_{i}_logo.gif")
                        image_pil = Image.open(image_filename)
                        image_pil.save(gif_filename, "GIF")
                        print(f"Converted PNG to GIF: {gif_filename}")

                        # Encode the image as a base64 string
                        with open(image_filename, "rb") as image_file:
                            base64_image = base64.b64encode(
                                image_file.read()).decode('utf-8')

                        # Get just the filename without the path
                        base_filename = os.path.basename(image_filename)
                        # Create a dictionary with the base filename as the key and base64 data as the value
                        image_logo_data = {
                            base_filename: base64_image,
                        }
                        # Save the base64 data in a JSON file
                        base64_filename = os.path.join(
                            output_folder, f"page_{page_number}_section_{i}_logo.json")

                        with open(base64_filename, "w") as json_file:
                            json.dump(image_logo_data, json_file, indent=4)

                        # Append the base64 data to the original coordinates logo_data
                        text["logo_base64"] = base64_image

                        # REORDERING THE DICTIONARY KEYS

                        desired_order = ["extracted_text", "x0", "y0",
                                         "x1", "y1", "base64", "logo", "logo_base64"]

                        entry["extracted_texts"][i] = dict(
                            (key, text[key]) for key in desired_order)

                    # FINDING THE IMAGE LOGO COORDINARTES AND EXTRACTING THE IMAGE LOGO

                    if text["logo"].get("image_logo", None) is not None:
                        # continue

                        if len(text["logo"].get("image_logo")):

                            text["image_logos"] = []

                            for i, img in enumerate(text["logo"].get("image_logo")):
                                # checking for multiple images in the section

                                image = page = pdf_document_pdf_plumber.pages[page_number-1].crop(
                                    (img["x0"], img["y1"],
                                     img["x1"], img["y0"])
                                )

                                # SAVE THE EXTRACTED IMAGE LOGO as opng file
                                image_filename = os.path.join(
                                    output_folder, f"page_{page_number}_section_{i}_logo_image_{i+1}.png")
                                image_obj = image.to_image(
                                    resolution=resolution)
                                image_obj.save(image_filename, format="png")

                                print(
                                    f"Extracted image logo saved as {image_filename}")

                                # Now, convert the PNG image to GIF format using Pillow
                                gif_filename = os.path.join(
                                    output_folder, f"page_{page_number}_section_{i}_logo_image_{i+1}.gif")
                                image_pil = Image.open(image_filename)
                                image_pil.save(gif_filename, "GIF")
                                print(f"Converted PNG to GIF: {gif_filename}")

                                # Encode the image as a base64 string
                                with open(image_filename, "rb") as image_file:
                                    base64_image = base64.b64encode(
                                        image_file.read()).decode('utf-8')

                                # Get just the filename without the path
                                base_filename = os.path.basename(
                                    image_filename)
                                # Create a dictionary with the base filename as the key and base64 data as the value
                                image_logo_data = {
                                    base_filename: base64_image,
                                }
                                # Save the base64 data in a JSON file
                                base64_filename = os.path.join(
                                    output_folder, f"page_{page_number}_section_{i}_logo_image_{i+1}.json")

                                with open(base64_filename, "w") as json_file:
                                    json.dump(image_logo_data,
                                              json_file, indent=4)

                                # extracting text from image logo using ocr and adding the base64
                                # to the dict

                                extracted_text = extract_text_from_image(
                                    image_filename)

                                # checking if extracted text is empty
                                if not len(extracted_text.replace("\n", '').replace("\f", '').strip()):
                                    extracted_text = "text not available"

                                text["logo"]["image_logo"][i]["image_text"] = extracted_text
                                text["logo"]["image_logo"][i][
                                    "image_label"] = f"image_label_{i+1}"
                                text["logo"]["image_logo"][i]["base64"] = base64_image

        # Save the updated coordinates_data back to the coordinates file

        with open(coordinates_file, "w") as json_file:
            json.dump(coordinates_data, json_file, indent=4)
    # except Exception as e:
    #     print(e)
    #     print(f"Error: {str(e)}")
