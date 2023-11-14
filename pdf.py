import os
import json
import re
from collections import defaultdict

config_path = 'config.json'  # Replace with the actual path
with open(config_path, 'r') as config_file:
    config = json.load(config_file)
# Print the content of the config dictionary
# print("Config Content:")
# print(json.dumps(config, indent=2))
# Function to extract data from a PDF using regular expressions
def extract_data_from_pdf(pdf_data, sections):
    all_extracted_data = defaultdict(list)
    pdf_text = pdf_data.decode('utf-8', errors='replace')
    for section in sections:
        section_title = section["title"]
        section_data = section["trademarks"]
        extracted_data = {}
        for key, pattern in section_data.items():
            # Convert the dictionary values to a string
            pattern_str = str(pattern)
            regex_pattern = re.compile(pattern_str)
            match = regex_pattern.search(pdf_text)
            if match:
                extracted_data[key] = match.group(1).strip()
        all_extracted_data[section_title].append(extracted_data)
    return all_extracted_data


# Read the config file
'''with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Function to extract data from a PDF using regular expressions
def extract_data_from_pdf(pdf_data, regex_patterns):
    extracted_data = {}
    for key, pattern in regex_patterns.items():
        regex_pattern = re.compile(pattern)
        match = regex_pattern.search(pdf_data)
        if match:
            extracted_data[key] = match.group(1).strip()
    return extracted_data'''

# Folder containing PDF files
pdf_folder = 'D:\\Vijay\\Python\\corsearch\\Saint Vincent'

# Dictionary to store extracted data from all PDFs
all_extracted_data = defaultdict(list)

# Loop through PDF files in the folder
for filename in os.listdir(pdf_folder):
    if filename.endswith('.pdf'):
        with open(os.path.join(pdf_folder, filename), 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            # extracted_data = extract_data_from_pdf(pdf_data, config["fields"])
            extracted_data = extract_data_from_pdf(pdf_data, config["applicableFor"]["sections"])

            all_extracted_data[filename].append(extracted_data)

# Print extracted data from all PDFs
for filename, data in all_extracted_data.items():
    print(f"Extracted data from {filename}:")
    print(json.dumps(data, indent=2))
    print("\n")