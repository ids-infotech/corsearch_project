import fitz
import re
import json
from image_processing import *
from code_cleaning import *
from structure_heading import process_bulk_trademarks
import os 

resolution = 200

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




























# import os
# import json
# import fitz  # PyMuPDF
# import re
# from image_processing import *

# def process_page(page):
#     """Extract text and page number from a page."""
#     page_text = page.get_text("text")
#     return page_text, page.number

# def correct_text_segmentation(content_data, delimiter):
#     """Correct text segmentation issues."""
#     corrected_data = []
#     for page_text in content_data:
#         split_texts = page_text['text'].split(delimiter)
#         corrected_data.append({'text_on_page': page_text['text_on_page'], 'text': split_texts[0]})
#         if len(split_texts) > 1:
#             corrected_data.append({'text_on_page': page_text['text_on_page'] + 1, 'text': split_texts[1]})
#     return corrected_data

# def merge_duplicate_pages(content_data):
#     """Merge texts from duplicate pages."""
#     consolidated_data = {}
#     for entry in content_data:
#         page_num = entry["text_on_page"]
#         text = entry["text"].strip()
#         if not text:
#             continue
#         consolidated_data[page_num] = consolidated_data.get(page_num, '') + " " + text
#     merged_data = [{"text_on_page": k, "text": v.strip()} for k, v in consolidated_data.items()]
#     merged_data.sort(key=lambda x: x["text_on_page"])
#     return merged_data

# def extract_data_from_pdf(pdf_file_path):
#     """Main function to extract data from PDF and save it as JSON."""
#     # Regular expression pattern for matching specific text sections
#     pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")

#     # Open the PDF file
#     pdf_document = fitz.open(pdf_file_path)
#     text_pages = {}

#     # Process each page
#     for page in pdf_document:
#         text, pn = process_page(page)
#         text_pages[pn] = text

#     # Concatenate text from all pages
#     extracted_text = " ".join(text_pages.values())
#     matches = pattern.findall(extracted_text)

#     # Extract and structure section data
#     section_data = {}
#     section_num = 1

#     for match in matches:
#         if "(511) \u2013 NICE classification for goods and services" in match:
#             continue

#         section_data[section_num] = {'page_number': [], 'content': [], 'content_data': []}
#         start_index = extracted_text.find(match)
#         page_nums = []
#         current_pos = 0
#         for pn, txt in text_pages.items():
#             current_pos += len(txt)
#             if start_index < current_pos:
#                 page_nums.append(pn)
#                 if current_pos > start_index + len(match):
#                     break

#         section_data[section_num]['page_number'] = [pn + 1 for pn in page_nums]

#         content_lines = [line for line in match.split("\n") if line.strip()]
#         section_data[section_num]["content"].extend(content_lines)

#         segment_start = start_index
#         current_content_data = []

#         for pn in page_nums:
#             segment_end = min(segment_start + len(text_pages[pn]), start_index + len(match))
#             while extracted_text[segment_end] not in [" ", "\n", "\t"] and segment_end > segment_start:
#                 segment_end -= 1

#             segment = extracted_text[segment_start:segment_end]
#             if segment.strip():
#                 current_content_data.append({"text_on_page": pn + 1, "text": segment.strip()})
#             segment_start = segment_end

#         section_data[section_num]["content_data"].extend(current_content_data)

#         delimiter = 'Successfull Examination Marks'
#         section_data[section_num]["content_data"] = correct_text_segmentation(section_data[section_num]["content_data"], delimiter)
#         section_data[section_num]["content_data"] = merge_duplicate_pages(section_data[section_num]["content_data"])

#         for entry in section_data[section_num]["content_data"]:
#             text = entry["text"]
#             lines = [line for line in text.split('\n') if line.strip()]
#             entry["text"] = lines

#         section_num += 1

#     pdf_document.close()

#     output_json_path = f"{pdf_file_path.split('.')[0]}output_today.json"
#     with open(output_json_path, "w", encoding="utf-8") as json_file:
#         json.dump(section_data, json_file, ensure_ascii=False, indent=4)

#     return output_json_path

# # Example usage
# pdf_file_path = "BT20211006-98.pdf"
# result_json = extract_data_from_pdf(pdf_file_path)
# print(f"Data extracted and saved to {result_json}")