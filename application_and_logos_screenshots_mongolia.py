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
            'image' : 'test_1'
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

def extract_logo_images_from_pdf_mongolia(pdf_file_path, output_dir_image_logo, target_page, min_width=150, min_height=10):
    # open the file
    pdf_file = fitz.open(pdf_file_path)

    # Create the output directory if it does not exist
    if not os.path.exists(output_dir_image_logo):
        os.makedirs(output_dir_image_logo)

    # Check if the target page is within the valid range
    if target_page < 0 or target_page >= len(pdf_file):
        # print(f"[!] Invalid target page {target_page}. Please provide a valid page index.")
        pdf_file.close()
        return

    # Get the target page
    page = pdf_file[target_page]

    # Get image list
    image_list = page.get_images(full=True)

    # # Print the number of images found on this page
    # if image_list:
    #     print(f"[+] Found a total of {len(image_list)} images on page {target_page}")
    # else:
    #     print(f"[!] No images found on page {target_page}")

    # Initialize logo_image_base64 with an empty list
    logo_image_base64 = ""

    # Iterate over the images on the page
    for image_index, img in enumerate(image_list, start=1):
        # Get the XREF of the image
        xref = img[0]
        # Extract the image bytes
        base_image = pdf_file.extract_image(xref)
        image_bytes = base_image["image"]
        # Get the image extension
        image_ext = base_image["ext"]
        # Load it to PIL
        logo_image = Image.open(io.BytesIO(image_bytes))
        # Check if the image meets the minimum dimensions
        if logo_image.width >= min_width and logo_image.height >= min_height:
            # Save the image as PNG
            png_path = os.path.join(output_dir_image_logo, f"image{target_page + 1}_{image_index}.png")
            logo_image.save(open(png_path, "wb"), format="png".upper())

            # Save the image as GIF
            gif_path = os.path.join(output_dir_image_logo, f"image{target_page + 1}_{image_index}.gif")
            logo_image.save(open(gif_path, "wb"), format="gif".upper())

            # Convert image to Base64
            current_logo_image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            # Check if the image meets the minimum dimensions
            if logo_image.width >= min_width and logo_image.height >= min_height:
                # Assign the Base64 representation only if the image meets the size requirements
                logo_image_base64 = current_logo_image_base64

            # Save Base64 to JSON
            json_data = {
                "deviceElements": logo_image_base64
            }

            json_path = os.path.join(output_dir_image_logo, f"image{target_page + 1}_{image_index}.json")
            with open(json_path, "w") as json_file:
                json.dump(json_data, json_file)
        else:
            print(f"[-] Skipping image {image_index} on page {target_page} due to its small size.")

    return logo_image_base64


# # # Start of the main script
pattern = re.compile(r"\(111\)[\s\S]*?(?=\(111\)|$)")  #MONGOLIA

pdf_file_path = "MN20230630-06.pdf"  # Replace with your actual PDF file path
pdf_document = fitz.open(pdf_file_path)

# TO STORE IMAGE LOGOS
output_dir_image_logo = f"{pdf_file_path}_image_logos"

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

        
        # print(logo_data)

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
    texts_to_remove_start = ["БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ", "АВСАН БАРААНЫ ТЭМДЭГ", "ТЭМДЭГ","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","БАРААНЫ ТЭМДЭГ", "REGISTERED TRADEMARK", "TRADEMARK", "REGISTERED"]
    section_data[section_key]["content_data"] = correct_text_segmentation_for_application_screenshots_mongolia(section_data[section_key]["content_data"], delimiter, texts_to_remove, texts_to_remove_start)

    # Call the merge_duplicate_pages_for_application_screenshots_mongolia function to join text on the same page into one
    section_data[section_key]["content_data"] = merge_duplicate_pages_for_application_screenshots_mongolia(section_data[section_key]["content_data"])

    # Call the post_process_lines_for_application_screenshots_mongolia function to correct the segmentation
    for entry in section_data[section_key]["content_data"]:
        lines = entry["text"].split('\n')
        lines = post_process_lines_for_application_screenshots_mongolia(lines)
        entry["text"] = "\n".join(lines)

    # Now call the split_text_by_newline_for_application_screenshots_mongolia function to split the text by newlines
    section_data[section_key]["content_data"] = split_text_by_newline_for_application_screenshots_mongolia(section_data[section_key]["content_data"])
    # print(section_data)

    # SAVE THE LOGO BASE64 IN A VARIABLE
    logo_image_base64 = extract_logo_images_from_pdf_mongolia(pdf_file_path, output_dir_image_logo, pn, min_width=150, min_height=10)
    
    # CREATING A NEW KEY TO STORE DEVICE ELEMENTS (BASE64 OF LOGOS)
    new_key = "deviceElements"
    new_data = logo_image_base64
    # LOOPING THROUGH THE JSON FILE TO ADD THE NEW KEY INSIDE 'CONTENT_DATA'
    for item in section_data[section_key]["content_data"]:
        item[new_key] = new_data
    
    # print(section_data)
    section_num += 1


# Serialize the section data to a JSON format
output_data = json.dumps(section_data, ensure_ascii=False, indent=4)
# print(output_data)
# Write the JSON data to a file
with open(f"{pdf_file_path}_result_of_segmented_text.json", "w", encoding="utf-8") as json_file:
    json_file.write(output_data)

# Close the PDF document
# pdf_document.close()

# '''
# IGNORES HEADINGS BEING CAPTURED BUT IMAGES AFTER THE NEW HEADINGS ARE BAD,
# WITHOUT THIS WE ARE GETTING IMAGES BUT ALSO GETTING MORE IMAGES
# '''

ignore_text = "УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ"

# EXTRACTING COORDINATES OF TEXT FROM THE PDF
def define_coordinates_from_pdf_for_application_screenshots_mongolia(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
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
            # Initialize a dictionary to store extracted text for the current page
            extracted_text_dict[str(page_number)] = {
                "page_number": page_number,
                "extracted_texts": []
            }
            print("[*] page number:", page_number)
            print("----------------------")

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
                            break

    # Save the modified JSON file with coordinates added
    with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

    # Save the defined coordinates to a new JSON file with formatting
    with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
        json.dump(extracted_text_dict, output_json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

# Example usage:
pdf_path = pdf_file_path  # Replace with the path to your PDF file, THIS VARIABLE IS IN THE STARTING OF THE SCRIPT
extracted_text_json_path = f"{pdf_file_path}_result_of_segmented_text.json"  # This is the JSON input file

'''DEFINED COORDINATES.JSON IS NOT NEEDED'''
output_json_path = f"{pdf_file_path}_defined_coordinates.json"  # This file is created as the output
define_coordinates_from_pdf_for_application_screenshots_mongolia(
    pdf_path, extracted_text_json_path, output_json_path)


'''THIS PART TAKES IMAGES BASED'''
def extract_and_process_images_mongolia(json_data, pdf_file, output_folder, resolution=200):
    # ADDING PADDING TO THE IMAGES TAKEN
    padding = 14.5
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

                # IF PAGE NUMBER IS NOT THE LAST PROCESSED PAGE 
                # THEN PAGE NUMBER WOULD BE THE SAME
                if page_number != last_processed_page:
                    image_counter = 0
                    last_processed_page = page_number

                # VARIABLE TO GET THE COORDINATES OF THE TEXT ON A PAGE
                # ADDING PADDING AND OTHER THINGS TO ENSURE PROPER DIMENSIONS OF THE IMAGE
                coordinates = page_data['coordinates']
                x0, y0, x1, y1 = coordinates['x0'], coordinates['y0'], coordinates['x1'], coordinates['y1']
                x0, y0 = max(x0 - padding, 0), max(y0 - 30, 0)
                x1, y1 = min(x1 + padding, pdf_document[page_number - 1].rect.width), min(y1 + padding, pdf_document[page_number - 1].rect.height)

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


# Load the entire JSON file
file_path = f'{pdf_file_path}_result_of_segmented_text.json'
with open(file_path, 'r', encoding= 'utf-8') as file:
    json_data = json.load(file)

# Example usage
pdf_file_path = pdf_file_path  # Replace with PDF file path
output_folder_path = f'output_applications_image_{pdf_file_path}'  # Replace with output folder path
extract_and_process_images_mongolia(json_data, pdf_file_path, output_folder_path)