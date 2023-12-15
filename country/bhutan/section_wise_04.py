import json
import os
from clear_temp import delete_temp_files
from final_structure_02 import *
from coordinates_log_file_03 import *
from pdf_01 import *



def get_page_count(pdf_file_path):
    try:
        pdf_document = fitz.open(pdf_file_path)
        number_of_pages = pdf_document.page_count
        pdf_document.close()
        return number_of_pages
    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_info_from_filename(pdf_file_path):
    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]

    pattern = re.compile(r'(?P<jurisdictionCode>[A-Z]{2})(?P<publicationDate>\d{8})-(?P<title>.*?)$')

    match = pattern.match(pdf_filename)

    if match:
        # Extract information from the match groups
        jurisdiction_code = match.group('jurisdictionCode')
        publication_date = match.group('publicationDate')
        title = pdf_filename

        # Create a dictionary with the extracted information
        extracted_info = {
            "jurisdictionCode": jurisdiction_code,
            "title": title,
            "numberOfPages": get_page_count(pdf_file_path),  # You can set this value based on your actual implementation
            "publicationDate": f"{publication_date[0:4]}-{publication_date[4:6]}-{publication_date[6:8]}"
        }

        return extracted_info
    else:
        error_message = "Invalid pdf filename"
        logging.error(f"Skipping {pdf_filename} due to {error_message}")

        return None
    
def remove_tradeMark_numbers(input_json_file, output_json_file):
    # Load data from the input JSON file
    with open(input_json_file, 'r', encoding='utf-8') as f_input:
        input_data = json.load(f_input)

    # Create a list to store sections with trademark entries
    sections_list = []

    # Specify the fields to extract trademark information from
    fields_to_extract = ["Madrid mark", "National mark"]

    # Iterate over the specified fields
    for field_name in fields_to_extract:
        # Create a section dictionary for the current field
        section_data = {"title": field_name, "tradeMarks": []}

        # Iterate over the keys in the current field
        for trademark_key, trademark_data_list in input_data.get(field_name, {}).items():
            # Iterate over the list of trademark data under each key
            for trademark_data in trademark_data_list:
                # Check if the current trademark_data is a dictionary
                if isinstance(trademark_data, dict):
                    # Append the current trademark_data to the tradeMarks list in the section
                    section_data["tradeMarks"].append(trademark_data)

        # Append the section_data to the sections_list
        sections_list.append(section_data)

    # Create a new structure with the "sections" key
    extracted_info = extract_info_from_filename(pdf_file_path)
    output_structure = {
         "jurisdictionCode": extracted_info["jurisdictionCode"],
        "title": extracted_info["title"],
        "numberOfPages": extracted_info["numberOfPages"],
        "publicationDate": extracted_info["publicationDate"],       
        "sections": sections_list}

    # Save the updated JSON structure
    with open(output_json_file, 'w', encoding='utf-8') as f_output:
        json.dump(output_structure, f_output, ensure_ascii=False, indent=4)

    print("Trademark numbers removed and grouped by sections successfully.")

# pdf_file_path = r'input_pdf\BT20230215-106.pdf'


def generate_json_bhutan(pdf_file_path):
# Example usage:
    output_json_folder = r'output'  # output json folder path
    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)
    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")
    temp_folder =r'temp_output'
    output_structure_file = os.path.join(temp_folder, f"{pdf_filename}.json")
    temp_folder_path = r'temp_output'


    
    pdf_Extraction_Bhutan(pdf_file_path, output_json_folder)
    process_bulk_trademarks(output_structure_file, pdf_file_path)
    update_structure_with_clippings_BHUTAN(output_structure_file, 'output_BT20230215-106.json', output_structure_file, 'BT20230215-106_base64.txt')
    remove_tradeMark_numbers(output_structure_file, output_json_path)
    delete_temp_files(temp_folder_path, delete_all=True)