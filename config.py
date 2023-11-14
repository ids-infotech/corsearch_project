import fitz  # PyMuPDF
import re
import json
from datetime import datetime

# Function to extract jurisdiction from the filename
def extract_jurisdiction_from_filename(file_name):
    match = re.search(r'\((.*?)\)', file_name)
    if match:
        return match.group(1)
    else:
        return None

def extract_section_info(text, section_name):
    section_match = re.search(fr'{section_name}\n(.*?)\n', text, re.DOTALL)
    if section_match:
        return section_match.group(1)
    else:
        return None

def convert_to_iso_date(date_string):
    try:
        parsed_date = datetime.strptime(date_string, "%d %b %Y")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return date_string

def generate_structure(attributes):
    structure = {}
    for attr in attributes:
        if '.' not in attr:  # Simple attributes without nesting
            structure[attr] = ""
        elif attr.count('.') == 1:  # Attributes with one dot for one level of nesting
            main_key, sub_key = attr.split('.')
            if main_key not in structure:
                structure[main_key] = {sub_key: ""}
            else:
                structure[main_key][sub_key] = ""
        elif attr.count('.') == 2:  # Attributes with three levels of nesting
            first_key, second_key, third_key = attr.split('.')
            if first_key not in structure:
                structure[first_key] = {third_key: ""}
            else:
                if third_key not in structure[first_key]:
                    structure[first_key][third_key] = ""
                else:
                    structure[first_key][third_key] = ""
    return structure

# Replace 'your_pdf_file.pdf' with the path to your PDF file
pdf_path = 'CD-Saint Vincent & the Grenadines (VC) - Extractor Specs-031123-092425.pdf'

# Extract jurisdiction from the file name
file_name = pdf_path.split('/')[-1]  # Extracting the file name from the path
jurisdiction_code = extract_jurisdiction_from_filename(file_name)

# Extract text from the PDF
with fitz.open(pdf_path) as pdf_document:
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

# Extract 'Dates Covered' section from the extracted text
dates_covered = extract_section_info(text, 'Dates Covered')

# Extract 'Sections To Be Extracted' section from the extracted text
sections_to_extract = extract_section_info(text, 'Section To Be Extracted')

if dates_covered and sections_to_extract and jurisdiction_code:
    formatted_date_range = {
        "start": convert_to_iso_date(dates_covered.split(' - ')[0].strip()),
        "end": convert_to_iso_date(dates_covered.split(' - ')[1].strip())
    }

    # JSON file name in the format {JurisdictionIsoCode}-{YYYYMMDD}-{YYYYMMDD}.json
    file_name_parts = [jurisdiction_code, formatted_date_range['start'].replace('-', ''), formatted_date_range['end'].replace('-', '')]
    json_file_name = '-'.join(file_name_parts) + '.json'

    # Structure the combined output in JSON format
    output_combined = {
        "applicableFor": {
            "jurisdictionCode": jurisdiction_code,
            "range": formatted_date_range,
            "sections": []
        }
    }

    # Dictionary to hold attributes for each section title
    attributes = {
        "Filings": [
            'applicationNumber',
            'applicationDate',
            'owners.owner.name',
            'verbalElements',
            'classifications.niceClass',
            'priorities.priority.number',
            'priorities.priority.date',
            'priorities.priority.country',
        ],
        "Applications": [
            'applicationNumber',
            'applicationDate',
            'owners.owner.name',
            'representatives.representative.name',
            'representatives.representative.address',
            'representatives.representative.country',
            'verbalElements',
            'deviceMarks',
            'classifications.niceClass',
            'classifications.goodServiceDescription',
            'Colors',
            'priorities.priority.number',
            'priorities.priority.date',
            'priorities.priority.country',
            'Disclaimer'
        ],
        "Errata": [
            'applicationNumber',
            'applicationDate',
            'owners.owner.name',
            'verbalElements',
            'deviceMarks',
            'representatives.representative.name',
            'representatives.representative.address',
            'representatives.representative.country',
            'classifications.niceClass',
            'classifications.goodServiceDescription',
            'Comments'
        ]

        
    }

    for section, section_trademarks in attributes.items():
        section_data = {
            "title": section,
            "trademarks": generate_structure(section_trademarks)
        }
        output_combined["applicableFor"]["sections"].append(section_data)

    # Save the combined JSON output to a file with a dynamic file name
    with open(json_file_name, 'w', encoding='utf-8') as file:
        json.dump(output_combined, file, ensure_ascii=False, indent=4)
    print(f"Combined data with a modified date range saved to {json_file_name}")
else:
    print("Either jurisdiction code, dates covered, or sections to extract not found.")

# import os
# import json
# import re
# from collections import defaultdict

# # Read the config file
# with open('config.json', 'r') as config_file:
#     config = json.load(config_file)

# # Check if the 'fields' key is present in the config dictionary
# if 'fields' not in config:
#     print("Error: 'fields' key not found in the config file.")
#     exit()

# # Function to extract data from a PDF using regular expressions
# def extract_data_from_pdf(pdf_data, regex_patterns):
#     extracted_data = {}
#     for key, pattern in regex_patterns.items():
#         regex_pattern = re.compile(pattern)
#         match = regex_pattern.search(pdf_data)
#         if match:
#             extracted_data[key] = match.group(1).strip()
#     return extracted_data

# # Folder containing PDF files
# pdf_folder = 'D:\\Vijay\\Python\\corsearch\\Saint Vincent'

# # Dictionary to store extracted data from all PDFs
# all_extracted_data = defaultdict(list)

# # Loop through PDF files in the folder
# for filename in os.listdir(pdf_folder):
#     if filename.endswith('.pdf'):
#         with open(os.path.join(pdf_folder, filename), 'rb') as pdf_file:
#             pdf_data = pdf_file.read()

#             # Check if 'fields' key is present in the config dictionary
#             if 'fields' not in config:
#                 print(f"Error: 'fields' key not found in the config file for {filename}")
#                 continue

#             extracted_data = extract_data_from_pdf(pdf_data, config["fields"])
#             all_extracted_data[filename].append(extracted_data)

# # Print extracted data from all PDFs
# for filename, data in all_extracted_data.items():
#     print(f"Extracted data from {filename}:")
#     print(json.dumps(data, indent=2))
#     print("\n")