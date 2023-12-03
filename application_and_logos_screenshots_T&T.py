'''GOOOD DONT DELETE'''
import pdfplumber
import json
import fitz  # PyMuPDF
import os
from PIL import Image
import base64
import re
import io


# Function to check if a string is entirely uppercase
def is_uppercase(s):
    return s == s.upper()

# # PATH TO THE PDF
# # KEEP THE PDF IN THE SAME FOLDER AS THE SCRIPT
pdf_file_path = 'TT20231115-44.pdf'  # Replace with your PDF path

# Regular expression pattern to match aspplications
pattern = re.compile(r"(\b\d{5,}\b\s+Class[\s\S]*?)(?=\b\d{5,}\b\s+Class|$)")

# Define a delimiter that identifies the heading or footer in the PDF
# This is used to split the text at this delimiter for each page
delimiter = 'Trade Marks Journal, Publication Date: November 15th 2023'

# Create a dictionary to store section data and initialize section number
section_data = {}
section_prefix = "tradeMark"
section_num = 1 # Start with section number 1

# Initialize a string to hold the concatenated text of all pages
full_text = ""
# Initialize a list to track the positions where each new page's text starts in 'full_text'
page_break_positions = []

# Open the PDF using pdfplumber
with pdfplumber.open(pdf_file_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        # Extract text from the current page
        page_text = page.extract_text() or ""
        # Record the position where this page's text will start in 'full_text'
        page_break_positions.append(len(full_text))
        #  Concatenate this page's text to 'full_text', separated by a newline
        full_text += page_text + "\n"  # Add a newline character to separate pages

# Define a function to find the page number given a position in 'full_text'
def find_page_number(position):
    # Determine which page this position falls into based on 'page_break_positions'
    return next((i for i, break_pos in enumerate(page_break_positions) if position < break_pos), len(page_break_positions))

# Iterate over all matches of the pattern in 'full_text'
for match in pattern.finditer(full_text):
    # Extract the matched text (an application)
    application_text = match.group(1)
    # Get the start and end positions of the match in 'full_text'
    start_pos, end_pos = match.span(1)
    # Determine the start and end page numbers for this application
    start_page = find_page_number(start_pos)
    # Determine the end page number
    end_page = find_page_number(end_pos)

    # To add the entire text in 'content'
    content_lines = application_text.strip().split("\n")

    # Split the application text using the delimiter
    split_texts = application_text.split(delimiter)
    # Strip whitespace from each part and filter out empty strings
    split_texts = [text.strip() for text in split_texts if text.strip()]

    # Construct a unique key for this section
    section_key = f"{section_prefix} {section_num}"
    
    # Store the page numbers, original content, and segmented content in 'section_data'
    section_data[section_key] = {
        "page_number": list(range(start_page, end_page)),
        "content": content_lines,
        "content_data": [{"text_on_page": page, "text": text.split('\n')} for page, text in zip(range(start_page, end_page + 1), split_texts)]
    }

    # Filter the entries in 'content_data'
    filtered_content_data = []

    # LOOPING THROUGHT THE JSON STRUCTURE TO REACH CONTENT DATA
    for entry in section_data[section_key]["content_data"]:
        # Check if the first line of the entry starts with the specified string
        if entry['text'][0].startswith("Protocol Relating to the Madrid Agreement Concerning"):
            continue  # Skip the entire entry
        # LOOP THROUGHT THE LINES IN THE KEY 'TEXT'
        # IF THE LINE STARTS WITH A CERTAIN CONDITION THEN REMOVE THAT ENTIRE ENTRY
        filtered_text = [line for line in entry['text']
                        if not (line.startswith("THE APPLICANT CLAIMS ") or 
                                line.startswith("CFE ") 
                                or is_uppercase(line) 
                                or len(line.split()) == 1)
                                ]
        
        if filtered_text:  # Only add entry if there's any text left after filtering
            filtered_content_data.append({'text_on_page': entry['text_on_page'], 'text': filtered_text})

    # Update the 'content_data' in the original data
    section_data[section_key]["content_data"] = filtered_content_data
    
    section_num += 1

# Convert the extracted data to JSON format
applications_json_str = json.dumps(section_data, indent=4, ensure_ascii=False)

# Write the JSON string to a file
with open(f'{pdf_file_path}_result_of_segmented_text.json', 'w', encoding='utf-8') as file:
    file.write(applications_json_str)




# '''COORDINATES'''
# Path to the PDF file
def define_coordinates_from_pdf_for_application_screenshots_tunisia(pdf_file_path, extracted_text_json_path):
    
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
        print(e)
        return

    # Extract text from the PDF and store it in extracted_text_dict
    with pdfplumber.open(pdf_file_path) as pdf:
        # Initialize variables to store the minimum and maximum coordinates
        min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

        # Iterate through each page in the PDF
        for page_number, page in enumerate(pdf.pages, start=1):            

            # Retrieve the current page (0-based index)
            page = pdf.pages[page_number - 1]  # Pages are 0-based index

            # Extract words from the page with their bounding box coordinates
            words_with_bounding_box = page.extract_words()

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

            # Iterate through existing data entries
            for page_data_key, page_data in existing_data.items():
                # Skip this entry if it has no 'content_data'
                if not page_data.get("content_data"):
                    continue

                # Iterate through content entries for the current page
                for content_entry in page_data["content_data"]:
                    # Get the start and end patterns
                    start = content_entry["text"][0]
                    end = content_entry["text"][-1]

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
                                                       
                            # Print a message indicating that the text has been successfully extracted
                            match = False
                            print("[+] extracted the text => ",
                                  '\n'.join(content_entry['text']), "\n")


                            # Update the content_data entry with coordinates
                            content_entry["coordinates"] = {
                                "x0": 0,
                                "y0": 60,
                                "x1": max_x1,
                                "y1": max_y1
                            }

                            break

    # Save the modified JSON file with coordinates added
    with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False, separators=(',', ': '))


# Example usage:
pdf_file_path = pdf_file_path  # Replace with the path to your PDF file, THIS VARIABLE IS IN THE STARTING OF THE SCRIPT
extracted_text_json_path = f"{pdf_file_path}_result_of_segmented_text.json"  # This is the JSON input file and also the new output file
define_coordinates_from_pdf_for_application_screenshots_tunisia(
    pdf_file_path, extracted_text_json_path)


'''NEW FUNCTION BASED ON THE NEW STRUCTURE'''
def extract_and_process_images_tunisia(json_data, pdf_file, output_folder, resolution=200):
    # ADDING PADDING TO THE IMAGES TAKEN
    padding = 25
    # DICT TO STORE THE RECTS THAT WERE SKIPPED (MAINLY ONE LINERS)
    skipped_rectangles = {}
    last_processed_page = -1

    try:
        # CHECK IF AN OUTPUT FOLDER EXISTS, CREATE ONE IF IT DOES NOT EXIST
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # READING THE PDF FILE
        pdf_document = fitz.open(pdf_file)

        # LOOPING THROUGH THE JSON FILE AS PER THE NEW STRUCTURE
        for trade_mark, data in json_data.items():
            # LOOPING TO GET TO THE REQUIRED NEST IN THE JSON
            for page_data in data['content_data']:
                if 'coordinates' not in page_data:
                    print(f"Skipping an entry in {trade_mark} as it lacks 'coordinates'.")
                    continue

                # VARIABLE TO STORE THE PAGE NUMBER ON WHICH THE TEXT IS 
                page_number = page_data['text_on_page']
                page = pdf_document[page_number - 1]
                page_width = page.rect.width 
                
                # IF PAGE NUMBER IS NOT THE LAST PROCESSED PAGE 
                # THEN PAGE NUMBER WOULD BE THE SAME
                if page_number != last_processed_page:
                    image_counter = 0
                    last_processed_page = page_number

        # The coordinates are in the format (x0, y0, x1, y1) - top left and bottom right corners.
        # x0 is the horizontal coordinate (from the left) of the top-left corner. [LEFT VERTICLE LINE goes LEFT(lower number) or RIGHT (higher number)]
        # y0 is the vertical coordinate (from the top) of the top-left corner. [TOP HORIZONTAL LINE goes UP (lower number) and DOWN(higher number) ]
        # x1 is the horizontal coordinate (from the left) of the bottom-right corner. [RIGHT VERTICLE LINE goes LEFT (lower number) or RIGHT (higher number)]
        # y1 is the vertical coordinate (from the top) of the bottom-right corner. [BOTTOM HORIZONTAL LINE goes UP(lower number) or DOWN(higher number)]

                coordinates = page_data['coordinates']
                x0, y0, x1, y1 = coordinates['x0'], coordinates['y0'], coordinates['x1'], coordinates['y1']

                x0 = coordinates['x0'] + padding
                y0 = coordinates['y0']
                x1 = page_width - 40  # USING PAGE WIDTH TO AVOID ERROR OF MISSING DATA 
                y1 = coordinates['y1'] + padding
                page = pdf_document[page_number - 1]
                
                rect = fitz.Rect(x0, y0, x1, y1)

                image = page.get_pixmap(matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect)

                # Filename with page number and counter
                image_filename_suffix = "_" if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0 else ""
                # SAVING IT AS .PNG
                image_filename = os.path.join(output_folder, f"{os.path.basename(pdf_file)}_page_{page_number}_img_{image_counter}{image_filename_suffix}.png")
                image.save(image_filename)

                # SAVING THE IMAGE TAKEN IN .GIF FORMAT
                gif_filename = os.path.join(output_folder, f"{os.path.basename(pdf_file)}_page_{page_number}_img_{image_counter}{image_filename_suffix}.gif")
                image_pil = Image.open(image_filename)
                image_pil.save(gif_filename, "GIF")

                # SAVING THE IMAGE IN BASE64 FORMAT
                with open(image_filename, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

                # Update JSON data with base64 for both valid and invalid coordinates
                page_data['binaryContent'] = base64_image

                base64_filename = os.path.join(output_folder, f"{os.path.basename(pdf_file)}_page_{page_number}_img_{image_counter}{image_filename_suffix}_base64.json")
                with open(base64_filename, "w") as json_file:
                    json.dump({os.path.basename(image_filename): base64_image}, json_file, indent=4)

                # INCREASE THE IMAGE COUNTER BY 1
                # TO ENSURE THAT imAGES DON'T GET OVERWRITTEN
                image_counter += 1

        with open(f'output_{os.path.basename(pdf_file)}.json', 'w') as file:
            json.dump(json_data, file, indent=4)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # CLOSING THE PDF TO SAVE MEMORY SPACE
    finally:
        pdf_document.close()


# Load the entire JSON file
file_path = f'{pdf_file_path}_result_of_segmented_text.json'
with open(file_path, 'r', encoding= 'utf-8') as file:
    json_data = json.load(file)

# Example usage
pdf_file_path = pdf_file_path  # Replace with PDF file path
output_folder_path = f'output_applications_image_{pdf_file_path}'  # Replace with output folder path
extract_and_process_images_tunisia(json_data, pdf_file_path, output_folder_path)


def extract_logos_tunisia(pdf_file_path, json_path, output_folder):
    # Read JSON data
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Open the PDF
    doc = fitz.open(pdf_file_path)

    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each trademark entry in the JSON
    for tradeMark, details in data.items():
        content_data = details.get("content_data", [])
        
        # Process each content data entry
        for item in content_data:
            page_number = item.get("text_on_page", -1)
            coordinates = item.get("coordinates", {})

            # If page number and coordinates are valid, process the page
            if page_number >= 0 and coordinates:
                page = doc.load_page(page_number - 1)  # page numbers in PDF are 0-indexed

                # Define the rectangle for image extraction
                rect = fitz.Rect(coordinates["x0"], coordinates["y0"], coordinates["x1"], coordinates["y1"])

                # Extract images that intersect with the defined rectangle
                for img in page.get_images(full=True):
                    xref = img[0]
                    img_rect = page.get_image_rects(xref)
                    
                    # Check if the image is within the defined area
                    for r in img_rect:
                        if rect.intersects(r):
                            # Extract and save the image with trademark in filename
                            pix = fitz.Pixmap(doc, xref)
                            image_filename = os.path.join(output_folder, f"{tradeMark}_logo_{xref}.png")
                            base64_filename = os.path.join(output_folder,f"{tradeMark}_logo_{xref}_base64.json")
                            if pix.n < 5:  # this is GRAY or RGB
                                pix.save(image_filename)
                            else:  # CMYK: convert to RGB first
                                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                                pix1.save(image_filename)
                                pix1 = None
                            pix = None

                            # Save the image in base64 format
                            with open(image_filename, "rb") as image_file:
                                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

                            # Update JSON data with base64 in a new key
                            item["deviceElements"] = base64_image if base64_image else None

                            with open(base64_filename, "w") as json_file:
                                json.dump({image_filename: base64_image}, json_file, indent=4)
    doc.close()

    # Write the updated JSON data back to the file
    with open(json_path, 'w', encoding= 'utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return data


# Assuming the user will provide the path to the PDF file they want to process
json_path = f'output_{pdf_file_path}.json'   # Replace this with the actual path to the JSON file
# Set the path to the folder where images will be saved
output_folder_logos = f"logo_images_{pdf_file_path}"  # Replace this with the actual path to the output folder

# Extract images, save them in a folder, and update JSON
updated_data_with_images_in_folder = extract_logos_tunisia(pdf_file_path, json_path, output_folder_logos)