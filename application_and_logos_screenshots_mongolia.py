import pdfplumber
import json
import fitz  # PyMuPDF
import os
from PIL import Image
import base64
import re
import io

#  Define a function to process a page and return its text and page number
def process_page_for_application_screenshots_mongolia(page):
    page_text = page.get_text("text")
    return page_text, page.number

'''REMOVES STRINGS FROM START AND END IRRESPECIVE OF SEQUENCE OF LIST'''
def correct_text_segmentation_for_application_screenshots_mongolia(content_data, delimiter, texts_to_remove, texts_to_remove_start):
    corrected_data = []
    for page_text in content_data:
        text = page_text['text']

        # Repeatedly check and remove any starting strings that match, regardless of order
        while any(text.startswith(text_to_remove_start) for text_to_remove_start in texts_to_remove_start):
            for text_to_remove_start in texts_to_remove_start:
                if text.startswith(text_to_remove_start):
                    text = text[len(text_to_remove_start):].lstrip()

        # Repeatedly check and remove any ending strings that match, regardless of order
        while any(text.endswith(text_to_remove) for text_to_remove in texts_to_remove):
            for text_to_remove in texts_to_remove:
                if text.endswith(text_to_remove):
                    text = text[:-len(text_to_remove)].rstrip()

        # Check if the delimiter is at the end and remove it
        if text.endswith(delimiter):
            text = text[:-len(delimiter)].rstrip()

        # Add the possibly corrected text to the corrected_data
        corrected_data.append({
            'text_on_page': page_text['text_on_page'],
            'text': text,
        })

    return corrected_data

def correct_text_in_entire_text(content_data, strings_to_remove):
    corrected_data = []

    for page_text in content_data:
        text = page_text['text']

        # Check and remove any specified strings in the entire text
        for string_to_remove in strings_to_remove:
            text = text.replace(string_to_remove, '')

        # Check if the delimiter is at the end and remove it
        delimiter = 'your_delimiter'  # Replace 'your_delimiter' with the actual delimiter you are using
        if text.endswith(delimiter):
            text = text[:-len(delimiter)].rstrip()

        # Add the possibly corrected text to the corrected_data
        corrected_data.append({
            'text_on_page': page_text['text_on_page'],
            'text': text,
        })

    return corrected_data

def merge_duplicate_pages_for_application_screenshots_mongolia(content_data):
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

def post_process_lines_for_application_screenshots_mongolia(lines):
    # New function to post-process lines
    processed_lines = []
    buffer_line = ""

    for line in lines:
        if re.match(r"\(\d+\)", line) and ":" not in line:
            buffer_line = line  # Start buffering this line
        elif buffer_line:
            processed_lines.append(buffer_line + " " + line)
            buffer_line = ""  # Clear the buffer
        else:
            processed_lines.append(line)  # No buffer_line, add the current line as it is

    # Ensure the last buffered line is added
    if buffer_line:
        processed_lines.append(buffer_line)

    return processed_lines

def post_process_content_for_application_screenshots_mongolia(content_list):
    processed_content = []
    buffer_line = ""

    for line in content_list:
        if re.match(r"\(\d+\)", line) and ":" not in line:
            buffer_line = line  # Start buffering this line
        elif buffer_line:
            processed_content.append(buffer_line + " " + line)
            buffer_line = ""  # Clear the buffer
        else:
            processed_content.append(line)  # No buffer_line, add the current line as it is

    # Ensure the last buffered line is added
    if buffer_line:
        processed_content.append(buffer_line)

    return processed_content

def split_text_by_newline_for_application_screenshots_mongolia(content_data):
    for entry in content_data:
        # Split the text within each entry by newline
        split_text = entry["text"].split('\n')
        # Filter out any empty strings that may result from consecutive newline characters
        split_text = [line.strip() for line in split_text if line.strip()]
        # Update the entry with the split text
        entry["text"] = split_text
    return content_data


def extract_and_segment_applications_mongolia(pdf_file_path):
    # # # Start of the main script
    pattern = re.compile(r"\(111\)[\s\S]*?(?=\(111\)|$)")  #MONGOLIA
      
    pdf_document = fitz.open(pdf_file_path)

    # # TO STORE IMAGE LOGOS
    # output_dir_image_logo = f"{pdf_file_path}_image_logos"

    # This dictionary will hold all extracted text with corresponding page numbers
    text_pages = {}
    for page in pdf_document:
        text, pn = process_page_for_application_screenshots_mongolia(page)
        text_pages[pn] = text

    # Concatenate the text from all pages
    extracted_text = " ".join(text_pages.values())

    # Find matches in the concatenated text
    matches = pattern.findall(extracted_text)

    # Create a dictionary to store section data and initialize section number
    section_data = {}
    section_num = 1
    # TO ADD THE WORD (tradeMark) IN THE BEGINNING OF THE JSON FILE
    section_prefix = "tradeMark"

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
                # new_pn_matching_PDF = pn + 1
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
        # Now process those content lines to join lines that should be together
        content_lines = post_process_content_for_application_screenshots_mongolia(content_lines)
        section_data[section_key]["content"].extend(content_lines)

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
                # Construct the dictionary with the "image" key
                current_content_data.append({
                    "text_on_page": pn + 1,  # Adding 1 to adjust the page number
                    "text": segment.strip(),
                })

                
                # print(current_content_data)
            # Update segment_start for the next page
            segment_start = segment_end
        

        # Add the segmented content data to the section data
        section_data[section_key]["content_data"].extend(current_content_data)

        # Call the correction function for the current section
        #  Removing the HEADING from the extracted text
        delimiter = "\n  \n \nМонгол Улсын Оюуны Өмчийн Газар \n \nУЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ"
        texts_to_remove = ["REGISTERED", "REGISTERED TRADEMARK","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ" ,"УЛСЫН БҮРТГЭЛД АВСАН" ,"УЛСЫН" ,"УЛСЫН БҮРТГЭЛД", "УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ", "Intellectual Property Office of Mongolia", "Монгол Улсын Оюуны Өмчийн Газар"]
        texts_to_remove_start = ["Монгол Улсын","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","Оюуны Өмчийн Газар","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","Өмчийн Газар","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","Газар","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","Улсын Оюуны Өмчийн Газар","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ",",Өмчийн Газар","Монгол Улсын Оюуны Өмчийн Газар","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ", "АВСАН БАРААНЫ ТЭМДЭГ", "ТЭМДЭГ","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","БАРААНЫ ТЭМДЭГ", "REGISTERED TRADEMARK", "TRADEMARK", "REGISTERED"]
        strings_to_remove = texts_to_remove_start

        section_data[section_key]["content_data"] = correct_text_segmentation_for_application_screenshots_mongolia(section_data[section_key]["content_data"], delimiter, texts_to_remove, texts_to_remove_start)
        section_data[section_key]["content_data"] = correct_text_in_entire_text(section_data[section_key]["content_data"], strings_to_remove)

        # Call the merge_duplicate_pages_for_application_screenshots_mongolia function to join text on the same page into one
        section_data[section_key]["content_data"] = merge_duplicate_pages_for_application_screenshots_mongolia(section_data[section_key]["content_data"])

        # Call the post_process_lines_for_application_screenshots_mongolia function to correct the segmentation
        for entry in section_data[section_key]["content_data"]:
            lines = entry["text"].split('\n')
            lines = post_process_lines_for_application_screenshots_mongolia(lines)
            entry["text"] = "\n".join(lines)

        # Now call the split_text_by_newline_for_application_screenshots_mongolia function to split the text by newlines
        section_data[section_key]["content_data"] = split_text_by_newline_for_application_screenshots_mongolia(section_data[section_key]["content_data"])

        section_num += 1


    # Serialize the section data to a JSON format
    output_data = json.dumps(section_data, ensure_ascii=False, indent=4)

    output_file_path =  f'{pdf_file_path}_result_of_segmented_text.json'

    # Write the JSON data to a file
    with open(output_file_path, "w", encoding="utf-8") as json_file:
        json_file.write(output_data)
    
    return output_file_path


'''
IGNORES HEADINGS BEING CAPTURED BUT IMAGES AFTER THE NEW HEADINGS ARE BAD,
WITHOUT THIS WE ARE GETTING IMAGES BUT ALSO GETTING MORE IMAGES
'''

ignore_text = "УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ"

# EXTRACTING COORDINATES OF TEXT FROM THE PDF
def define_coordinates_from_pdf_for_application_screenshots_mongolia(pdf_path, extracted_text_json_path):
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
                    
                    # Skip processing if the extracted text matches the ignored text
                    if '\n'.join(content_entry['text']) == ignore_text:
                        continue
                        
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
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1
                            }
                            break

    # Save the modified JSON file with coordinates added
    with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))


'''THIS PART TAKES IMAGES BASED'''
def extract_and_process_images_mongolia(json_data, pdf_file, output_folder, output_parent_folder, resolution=200):
    # ADDING PADDING TO THE IMAGES TAKEN
    padding = 14.5
    # DICT TO STORE THE RECTS THAT WERE SKIPPED (MAINLY ONE LINERS)
    skipped_rectangles = {}
    last_processed_page = -1
    #  TO TAKE PICTURE OF ENTIRE PAGE (FOR MONGOLIA)
    predefined_rect = fitz.Rect(54, 124, 541, 768)
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
                    print(f"No coordinates for {trade_mark}, using predefined rectangle.")
                    page_data['coordinates'] = {
                        'x0': predefined_rect.x0,
                        'y0': predefined_rect.y0,
                        'x1': predefined_rect.x1,
                        'y1': predefined_rect.y1
                    }
         
        # The coordinates are in the format (x0, y0, x1, y1) - top left and bottom right corners.
        # x0 is the horizontal coordinate (from the left) of the top-left corner. [LEFT VERTICLE LINE goes LEFT(lower number) or RIGHT (higher number)]
        # y0 is the vertical coordinate (from the top) of the top-left corner. [TOP HORIZONTAL LINE goes UP (lower number) and DOWN(higher number) ]
        # x1 is the horizontal coordinate (from the left) of the bottom-right corner. [RIGHT VERTICLE LINE goes LEFT (lower number) or RIGHT (higher number)]
        # y1 is the vertical coordinate (from the top) of the bottom-right corner. [BOTTOM HORIZONTAL LINE goes UP(lower number) or DOWN(higher number)]
       
                # VARIABLE TO STORE THE PAGE NUMBER ON WHICH THE TEXT IS 
                page_number = page_data['text_on_page']

                # IF PAGE NUMBER IS NOT THE LAST PROCESSED PAGE 
                # THEN PAGE NUMBER WOULD BE THE SAME
                if page_number != last_processed_page:
                    image_counter = 0
                    last_processed_page = page_number

                # VARIABLE TO GET THE COORDINATES OF THE TEXT ON A PAGE
                # ADDING PADDING AND OTHER THINGS TO ENSURE PROPER DIMENSIONS OF THE IMAGE
                coordinates = page_data['coordinates']
                x0, y0, x1, y1 = coordinates['x0'], coordinates['y0'], coordinates['x1'], coordinates['y1']
      
                x0 = coordinates['x0'] - padding
                y0 = coordinates['y0'] - 30
                x1 = coordinates['x1'] + 40  
                y1 = coordinates['y1'] + padding


                # page = pdf_document[page_number - 1]
                page = pdf_document[page_number - 1]

                rect = fitz.Rect(x0, y0, x1, y1)
                image = page.get_pixmap(matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect)

                # Filename with page number and counter
                image_filename_suffix = "_predefined" if 'coordinates' not in page_data else ""
                # SAVING IT AS .PNG
                image_filename = os.path.join(output_folder, f"{os.path.basename(pdf_file)}_page_{page_number}_img_{image_counter}{image_filename_suffix}.png")
                print(f"Saving image to {image_filename}")  # Debugging print statement
                try:
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
                
                except Exception as e:
                    print(f"An error occurred while saving the image or converting to base64: {e}")

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


def extract_logos_mongolia(input_file_path, json_path, output_folder, output_parent_folder):
    # Read JSON data
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Open the PDF
    doc = fitz.open(input_file_path)
    
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

                            with open(base64_filename, "w", encoding='utf-8') as json_file:
                                json.dump({image_filename: base64_image}, json_file, ensure_ascii=False, indent=4)
    doc.close()

    # Write the updated JSON data back to the file
    with open(json_path, 'w', encoding= 'utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    return data


def update_trade_mark_keys_mongolia(input_file_path, output_file_path):
    # Read the JSON data from the file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        original_json = json.load(file)

    updated_json = {}
    for key, value in original_json.items():
        # Find the "(111) Улсын бүртгэлийн дугаар" line in the "content" list
        application_number = next((line for line in value["content"] if line.startswith("(111) Улсын бүртгэлийн дугаар  : ")), None)
        
        # Extract the number/string after "(111) Улсын бүртгэлийн дугаар : "
        if application_number:
            new_key = application_number.split("(111) Улсын бүртгэлийн дугаар  : ")[1].strip()
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



def cleaning_multiple_entry_mongolia(input_file_path, output_file_path):
    # Open the JSON file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    for key in json_data.keys():
        content_data = json_data[key].get("content_data", [])
        if content_data and 'deviceElements' in content_data[0]:
            modified_entries = []
            for entry in content_data[1:]:
                if 'deviceElements' in entry:
                    modified_entries.append(entry)
            
            # Remove the identified entries from the 'content_data' list
            for entry in modified_entries:
                content_data.remove(entry)

    # updating the JSON file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)



'''CALLING ALL THE OTHER FUNCTIONS'''
def image_processing_Mongolia(pdf_file_path):
    # Step 1: Extract and segment applications
    result_file_path = extract_and_segment_applications_mongolia(pdf_file_path)
    print(f"Segmented data written to: {result_file_path}")

    # Step 2: Define coordinates from PDF for application screenshots
    extracted_text_json_path = f"{pdf_file_path}_result_of_segmented_text.json"
    define_coordinates_from_pdf_for_application_screenshots_mongolia(pdf_file_path, extracted_text_json_path)

    # FOLDER WHERE THE IMAGES ARE SAVED
    output_parent_folder = 'Mongolia_images'

    # Step 3: Extract and process images
    json_data = None
    with open(extracted_text_json_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    output_folder_path = f'output_applications_image_{pdf_file_path}'
    extract_and_process_images_mongolia(json_data, pdf_file_path, output_folder_path, output_parent_folder)

    # Step 4: Extract logos
    json_path = f'output_{pdf_file_path}.json'
    output_folder_logos = f"logo_images_{pdf_file_path}"
    extract_logos_mongolia(pdf_file_path, json_path, output_folder_logos, output_parent_folder)

    # Step 5: Update trade mark keys
    input_file_path = json_path
    output_file_path = f"output_for_processing_{pdf_file_path}.json"
    update_trade_mark_keys_mongolia(input_file_path, output_file_path)

    # Step 6: Filter JSON data
    input_file_path = output_file_path
    output_file_path = input_file_path
    filter_json_data(input_file_path, output_file_path)

    # Step 7: Removing duplicate entries
    input_file_path = output_file_path  # Replace with your input file path
    output_file_path = input_file_path # Replace with your desired output file path
    cleaning_multiple_entry_mongolia(input_file_path, output_file_path)

if __name__ == "__main__":
    # pdf_file_path = r'input_pdf\MN20230531-05.pdf'
    # # Extracting just the filename
    # pdf_file_name = os.path.basename(pdf_file_path)
    pdf_path =  'MN20230531-05.pdf'
    image_processing_Mongolia(pdf_path)