# import pdfplumber
import json
import fitz  # PyMuPDF
# import os
# from PIL import Image
# import base64
import re


# Define a function to process a page and return its text and page number
def process_page_for_application_screenshots_bhutan(page):
    page_text = page.get_text("text")
    return page_text, page.number


def correct_text_segmentation_for_application_screenshots_bhutan(content_data, delimiter):
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


def merge_duplicate_pages_for_application_screenshots_bhutan(content_data):
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


# # Define a regular expression pattern to match specific text sections
# pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")  #BHUTAN


# # Path to the PDF file
# # pdf_file_path = "BT20211006-98.pdf"
# pdf_document = fitz.open(pdf_file_path)

# # This dictionary will hold all extracted text with corresponding page numbers
# text_pages = {}
# for page in pdf_document:
#     text, pn = process_page_for_application_screenshots_bhutan(page)
#     text_pages[pn] = text

# # Concatenate the text from all pages
# extracted_text = " ".join(text_pages.values())

# # Find matches in the concatenated text
# matches = pattern.findall(extracted_text)

# # Create a dictionary to store section data and initialize section number
# section_data = {}
# section_num = 1

# # Initialize a list to store section content data
# section_content_data = []

# # Iterate through the matches
# for match in matches:
#     start_index = extracted_text.find(match)

#     # Determine the pages the match spans
#     # Create an empty list to store the page numbers where the match appears
#     page_nums = []
#     # Initialize a variable to keep track of the current position in the extracted text
#     current_pos = 0 
#     # Iterate through each page and its corresponding text
#     for pn, txt in text_pages.items():
#         # Update the current position by adding the length of the text on the current page
#         current_pos += len(txt)
#         if start_index < current_pos:
#             # If the starting index of the match is less than the current position, it means the match spans this page
#             # Add the page number to the list of page numbers where the match appears
#             # Increase the pn (page_numer) by 1 to match page number in PDF
# #             new_pn_matching_PDF = pn + 1
#             page_nums.append(pn)
#             # If the current position is greater than the end of the match, 
#             # it means the match doesn't span further pages
#             if current_pos > start_index + len(match):
#                 break

#     # Skip a specific section 
#     if "(511) \u2013 NICE classification for goods and services" in match:
#         continue

#     if section_num not in section_data:
#         section_data[section_num] = {"page_number": [pn + 1 for pn in page_nums] # Adding 1 to adjust the page number
#                                     , "content": [],
#                                     "content_data": []
#                                     }

#     # Split the matched text into lines and add them to the section data
#     content_lines = [line for line in match.split("\n") if line.strip()]
#     section_data[section_num]["content"].extend(content_lines)

#     # Initialize a pointer for the current start of the segment
#     segment_start = start_index

#     # Temporary storage for the segmented content for this match
#     current_content_data = []

#     # Iterate through the pages the match spans
#     for pn in page_nums:
#         # Determine where the segment for this page ends
#         segment_end = min(segment_start + len(text_pages[pn]), start_index + len(match))

#         # Check if segment_end is cutting a word. If yes, move it back to the last space.
#         while extracted_text[segment_end] not in [" ", "\n", "\t"] and segment_end > segment_start:
#             segment_end -= 1

#         # Extract the segment of the match that lies within this page
#         segment = extracted_text[segment_start:segment_end]

#         # If this segment contains part of the match, add it to the current_content_data
#         if segment.strip():
#             current_content_data.append({
#                 "text_on_page": pn + 1, # Adding 1 to adjust the page number
#                 "text": segment.strip()
#             })

#         # Update segment_start for the next page
#         segment_start = segment_end
    
#     # Add the segmented content data to the section data
#     section_data[section_num]["content_data"].extend(current_content_data)
    
#     # Call the correction function for the current section
#     #  Removing the HEADING from the extracted text
#     delimiter = 'Successfull Examination Marks'
#     section_data[section_num]["content_data"] = correct_text_segmentation_for_application_screenshots_bhutan(section_data[section_num]["content_data"], delimiter)
    
#     # Call the merge_duplicate_pages_for_application_screenshots_bhutan function to join text on the same page into one
#     section_data[section_num]["content_data"] = merge_duplicate_pages_for_application_screenshots_bhutan(section_data[section_num]["content_data"])
    
#     # TO CHECK IF (540): is the last input in the 'text' key
#     # IF THIS IS THE CASE THEN SWAP [-1] and [-2] values
#     for section in section_data.values():
#         for entry in section["content_data"]:
#             # Check if the 'text' key exists and has at least two elements
#             if 'text' in entry and len(entry['text']) >= 2:
#                 # Check if the last element matches the specific pattern
#                 if entry['text'][-1].startswith("(540):"):
#                     # Swap the last and second-to-last elements
#                     entry['text'][-1], entry['text'][-2] = entry['text'][-2], entry['text'][-1]

                
#     # Split the text into lines (segments) for each entry in content_data
#     for entry in section_data[section_num]["content_data"]:
#         text = entry["text"]
#         lines = text.split('\n')
        
#         # Remove empty strings from the 'lines' list
#         lines = [line for line in lines if line.strip() != ""]
        
#         # Update the "text" value for the current entry to contain the split lines
#         entry["text"] = lines
        
#     section_num += 1

# # Serialize the section data to a JSON format
# output_data = json.dumps(section_data, ensure_ascii=False, indent=4)

# # Write the JSON data to a file
# with open(f"{pdf_file_path}_result_of_segmented_text.json", "w", encoding="utf-8") as json_file:
#     json_file.write(output_data)

################## CODE CLEANING MONGOLIA #####################################################

def process_page(page):
    page_text = page.get_text("text")
    return page_text, page.number

def post_process_lines(lines):
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

def post_process_content(content_list):
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

'''REMOVES STRINGS FROM START AND END IRRESPECIVE OF SEQUENCE OF LIST'''
def correct_text_segmentation(content_data, delimiter, texts_to_remove, texts_to_remove_start):
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
            'text': text
        })

    return corrected_data

def split_text_by_newline(content_data):
    for entry in content_data:
        # Split the text within each entry by newline
        split_text = entry["text"].split('\n')
        # Filter out any empty strings that may result from consecutive newline characters
        split_text = [line.strip() for line in split_text if line.strip()]
        # Update the entry with the split text
        entry["text"] = split_text
    return content_data

def find_and_fix_data(pdf_file):
    def fix_structure(data):
        for section, section_data in data.items():
            i = 0
            while i < len(section_data):
                if section_data[i].startswith('(') and not section_data[i].startswith('(170)'):
                    key = section_data[i]
                    if i + 1 < len(section_data):
                        value = section_data[i + 1]
                        # Check if the value already has a colon
                        if not value.startswith(":"):
                            section_data[i] = f"{key} : {value}"
                        else:
                            section_data[i] = f"{key} {value}"
                        del section_data[i + 1]
                i += 1

    exclude_words = ["Улсын", "бүртгэлийн", "дугаар", "Бүртгэлийн", "хүчинтэй", "байх", "хугацаа", "Мэдүүлгийн",
                     "улсын", "анхдагч", "огноо", "Давамгайлах", "Хэвлэлийн", "Эзэмшигчийн", "Итгэмжлэгдсэн",
                     "төлөөлөгчийн", "Хамгаалагдахгүй", 'үг,', "дүрс", "Барааны", "тэмдгийн", "дүрсийн", "олон",
                     "улсын", "ангилал", "дардас.", "нэр", "Барааны", "тэмдгийн", "өнгийн", "ялгаа", "Барааны",
                     "тэмдгийн", "бараа,", "үйлчилгээний", "олон", "улсын", "ангилал,", "ашиглах", "бараа",
        'Монгол', 'Оюуны', 'Өмчийн', 'Газар',"үйлчилгээний", "тэмдэг.", 'Нэр ','УЛСЫН', 'БҮРТГЭЛД','БАРААНЫ','ТЭМДЭГ','АВСАН']

    doc = fitz.open(pdf_file)
    found_data = {}
    in_section = False
    current_section = []
    section_counter = 1

    for page in range(len(doc)):
        text = doc[page].get_text()

        lines = text.split("\n")

        for line in lines:
            # Exclude specific words from the line before processing
            words = line.split()
            filtered_words = [word for word in words if word not in exclude_words]
            updated_line = ' '.join(filtered_words)

            if "(111)" in line:
                if in_section:
                    found_data[f"tradeMark {section_counter}"] = current_section
                    current_section = []
                    section_counter += 1

                in_section = True

            if in_section and updated_line.strip():  # Check for non-empty lines
                current_section.append(updated_line)

    if in_section:
        found_data[f"tradeMark {section_counter}"] = current_section

    doc.close()

    # Fix the data structure
    fix_structure(found_data)

    # Save the modified data into a JSON file section-wise
    output_data = {}
    for section, section_data in found_data.items():
        output_data[section] = section_data

    with open('pdf.json', 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)


def is_header_line_tunisia(line):
    # Add conditions to identify header lines
    header_keywords = ["Muwassafat  N° 424"]
    return any(keyword in line for keyword in header_keywords)




