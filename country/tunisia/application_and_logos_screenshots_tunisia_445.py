import pdfplumber
import json
import fitz  # PyMuPDF
import os
from PIL import Image
import base64
import re
import io
from string import digits

# Define a function to process a page and return its text and page number
def process_page_for_application_screenshots(page):
    page_text = page.get_text("text")
    return page_text, page.number

def correct_text_segmentation_for_application_screenshots(content_data, delimiter):
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

'''DONT DELETE THIS FUNCITON'''
# Function to remove 'start' or 'stop' from the ending index of 'text' in content_data
# def remove_start_stop_from_text_445(content_data):
#     for entry in content_data:
#         text = entry["text"]
        
#         if isinstance(text, list):
#             # If 'text' is a list, iterate over the elements
#             for i in range(len(text)):
#                 # Check if 'start' or 'stop' is at the ending index and remove it
#                 if text[i].endswith('start'):
#                     text[i] = text[i][:-len('start')].strip()
#                 elif text[i].endswith('stop'):
#                     text[i] = text[i][:-len('stop')].strip()
#         elif isinstance(text, str):
#             # Check if 'start' or 'stop' is at the ending index and remove it
#             if text.endswith('start'):
#                 entry["text"] = text[:-len('start')].strip()
#             elif text.endswith('stop'):
#                 entry["text"] = text[:-len('stop')].strip()

'''BEST VERSION for 445'''
def remove_start_stop_from_text_445(content_data):
    for entry in content_data:
        text = entry["text"]
        
        if isinstance(text, list):
            # If 'text' is a list, iterate over the elements
            for i in range(len(text)):
                # Check if 'start' or 'stop' is at the ending index and remove it
                if text[i].endswith('start'):
                    text[i] = text[i][:-len('start')].strip()
                elif text[i].endswith('stop'):
                    text[i] = text[i][:-len('stop')].strip()
                    
            # Check if the last line is whitespace followed by a number, then remove it
            while text and re.match(r'\s*\d+\s*$', text[-1]):
                text.pop()  # Remove the last line
        elif isinstance(text, str):
            # Check if 'start' or 'stop' is at the ending index and remove it
            if text.endswith('start'):
                entry["text"] = text[:-len('start')].strip()
            elif text.endswith('stop'):
                entry["text"] = text[:-len('stop')].strip()
                
            # Check if the entire 'text' is whitespace followed by a number, then set 'text' to an empty string
            if re.match(r'\s*\d+\s*$', text):
                entry["text"] = ''


def merge_duplicate_pages_for_application_screenshots(content_data):
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


# Function to remove leading numbers from a string
def remove_leading_numbers(s):
    return re.sub(r'^\d+\s+', '', s)

# REMOVE EMTY STRINGS
def remove_empty_strings(lines):
    return [line for line in lines if line.strip() and line.strip().lower() != "start"]

def process_lines(content_lines):

    processed_lines = []
    for line in content_lines:

        # Exclude lines with only one character
        if len(line.strip()) == 1:
            continue

        # Exclude lines with some digits followed by a hyphen
        if any(char.isdigit() for char in line) and line.strip().endswith('-'):
            continue

        if line.strip().isdigit():
            continue
        # Add the processed line to the result
        processed_lines.append(line)

    return processed_lines

def extract_and_segment_applications_tunisia_445(pdf_file_path):
    # Define a regular expression pattern to match specific text sections
    pattern = re.compile(r"Numéro de dépôt[\s\S]*?(?=Numéro de dépôt|$)")

    # Path to the PDF file
    pdf_file_path = "TN20230118-445.pdf"
    pdf_document = fitz.open(pdf_file_path)

    # Define the page range you want to process
    start_page = 10  # The first page in PyMuPDF is 0
    end_page = 30  # Process up to page 50

    # TO STORE IMAGE LOGOS
    output_dir_image_logo = f"{pdf_file_path}_image_logos"

    # This dictionary will hold all extracted text with corresponding page numbers
    text_pages = {}
    # Loop over the specified range of pages
    for page_num in range(start_page, end_page):
        page = pdf_document[page_num]
        text, pn = process_page_for_application_screenshots(page)
        text_pages[pn] = text

    # Concatenate the text from all pages
    extracted_text = " ".join(text_pages.values())

    # Find matches in the concatenated text
    matches = pattern.findall(extracted_text)

    # Create a dictionary to store section data and initialize section number
    section_data = {}
    section_num = 1
    section_prefix = "tradeMark"

    # Initialize a list to store section content data
    # section_content_data = []

    # Iterate through the matches
    for match in matches:
        start_index = extracted_text.find(match)

        # Determine the pages the match spans
        # Create an empty list to store the page numbers where the match appears
        page_nums = []
        # Initialize a variable to keep track of the current position in the extracted text
        current_pos = 0 
        # Iterate through each page and its corresponding text
        for pn, txt in text_pages.items():
            # Update the current position by adding the length of the text on the current page
            current_pos += len(txt)
            if start_index < current_pos:
                # If the starting index of the match is less than the current position, it means the match spans this page
                # Add the page number to the list of page numbers where the match appears
                # Increase the pn (page_numer) by 1 to match page number in PDF
    #             new_pn_matching_PDF = pn + 1
                page_nums.append(pn)
                # If the current position is greater than the end of the match, 
                # it means the match doesn't span further pages
                if current_pos > start_index + len(match):
                    break


        #  NEW SECTION KEY
        section_key = f"{section_prefix} {section_num}"

        if section_num not in section_data:
            section_data[section_key] = {"page_number": [pn + 1 for pn in page_nums] # Adding 1 to adjust the page number
                                        , "content": [],
                                        "content_data": []
                                        }

        # Split the matched text into lines and add them to the section data
        content_lines = [line for line in match.split("\n") if line.strip()]
        content_lines_cleaned =  process_lines(content_lines)
        section_data[section_key]["content"].extend(content_lines_cleaned)

        # Initialize a pointer for the current start of the segment
        segment_start = start_index

        # Temporary storage for the segmented content for this match
        current_content_data = []

        # Iterate through the pages the match spans
        for pn in page_nums:
            # Determine where the segment for this page ends
            segment_end = min(segment_start + len(text_pages[pn]), start_index + len(match))

            # Check if segment_end is cutting a word. If yes, move it back to the last space.
            while extracted_text[segment_end] not in [" ", "\n", "\t"] and segment_end > segment_start:
                segment_end -= 1

            # Extract the segment of the match that lies within this page
            segment = extracted_text[segment_start:segment_end]

            # If this segment contains part of the match, add it to the current_content_data
            if segment.strip():
                
                current_content_data.append({
                    "text_on_page": pn + 1, # Adding 1 to adjust the page number
                    "text": segment.strip()
                })

            # Update segment_start for the next page
            segment_start = segment_end
        
        # Add the segmented content data to the section data
        section_data[section_key]["content_data"].extend(current_content_data)
        
        # Call the correction function for the current section
        #  Removing the HEADING from the extracted text
        delimiter = " Muwassafat  N° 445 "
        section_data[section_key]["content_data"] = correct_text_segmentation_for_application_screenshots(section_data[section_key]["content_data"], delimiter)
        
        # Call the merge_duplicate_pages_for_application_screenshots function to join text on the same page into one
        section_data[section_key]["content_data"] = merge_duplicate_pages_for_application_screenshots(section_data[section_key]["content_data"])

        # Call the function to remove 'start' or 'stop' from the ending index of 'text' in content_data
        # remove_start_stop_from_text_445(section_data[section_key]["content_data"])

        unwanted_line_pattern = re.compile(r"\s*\d+\s+Muwassafat  N° 445")

        # Split the text into lines (segments) for each entry in content_data
        for entry in section_data[section_key]["content_data"]:
            text = entry["text"]
            lines = text.split('\n')

            # lines = [remove_leading_numbers(line) for line in lines if line.strip() != ""]
            # Call the function to remove 'start' or 'stop' from the ending index of 'text' in content_data
            remove_start_stop_from_text_445(section_data[section_key]["content_data"])
            lines = remove_empty_strings(lines)

            # Use the regex pattern to find and remove the unwanted line
            # Check if the last line matches the unwanted pattern, and remove it if so
            if lines and unwanted_line_pattern.search(lines[-1]):
                lines.pop()

            # Update the "text" value for the current entry to contain the split lines
            entry["text"] = lines
            
        section_num += 1

    # Serialize the section data to a JSON format
    output_data = json.dumps(section_data, ensure_ascii=False, indent=4)

    output_file_path =  f'{pdf_file_path}_result_of_segmented_text.json'

    # Write the JSON data to a file
    with open(output_file_path, "w", encoding="utf-8") as json_file:
        json_file.write(output_data)

    return output_file_path


'''TO GET COORDINATES FOR TUNISIA'''
# END PAGE SHOULD BE +1 FROM THE PREVIOUS END_PAGE
def define_coordinates_tunisia_445(pdf_path, extracted_text_json_path, start_page=10, end_page=30):   
    
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
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize variables to store the minimum and maximum coordinates
        min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

        # Iterate through each page in the PDF
        # Use enumerate to iterate over the specified range of pages only
        for page_number in range(start_page - 1, min(end_page, len(pdf.pages))):  # '-1' because pdfplumber is zero-indexed
            page = pdf.pages[page_number]
            
            # Get the height of the page
            page_height = page.height

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
                            
                            # Check if any coordinate is set to infinity
                            if any(coord == float('inf') or coord == -float('inf') for coord in [min_x0, min_y0, max_x1, max_y1]):
                                print("[-] Invalid coordinates found. Skipping entry.")
                                continue

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
                            break

    # Save the modified JSON file with coordinates added
    with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, ensure_ascii=False,  separators=(',', ': '))



'''THIS PART TAKES IMAGES BASED'''
def extract_and_process_images_tunisia(json_data, pdf_file, output_folder, output_parent_folder, resolution=200):
    # ADDING PADDING TO THE IMAGES TAKEN
    padding = 14.5
    # DICT TO STORE THE RECTS THAT WERE SKIPPED (MAINLY ONE LINERS)
    skipped_rectangles = {}
    last_processed_page = -1

    try:
        # CREATE OUTPUT FOLDER PATH
        output_folder = os.path.join(output_parent_folder, f"{pdf_path}_application_images")

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

                # VARIABLE TO GET THE COORDINATES OF THE TEXT ON A PAGE
                # ADDING PADDING AND OTHER THINGS TO ENSURE PROPER DIMENSIONS OF THE IMAGE
                coordinates = page_data['coordinates']
                x0, y0, x1, y1 = coordinates['x0'], coordinates['y0'], coordinates['x1'], coordinates['y1']
                # x0, y0 = max(x0 - padding, 0), max(y0 - padding, 0)
                # x1, y1 = min(x1 + padding, pdf_document[page_number - 1].rect.width), min(y1 + padding, pdf_document[page_number - 1].rect.height)
                x0 = coordinates['x0']- padding
                y0 = coordinates['y0'] - padding
                x1 = page_width - 40  # USING PAGE WIDTH TO AVOID ERROR OF MISSING DATA 
                y1 = coordinates['y1'] + padding
                page = pdf_document[page_number - 1]

                # Check for invalid coordinates
                # USING PREDEIFNED COORDINATES FOR INVALID RECTS
                if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:
                    rect = fitz.Rect(67, 60, page.rect.width - 40, 90)
                    skipped_rectangles[page_number] = skipped_rectangles.get(page_number, 0) + 1
                    print(f"Using predefined coordinates for skipped rectangle on page {page_number}")
                else:
                    rect = fitz.Rect(x0, y0, x1, y1)

                image = page.get_pixmap(matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect)

                # Filename with page number and counter
                image_filename_suffix = "_invalid" if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0 else ""
                # SAVING IT AS .PNG
                image_filename = os.path.join(output_folder, f"{os.path.basename(pdf_file)}_page_{page_number}_img_{image_counter}{image_filename_suffix}.png")
                print(f"Saving image to {image_filename}")  # Debugging print statement
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
                    json.dump({os.path.basename(image_filename): base64_image}, json_file, indent=4, ensure_ascii=False)

                # INCREASE THE IMAGE COUNTER BY 1
                # TO ENSURE THAT IMAGES DON'T GET OVERWRITTEN
                image_counter += 1

        # SAVING THE INFORMATION ABOUT RECTS THAT WERE SKIPPED
        for page, count in skipped_rectangles.items():
            print(f"SKIPPED {count} RECTANGLES ON PAGE {page}")

        with open(f'output_{os.path.basename(pdf_file)}.json', 'w', encoding= 'utf-8') as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    # CLOSING THE PDF TO SAVE MEMORY SPACE
    finally:
        pdf_document.close()


'''TO EXTRACT LOGOS IMAGES'''
def extract_logos_tunisia(pdf_file_path, json_path, output_folder, output_parent_folder):
    # Read JSON data
    with open(json_path, 'r', encoding='utf-8`') as file:
        data = json.load(file)

    # Open the PDF
    doc = fitz.open(pdf_file_path)
    # CREATE OUTPUT FOLDER PATH
    output_folder = os.path.join(output_parent_folder, f"{pdf_path}_logo_images")

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

                            with open(base64_filename, "w", encoding= 'utf-8') as json_file:
                                json.dump({image_filename: base64_image}, json_file, indent=4, ensure_ascii=False)
    doc.close()

    # Write the updated JSON data back to the file
    with open(json_path, 'w', encoding= 'utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return data



def update_trade_mark_keys_tunisia(input_file_path, output_file_path):
    # Read the JSON data from the file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        original_json = json.load(file)

    updated_json = {}
    for key, value in original_json.items():
        # Find the "Numéro de dépôt" line in the "content" list
        numero_de_depot = next((line for line in value["content"] if line.startswith("Numéro de dépôt : ")), None)
        
        # Extract the number/string after "Numéro de dépôt : "
        if numero_de_depot:
            new_key = numero_de_depot.split("Numéro de dépôt : ")[1].strip()
            updated_json[new_key] = value

    # Write the updated JSON data to a new file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(updated_json, file, indent=4, ensure_ascii=False)


def filter_json_data(input_file_path, output_file_path):
    # Read the JSON data from the file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        original_json = json.load(file)

    # Filter the JSON data
    filtered_json = {}
    for key, value in original_json.items():
        # Process every entry, assuming each is a trademark entry
        filtered_content_data = []
        for content in value.get("content_data", []):
            # Start with an empty dictionary
            filtered_content = {}

            # Add 'coordinates' if it exists
            if 'coordinates' in content and content['coordinates']:
                filtered_content['coordinates'] = content['coordinates']

            # Add 'binaryContent' if it exists
            if 'binaryContent' in content and content['binaryContent']:
                filtered_content['binaryContent'] = content['binaryContent']

            # Add 'deviceElements' only if it's not empty
            if 'deviceElements' in content and content['deviceElements']:
                filtered_content['deviceElements'] = content['deviceElements']

            # Append the filtered content if it's not empty
            if filtered_content:
                filtered_content_data.append(filtered_content)

        # Add the filtered content data only if it's not empty
        if filtered_content_data:
            filtered_json[key] = {"content_data": filtered_content_data}

    # Write the filtered JSON data to a new file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(filtered_json, file, indent=4, ensure_ascii=False)

# # Example usage
# input_file_path = output_file_path  # Replace with your input file path
# output_file_path = input_file_path # Replace with your desired output file path
# filter_json_data(input_file_path, output_file_path)
        
'''CALLING ALL THE OTHER FUNCTIONS'''
def image_processing_tunisia_445(pdf_file_path):
    # Step 1: Extract and segment applications
    result_file_path = extract_and_segment_applications_tunisia_445(pdf_file_path)
    print(f"Segmented data written to: {result_file_path}")

    # Step 2: Define coordinates from PDF for application screenshots
    extracted_text_json_path = f"{pdf_file_path}_result_of_segmented_text.json"
    define_coordinates_tunisia_445(pdf_file_path, extracted_text_json_path)

    # FOLDER WHERE THE IMAGES ARE SAVED
    output_parent_folder = 'Tunisia_445_images'

    # Step 3: Extract and process images
    json_data = None
    with open(extracted_text_json_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    output_folder_path = f'output_applications_image_{pdf_file_path}'
    extract_and_process_images_tunisia(json_data, pdf_file_path, output_folder_path, output_parent_folder)

    # Step 4: Extract logos
    json_path = f'output_{pdf_file_path}.json'
    output_folder_logos = f"logo_images_{pdf_file_path}"
    extract_logos_tunisia(pdf_file_path, json_path, output_folder_logos, output_parent_folder)

    # Step 5: Update trade mark keys
    input_file_path = json_path
    output_file_path = f"output_for_processing_{pdf_file_path}.json"
    update_trade_mark_keys_tunisia(input_file_path, output_file_path)

    # Step 6: Filter JSON data
    input_file_path = output_file_path
    output_file_path = input_file_path
    filter_json_data(input_file_path, output_file_path)


if __name__ == "__main__":
    # pdf_file_path = r'input_pdf\MN20230531-05.pdf'
    # # Extracting just the filename
    # pdf_file_name = os.path.basename(pdf_file_path)
    pdf_path =  'TN20230118-445.pdf'
    image_processing_tunisia_445(pdf_path)