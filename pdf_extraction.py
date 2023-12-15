import fitz
import re
import json
from image_processing import *
from code_cleaning import *
from structure_mongolia import process_bulk_trademarks
import os 
from country.bhutan import application_and_logos_screenshots_bhutan
from country.bhutan import section_wise_04

resolution = 200

def bhutan_pdf_parser(pdf_file_path):
    process_screenshots_bhutan(pdf_file_path)
    generate_json_bhutan(pdf_file_path)

def mongolia_pdf_parser(pdf_file_path):
    process_screenshots_bhutan(pdf_file_path)
    generate_json_bhutan(pdf_file_path)

def tunisia_pdf_parser(pdf_file_path):
    process_screenshots_bhutan(pdf_file_path)
    generate_json_bhutan(pdf_file_path)
    

























def bhutan_pdf_extraction(pdf_file_path):
    
    pdf_document = fitz.open(pdf_file_path)
    pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")

    text_pages = {}
    for page in pdf_document:
        text, pn = process_page_for_application_screenshots_bhutan(page)
        text_pages[pn] = text
    # Concatenate the text from all pages
    extracted_text = " ".join(text_pages.values())
    # Find matches in the concatenated text
    matches = pattern.findall(extracted_text)

    section_data = {}
    section_num = 1


    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text('text')

        matches = pattern.findall(page_text)

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
        section_data[section_num]["content_data"] = correct_text_segmentation_for_application_screenshots_bhutan(section_data[section_num]["content_data"], delimiter)
        
        # Call the merge_duplicate_pages_for_application_screenshots_bhutan function to join text on the same page into one
        section_data[section_num]["content_data"] = merge_duplicate_pages_for_application_screenshots_bhutan(section_data[section_num]["content_data"])
        
        # TO CHECK IF (540): is the last input in the 'text' key
        # IF THIS IS THE CASE THEN SWAP [-1] and [-2] values
        for section in section_data.values():
            for entry in section["content_data"]:
                # Check if the 'text' key exists and has at least two elements
                if 'text' in entry and len(entry['text']) >= 2:
                    # Check if the last element matches the specific pattern
                    if entry['text'][-1].startswith("(540):"):
                        # Swap the last and second-to-last elements
                        entry['text'][-1], entry['text'][-2] = entry['text'][-2], entry['text'][-1]

                    
        # Split the text into lines (segments) for each entry in content_data
        for entry in section_data[section_num]["content_data"]:
            text = entry["text"]
            lines = text.split('\n')
            
            # Remove empty strings from the 'lines' list
            lines = [line for line in lines if line.strip() != ""]
            
            # Update the "text" value for the current entry to contain the split lines
            entry["text"] = lines
            
        section_num += 1
        pdf_document.close()

        # Serialize the section data to a JSON format
        output_data = json.dumps(section_data, ensure_ascii=False, indent=4)

        # Write the JSON data to a file
        with open(f"{pdf_file_path}_result_of_segmented_text.json", "w", encoding="utf-8") as json_file:
            json_file.write(output_data)


        data_extracted = "output.json"
        output_json_folder = r'D:\final_corsearch\output_json'          # output json folder path

        if not os.path.exists(output_json_folder):
            os.makedirs(output_json_folder)

        pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
        output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")    
        # print(output_json_path,"42")

        # image_folder = create_image_folder(pdf_file_path)
        # coordinates_file = output_json_path

    
        output_data = json.dumps(section_data, indent=4, ensure_ascii=False)
        with open(data_extracted, "w", encoding="utf-8") as json_file:
            json_file.write(output_data)
            
        # locate_data_in_pdf(pdf_file_path)
        # define_coordinates_from_pdf(pdf_file_path, data_extraction, output_json_path)
        # extract_and_save_image(pdf_file_path, coordinates_file, image_folder, resolution)
        process_bhutan_pdf(pdf_file_path, data_extracted, output_json_path)


def mongolia_pdf_extraction(pdf_file_path):
    
     # Call the first script function
    find_and_fix_data(pdf_file_path)

    # Start of the second script
    pattern = re.compile(r"\(111\)[\s\S]*?(?=\(111\)|$)")  # MONGOLIA

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



        if section_num not in section_data:
            section_data[section_num] = {"page_number": [pn + 1 for pn in page_nums] # Adding 1 to adjust the page number
                                     , "content": [],
                                     "content_data": []
                                    }
    
    # Split the matched text into lines and add them to the section data
        content_lines = [line for line in match.split("\n") if line.strip()]
    # Now process those content lines to join lines that should be together
        content_lines = post_process_content(content_lines)
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
        delimiter = "\n  \n \nМонгол Улсын Оюуны Өмчийн Газар \n \nУЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ"
        texts_to_remove = ["REGISTERED" ,"REGISTERED TRADEMARK","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ" ,"УЛСЫН БҮРТГЭЛД АВСАН" ,"УЛСЫН" ,"УЛСЫН БҮРТГЭЛД", "УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ", "Intellectual Property Office of Mongolia", "Монгол Улсын Оюуны Өмчийн Газар"]
        texts_to_remove_start = ["TRADEMARK","БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ", "АВСАН БАРААНЫ ТЭМДЭГ", "ТЭМДЭГ","УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ","БАРААНЫ ТЭМДЭГ", "REGISTERED TRADEMARK"]
        section_data[section_num]["content_data"] = correct_text_segmentation(section_data[section_num]["content_data"], delimiter, texts_to_remove, texts_to_remove_start)

    # Call the merge_duplicate_pages function to join text on the same page into one
        section_data[section_num]["content_data"] = merge_duplicate_pages(section_data[section_num]["content_data"])

    # Call the post_process_lines function to correct the segmentation
        for entry in section_data[section_num]["content_data"]:
            lines = entry["text"].split('\n')
            lines = post_process_lines(lines)
            entry["text"] = "\n".join(lines)

    # Now call the split_text_by_newline function to split the text by newlines
        section_data[section_num]["content_data"] = split_text_by_newline(section_data[section_num]["content_data"])

        section_num += 1

# Serialize the section data to a JSON format
    output_data = json.dumps(section_data, ensure_ascii=False, indent=4)
    output_json = f"{pdf_file_path}_result_latest_version.json"

# Write the JSON data to a file
    with open(output_json, "w", encoding="utf-8") as json_file:
        json_file.write(output_data)

    data_extracted = output_json
    data_json_folder = r'D:\corsearch_project\data_json_folder'          # output json folder path

    if not os.path.exists(data_json_folder):
        os.makedirs(data_json_folder)

    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_json_path = os.path.join(data_json_folder, f"{pdf_filename}.json")    
    # print(output_json_path,"42")

    # image_folder = create_image_folder(pdf_file_path)
    # coordinates_file = output_json_path


    # define_coordinates_from_pdf(pdf_file_path, data_extraction, output_json_path)
    # extract_and_save_image(pdf_file_path, coordinates_file, image_folder, resolution)
    process_mongolia_pdf(pdf_file_path, data_extracted, output_json_path)

    json_file_path = 'pdf.json'

# Process the bulk trademarks
    processed_trademarks = process_bulk_trademarks(json_file_path, pdf_file_path)

    # Specify the path to the output JSON file
    output_json_folder = r'D:\corsearch_project\output_json_folder'
    if not os.path.exists(data_json_folder):
        os.makedirs(data_json_folder)

    final_output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")    

    # output_json_file_path = 'structure_heading.json'

    # Save the modified JSON data into a single file with UTF-8 encoding
    with open(final_output_json_path, 'w', encoding='utf-8') as output_file:
        json.dump(processed_trademarks, output_file, ensure_ascii=False, indent=4)


def tunisia_pdf_extraction(pdf_file_path):
    def fix_structure_tunisia(data):
        for section, section_data in data.items():
            i = 0
            while i < len(section_data) - 1:  # Adjusted the loop condition
                if section_data[i].startswith('Numéro de dépôt:'):
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

    # exclude_numbers = [str(i) for i in range(1, 1501)]
    exclude_words = []

    doc = fitz.open(pdf_file_path)
    found_data = {}
    in_section = False
    current_section = []
    section_counter = 1

    for page in range(len(doc)):
        text = doc[page].get_text()

        lines = text.split("\n")

        for line_index, line in enumerate(lines):
            # Exclude header lines
            if is_header_line_tunisia(line):
                continue

            # Exclude lines with only one character
            if len(line.strip()) == 1:
                continue

            # Exclude lines with some digits followed by a hyphen
            if any(char.isdigit() for char in line) and line.strip().endswith('-'):
                continue

            # Exclude specific words from the line before processing
            words = line.split()
            filtered_words = [word for word in words if word not in exclude_words]
            updated_line = ' '.join(filtered_words)

            if "Numéro de dépôt :" in line:
                if in_section:
                    #found_data[f"{section_counter}"] = {"content": current_section}
                    found_data[f"tradeMark {section_counter}"] = current_section
                    current_section = []
                    section_counter += 1

                in_section = True

            if in_section and updated_line.strip():  # Check for non-empty lines
                current_section.append(updated_line)

    if in_section:
        found_data[f"tradeMark {section_counter}"] = current_section
        #found_data[f"{section_counter}"] = {"content": current_section}

    doc.close()

    # Fix the data structure
    fix_structure_tunisia(found_data)

    # Generate the JSON file name based on the input PDF file
    pdf_file_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_json = f"{pdf_file_path}_result_latest_version.json"

    # Save the modified data into a JSON file section-wise
    output_data = {}
    for section, section_data in found_data.items():
        output_data[section] = section_data

    with open(json_file_name, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)

    data_extracted = output_json
    data_json_folder = r'D:\corsearch_project\data_json_folder'          # output json folder path

    if not os.path.exists(data_json_folder):
        os.makedirs(data_json_folder)

    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_json_path = os.path.join(data_json_folder, f"{pdf_filename}.json")    
    

    # process_tunisia_pdf(pdf_file_path, data_extracted, output_json_path)

    json_file_path = 'pdf.json'

# Process the bulk trademarks
    processed_trademarks = process_bulk_trademarks(json_file_path, pdf_file_path)

    # Specify the path to the output JSON file
    output_json_folder = r'D:\corsearch_project\output_json_folder'
    if not os.path.exists(data_json_folder):
        os.makedirs(data_json_folder)

    final_output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")    

    # output_json_file_path = 'structure_heading.json'

    # Save the modified JSON data into a single file with UTF-8 encoding
    with open(final_output_json_path, 'w', encoding='utf-8') as output_file:
        json.dump(processed_trademarks, output_file, ensure_ascii=False, indent=4)


def algeria_pdf_extraction(pdf_file):
    def fix_structure_algeria(data):
        for section, section_data in data.items():
            i = 0
        while i < len(section_data):
            if section_data[i].startswith('(') and not section_data[i].startswith('(170)'):
                key = section_data[i]
                if i + 1 < len(section_data):
                    value = section_data[i + 1]
                    # Check if the value already has a colon
                    if not value.startswith(""):
                        section_data[i] = f"{key}\n{value}"
                    else:
                        # If value starts with a digit, move it to the next line
                        if value[0].isdigit():
                            section_data[i] = key
                            section_data.insert(i + 1, value)
                        else:
                            section_data[i] = f"{key} {value}"
                        del section_data[i + 2]
            i += 1

    exclude_words = ["_____________________________________________","____________________________________________",]

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
    fix_structure_algeria(found_data)

    # Save the modified data into a JSON file section-wise
    output_data = {}
    for section, section_data in found_data.items():
        output_data[section] = section_data

    with open('output.json', 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)

