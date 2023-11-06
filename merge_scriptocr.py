import fitz
import pdfplumber
import re
import json
import os
from PIL import Image
import base64
import re
from docx import Document
import json
from bhutan_docx import get_headings as get_headings
import time
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\syed.a\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"


headings = get_headings()
head_list = list(headings.values())
print(head_list[0], "-------head list-----")

# time.sleep(50)
resolution = 200  # Change this to your desired resolution (in DPI)

# image extracation
# output--->   extract text  dict  in the final json


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


def extract_text_from_image(image_path):
    processed_image = preprocess_image(image_path)

    # Perform OCR on the preprocessed image
    text = pytesseract.image_to_string(processed_image)

    print("Text from image is", "bad" if not text else "good")
    return text


def define_coordinates_from_pdf(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
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

                # ------------ MY CODE----------------------###
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


def is_valid_pdf(pdf_file_path):
    try:
        with fitz.open(pdf_file_path) as pdf_document:
            _ = len(pdf_document)
        return True  # PDF is valid
    except Exception as e:
        print(f"Error: {e}")
        return False  # PDF is not valid


def handle_corrupted_pdf(pdf_file_path, error_message):
    with open("corrupted_pdf_logs.txt", "a") as log_file:
        log_file.write(f"Corrupted PDF: {pdf_file_path}\n")
        log_file.write(f"Error: {error_message}\n\n")


def handle_password_protected_pdf(pdf_file_path):
    try:
        pdf_document = fitz.open(pdf_file_path)
        if pdf_document.is_encrypted:
            password = input("Enter the password for the PDF: ")
            pdf_document.authenticate(password)
            return pdf_document
        else:
            return pdf_document
    except Exception as e:
        print(f"Error: {e}")
        return None

# for image folder


def create_output_folder(pdf_file_path):
    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
    # Creating a folder name based on the PDF file name
    output_folder = f"{pdf_filename}_images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder


def get_pdf_size(pdf_file_path):
    pdf_size_bytes = os.path.getsize(pdf_file_path)
    pdf_size_mb = pdf_size_bytes / (1024 * 1024)
    formatted_pdf_size = "{:.4f}".format(pdf_size_mb)
    return formatted_pdf_size


def convert_to_readable_date(date_string):
    date_parts = date_string.split("+")

    if len(date_parts) >= 1:
        date_part = date_parts[0].replace("D:", "").strip()
        year = date_part[:4]
        month = date_part[4:6]
        day = date_part[6:8]
        time_part = date_part[-6:]
        formatted_date = f"{year}-{month}-{day}"
        formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
        result = f"Year: {year}, Date: {formatted_date}, Time: {formatted_time}"
        if len(date_parts) == 2:
            time_zone_part = date_parts[1].strip()
            result += f", Time Zone: {time_zone_part}"
        return result
    else:
        return "Invalid Date String"


def extract_country_info(input_str):
    country_code = input_str[:2]
    year_str = input_str[2:6]
    month_str = input_str[6:8]
    day_str = input_str[8:10]
    number_str = input_str.split('-')[1].split('.')[0]

    return {
        "Country Code": country_code,
        "Year": year_str,
        "Month": month_str,
        "Day": day_str,
        "Batch": number_str
    }


def get_pdf_metadata_and_info(pdf_file_path):
    pdf_document = fitz.open(pdf_file_path)
    pdf_metadata = pdf_document.metadata
    image_count = 0
    page_count = len(pdf_document)

    word_count = 0
    char_count = 0

    for page_number in range(page_count):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)
        image_count += len(image_list)
        page_text = page.get_text()
        words = page_text.split()
        word_count += len(words)
        char_count += len(page_text)

    pdf_size = get_pdf_size(pdf_file_path)

    if 'creationDate' in pdf_metadata:
        pdf_metadata['creationDate'] = convert_to_readable_date(
            pdf_metadata['creationDate'])
    if 'modDate' in pdf_metadata:
        pdf_metadata['modDate'] = convert_to_readable_date(
            pdf_metadata['modDate'])

    return pdf_metadata, image_count, pdf_size, page_count, word_count, char_count


def process_multiple_pdfs(pdf_folder_path, output_folder_path):
    # Ensure the output folder exists, if not, create it
    os.makedirs(output_folder_path, exist_ok=True)

    pdf_files = [file for file in os.listdir(
        pdf_folder_path) if file.endswith(".pdf")]

    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(pdf_folder_path, pdf_file)
        print(f"Processing PDF: {pdf_file_path}")

        # Check if the PDF is valid before processing
        if not is_valid_pdf(pdf_file_path):
            error_message = "Invalid or corrupted PDF format."
            print(f"Skipping {pdf_file} due to {error_message}")
            handle_corrupted_pdf(pdf_file_path, error_message)
            continue

        # Handle password-protected PDFs
        pdf_document = handle_password_protected_pdf(pdf_file_path)
        if pdf_document is None:
            print(f"Failed to open {pdf_file}. Please check the password.")
            continue

        # pdf_data = []
        pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")
        section_data = {}
        section_num = 1
        fl_list = []
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            page_text = page.get_text('text')
            matches = pattern.findall(page_text)
            for match in matches:
                if "(511) \u2013 NICE classification for goods and services" in match:
                    continue
                if section_num not in section_data:

                    section_data[section_num] = {"content": []}
                content_lines = [
                    line for line in match.split('\n') if line.strip()]
                # print(type(content_lines),content_lines,"-----content line----------------318-------",match)
                fl = []
                flag = False
                if isinstance(content_lines, list):
                    lst = head_list[0]

                    for i in content_lines:
                        print(i, "------------")
                        for j in lst:
                            if j in i:
                                fl.append(i)
                        if '511' in i:
                            flag=True
                        if '210' in i:
                            flag=False
                        if flag:
                            fl.append(i)

                section_data[section_num]["content"].extend(fl)
                fl = fl.clear()
                if "(210)" in match:
                    section_num += 1
        # pdf_document.close()

        output_data = json.dumps(section_data, indent=4, ensure_ascii=False)
        with open("output.json", "w", encoding="utf-8") as json_file:
            json_file.write(output_data)
        # Extract PDF metadata and country info (implement your logic)
        pdf_metadata, image_count, pdf_size, page_count, word_count, char_count = get_pdf_metadata_and_info(
            pdf_file_path)
        pdf_info = extract_country_info(os.path.basename(pdf_file))

        output_json_path = os.path.join(
            output_folder_path, f"{pdf_file.split('.')[0]}.json")
        coordinates_file = output_json_path
        extracted_text_json_path = "output.json"
        # Create the output folder based on the PDF name
        output_folder = create_output_folder(pdf_file_path)

        define_coordinates_from_pdf(
            pdf_file_path, extracted_text_json_path, output_json_path)

        extract_and_save_image(
            pdf_file_path, coordinates_file, output_folder, resolution)

        with open(coordinates_file, 'r', encoding='utf-8') as json_file:
            coordinates_data = json.load(json_file)

        # Create a dictionary with PDF details
        pdf_details = {
            "PDF Metadata": pdf_metadata,
            **pdf_info,
            "Number of Images in PDF": image_count,
            "Number of Pages in PDF": page_count,
            "PDF File Size (in MB)": pdf_size,
            "Word Count": word_count,
            "Character Count": char_count,
            "Coordinates Data": coordinates_data
        }

        print("PDF details processed for", pdf_file)
        print("Number of Images in PDF:", image_count)
        print("Number of Pages in PDF:", page_count)
        print("PDF File Size (in MB):", pdf_size, "MB")
        print("Word Count:", word_count)
        print("Character Count:", char_count)
        print("\n")

        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(pdf_details, json_file, indent=4, ensure_ascii=False)

        print(f"PDF details saved to: {output_json_path}")
        pdf_document.close()


if __name__ == "__main__":
    pdf_folder_path = r'output_pdf'  # Change this to your PDF file
    # pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]  # Extract the filename without extension
    # Replace with the path to your desired output folder
    output_folder_path = r'output'
    # extracted_text_json_path = "output.json"       #extract the  file name based on pdf file name

    # Write the PDF details to a separate JSON file in the output folder

    # output_json_path = f"{pdf_filename}.json"  # Set the output JSON filename based on the PDF filename

    # coordinates_file = output_json_path  # Use the same JSON filename for coordinates

    # output_folder = "output_images"

    # resolution = 200  # Change this to your desired resolution (in DPI)

    # json_file_path = output_json_path  # Use the same JSON filename for processing
    # process_single_pdf(pdf_file_path, json_file_path)
    process_multiple_pdfs(pdf_folder_path, output_folder_path)