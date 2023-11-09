import pdfplumber
import json
import fitz  # PyMuPDF
import os
from PIL import Image
import base64
import re



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


# Define a regular expression pattern to match specific text sections

# pattern = re.compile(r"\(E-01:\)[\s\S]*?(?=\(E-01:\)|$)")  #ARUBA
pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")  #BHUTAN
# pattern = re.compile(r"\(111\)[\s\S]*?(?=\(111\)|$)")  #MONGOLIA


# Path to the PDF file
pdf_file_path = "BT20230612-108.pdf"
pdf_document = fitz.open(pdf_file_path)

# This dictionary will hold all extracted text with corresponding page numbers
text_pages = {}
for page in pdf_document:
    text, pn = process_page(page)
    text_pages[pn] = text

# Concatenate the text from all pages
extracted_text = " ".join(text_pages.values())

# Find matches in the concatenated text
matches = pattern.findall(extracted_text)

# Create a dictionary to store section data and initialize section number
section_data = {}
section_num = 1

# Initialize a list to store section content data
section_content_data = []

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

    # Skip a specific section 
    if "(511) \u2013 NICE classification for goods and services" in match:
        continue

    if section_num not in section_data:
        section_data[section_num] = {"page_number": [pn + 1 for pn in page_nums] # Adding 1 to adjust the page number
                                     , "content": [],
                                     "content_data": []
                                    }

    # Split the matched text into lines and add them to the section data
    content_lines = [line for line in match.split("\n") if line.strip()]
    section_data[section_num]["content"].extend(content_lines)

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
    section_data[section_num]["content_data"].extend(current_content_data)
    
    # Call the correction function for the current section
    #  Removing the HEADING from the extracted text
    delimiter = 'Successfull Examination Marks'
    section_data[section_num]["content_data"] = correct_text_segmentation(section_data[section_num]["content_data"], delimiter)
    
    # Call the merge_duplicate_pages function to join text on the same page into one
    section_data[section_num]["content_data"] = merge_duplicate_pages(section_data[section_num]["content_data"])
    
    # Split the text into lines (segments) for each entry in content_data
    for entry in section_data[section_num]["content_data"]:
        text = entry["text"]
        lines = text.split('\n')
        
        # Remove empty strings from the 'lines' list
        lines = [line for line in lines if line.strip() != ""]
        
        # Update the "text" value for the current entry to contain the split lines
        entry["text"] = lines
        
    section_num += 1

# Serialize the section data to a JSON format
output_data = json.dumps(section_data, ensure_ascii=False, indent=4)

# Write the JSON data to a file
with open(f"{pdf_file_path}_result_latest_version.json", "w", encoding="utf-8") as json_file:
    json_file.write(output_data)


def define_coordinates_from_pdf(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
    # Load the JSON file containing the previously extracted text (if it exists)
    try:
        with open(extracted_text_json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        print("[-] Existing file not found")
        return
    except Exception as e:
        print(e)
        return

    # Extract text from the PDF and store it in extracted_text_dict
    with pdfplumber.open(pdf_path) as pdf:
        min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

        for page_number, page in enumerate(pdf.pages, start=1):
            extracted_text_dict[str(page_number)] = {
                "page_number": page_number,
                "extracted_texts": []
            }
            print("[*] page number:", page_number)
            print("----------------------")

            # lines
            page = pdf.pages[page_number - 1]  # Pages are 0-based index

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

            for page_data_key, page_data in existing_data.items():
                if not page_data.get("content_data"):
                    continue

                for content_entry in page_data["content_data"]:
                    start = content_entry["text"][0]
                    end = content_entry["text"][-1]

                    match = False

                    min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

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

                        # comparing texts
                        end_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in end.split(" ") if i]

                        if end_found and match:
                            extracted_text_dict[str(page_number)]["extracted_texts"].append({
                                "extracted_text": '\n'.join(content_entry['text']),
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1,
                            })
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
        json.dump(existing_data, json_file, indent=4, separators=(',', ': '))

    # Save the defined coordinates to a new JSON file with formatting
    with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
        json.dump(extracted_text_dict, output_json_file, indent=4, separators=(',', ': '))

        
# Example usage:
pdf_path = "BT20230612-108.pdf"  # Replace with the path to your PDF file
extracted_text_json_path = "BT20230612-108.pdf_result_latest_version.json"  # This is the JSON input file
output_json_path = "defined_coordinates_trial.json"  # This file is created as the output
define_coordinates_from_pdf(
    pdf_path, extracted_text_json_path, output_json_path)


def extract_and_save_image(pdf_file, coordinates_file, output_folder, resolution=200):
    padding = 14.5
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
                image_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.png")
                image.save(image_filename)
                print(f"Extracted image saved as {image_filename}")

                # Now, convert the PNG image to GIF format using Pillow
                gif_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.gif")
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
                base64_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.json")
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



if __name__ == "__main__":
    pdf_file = "BT20230612-108.pdf"
    coordinates_file = "defined_coordinates_trial.json"
    output_folder = "OUTPUT_SCREENSHOTS_ON_ZUHAIR_SCRIPT_WITH_PNG_GIF_B64_TRIAL"
    resolution = 200
    extract_and_save_image(pdf_file, coordinates_file, output_folder, resolution)
