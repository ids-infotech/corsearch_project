



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
        keys = attr.split('.')
        current_level = structure
        for key in keys[:-1]:
            if key not in current_level:
                current_level[key] = {}
            current_level = current_level[key]
        current_level[keys[-1]] = ""
    return structure

# Replace 'your_pdf_file.pdf' with the path to your PDF file
pdf_path = 'CD-Aruba (AW) - Extractor Specs-031123-084723.pdf'

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
print(f'Dates Covered: {dates_covered}')

# Extract 'Sections To Be Extracted' section from the extracted text
sections_to_extract = extract_section_info(text, 'Sections To Be Extracted')
print(f'Sections To Be Extracted: {sections_to_extract}')

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
        "Renewal": [
            'applicationNumber',
            'applicationDate',
            'registrationNumber',
            'registrationDate',
            'owners.name',
            'owners.addrress',
            'owners.country',
            "renewalDate",
            "expiryDate",
            'representatives.name',
            'representatives.address',
            'representatives.country',
            'verbalElements',
            'classifications.niceClass',

        ],
       "Registration": [
            'applicationNumber',
            'applicationDate',
            'registrationNumber',
            'registrationDate',
            "expiryDate",
            'owners.name',
            'owners.addrress',
            'owners.country',
            'representatives.name',
            'representatives.address',
            'representatives.country',
            'verbalElements',
            'classifications.niceClass',
            "priority.number",
            "priority.date",
            "priority.country",

        ], 

    }

    for section, section_trademarks in attributes.items():
        section_data = {
            "title": section,
            "trademarks": generate_structure(section_trademarks)
        }
        output_combined["applicableFor"]["sections"].append(section_data)

    # Save the combined JSON output to a file with a dynamic file name
    with open(json_file_name, 'w') as file:
        json.dump(output_combined, file, indent=4)
    print(f"Combined data with a modified date range saved to {json_file_name}")
else:
    print("Either jurisdiction code, dates covered, or sections to extract not found.")
