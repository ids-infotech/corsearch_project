
import fitz
import pdfplumber
import re
import json
import os
from PIL import Image
import base64

resolution = 200  # Change this to your desired resolution (in DPI)
pdf_file_path = "BT20230612-108.pdf"
pdf_document = fitz.open(pdf_file_path)
pdf_data = []
pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")
section_data = {}
section_num = 1
for page_number in range(pdf_document.page_count):
    page = pdf_document.load_page(page_number)
    page_text = page.get_text('text')
    matches = pattern.findall(page_text)
    for match in matches:
        if "(511) \u2013 NICE classification for goods and services" in match:
            continue
        if section_num not in section_data:
            section_data[section_num] = {"content": []}
        content_lines = [line for line in match.split('\n') if line.strip()]
        section_data[section_num]["content"].extend(content_lines)
        if "(210)" in match:
            section_num += 1
pdf_document.close()
# output_data = json.dumps(section_data, indent=4)
# with open("output.json", "w", encoding="utf-8") as json_file:
#     json_file.write(output_data)
output_data = json.dumps(section_data, indent=4, ensure_ascii=False)
with open("output.json", "w", encoding="utf-8") as json_file:
    json_file.write(output_data)

#image extracation 
#output--->   extract text  dict  in the final json
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
                        extracted_text_dict[str(page_number)]["extracted_texts"].append({
                            "extracted_text": '\n'.join(v['content']),
                            "x0": min_x0,
                            "y0": min_y0,
                            "x1": max_x1,
                            "y1": max_y1,
                        })
                        match = False
                       
                        break
    json.dumps(extracted_text_dict, indent=4)
    # Save the defined coordinates to a new JSON file with formatting
    with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
    # with open("output.json", "w", encoding="utf-8") as output_json_file:
        json.dump(extracted_text_dict, output_json_file,
                  indent=4, separators=(',', ': '))

# output ---> corrdinates into the final json file 
def extract_and_save_image(pdf_file, coordinates_file, output_folder, resolution=200):
    padding = 5
    try:
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Open the PDF file
        pdf_document = fitz.open(pdf_file)
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
                image_filename = os.path.join(output_folder, f"page_{page_number}_section_{i}.png")
                image.save(image_filename)
                print(f"Extracted image saved as {image_filename}")
                # Now, convert the PNG image to GIF format using Pillow
                gif_filename = os.path.join(output_folder, f"page_{page_number}_section_{i}.gif")
                image_pil = Image.open(image_filename)
                image_pil.save(gif_filename, "GIF")
                print(f"Converted PNG to GIF: {gif_filename}")
                # Encode the image as a base64 string
                with open(image_filename, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                # Get just the filename without the path
                base_filename = os.path.basename(image_filename)
                # Create a dictionary with the base filename as the key and base64 data as the value
                image_data = {
                    base_filename: base64_image
                }
                # Save the base64 data in a JSON file
                base64_filename = os.path.join(output_folder, f"page_{page_number}_section_{i}.json")
                with open(base64_filename, "w") as json_file:
                    json.dump(image_data, json_file, indent=4)
                # Append the base64 data to the original coordinates_data
                text["base64"] = base64_image
        # Save the updated coordinates_data back to the coordinates file

        with open(coordinates_file, "w") as json_file:
            json.dump(coordinates_data, json_file, indent=4)
    except Exception as e:
        print(e)
        print(f"Error: {str(e)}")


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
        pdf_metadata['creationDate'] = convert_to_readable_date(pdf_metadata['creationDate'])
    if 'modDate' in pdf_metadata:
        pdf_metadata['modDate'] = convert_to_readable_date(pdf_metadata['modDate'])
    return pdf_metadata, image_count, pdf_size, page_count, word_count, char_count



def process_single_pdf(pdf_file_path, json_file_path):
    pdf_details_list = []
    # print(f"Processing PDF: {pdf_file_path}")
    pdf_metadata, image_count, pdf_size, page_count, word_count, char_count = get_pdf_metadata_and_info(pdf_file_path)
    # print("PDF Metadata:")
    for key, value in pdf_metadata.items():
        y=f"{key}: {value}"
    if "-" in os.path.basename(pdf_file_path) and pdf_file_path.endswith(".pdf"):
        pdf_info = extract_country_info(os.path.basename(pdf_file_path))
        # print("COUNTRY INFO:")
        for key, value in pdf_info.items():
            t=f"{key}: {value}"
    else:
        pdf_info = {}
    
    pdf_details = {
        "PDF File": pdf_file_path,
        "PDF Metadata": pdf_metadata,
        **pdf_info,
        "Number of Images in PDF": image_count,
        "Number of Pages in PDF": page_count,
        "PDF File Size (in MB)": pdf_size,
        "Word Count": word_count,
        "Character Count": char_count
    }
    # Read the existing JSON data
    with open(json_file_path, 'r') as json_file:
    # with open(json_file_path, 'w') as json_file:
    #     json.dump(pdf_details_dict, json_file, indent=4, ensure_ascii=False)    
        existing_data = json.load(json_file)
    

    # Add the new data to the existing JSON data
    existing_data["1"] = pdf_details
    # Write the updated data back to the JSON file
    # with open(json_file_path, 'w') as json_file:
        # json.dump(existing_data, json_file, indent=4)  # You can use 'indent' for pretty formatting
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    pdf_file_path = "BT20230612-108.pdf"  # Change this to your PDF file
    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]  # Extract the filename without extension
    extracted_text_json_path = "output.json"       #extract the  file name based on pdf file name
    
    output_json_path = f"{pdf_filename}.json"  # Set the output JSON filename based on the PDF filename
    define_coordinates_from_pdf(
        pdf_file_path, extracted_text_json_path, output_json_path)
    coordinates_file = output_json_path  # Use the same JSON filename for coordinates
    # resolution = 200  # Change this to your desired resolution (in DPI)

    
    output_folder = "output_images"  


    # resolution = 200  # Change this to your desired resolution (in DPI)
    extract_and_save_image(pdf_file_path, coordinates_file,
                           output_folder, resolution)
    json_file_path = output_json_path  # Use the same JSON filename for processing
    process_single_pdf(pdf_file_path, json_file_path)
    # process_multiple_pdfs(pdf_file_path, json_file_path)
