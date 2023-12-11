import fitz
import re
import json

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

pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")  #BHUTAN
# pattern = re.compile(r"\(111\)[\s\S]*?(?=\(111\)|$)")  #MONGOLIA


# Path to the PDF file
# Change this to the country name
# Make sure the pdf file is also in the same folder as the script
pdf_file_path = "BT20211202-100.pdf"
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