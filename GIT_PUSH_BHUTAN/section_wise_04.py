# import json
# import os

# from final_structure_02 import *
# from coordinates_log_file_03 import *
# from pdf_01 import *


# def remove_tradeMark_numbers(input_json_file, output_json_file):
#     # Load data from the input JSON file
#     with open(input_json_file, 'r', encoding='utf-8') as f_input:
#         input_data = json.load(f_input)

#     # Create a list to store sections with trademark entries
#     sections_list = []

#     # Specify the fields to extract trademark information from
#     fields_to_extract = ["Madrid mark", "National mark"]

#     # Iterate over the specified fields
#     for field_name in fields_to_extract:
#         # Create a section dictionary for the current field
#         section_data = {"title": field_name, "tradeMarks": []}

#         # Iterate over the keys in the current field
#         for trademark_key, trademark_data_list in input_data.get(field_name, {}).items():
#             # Iterate over the list of trademark data under each key
#             for trademark_data in trademark_data_list:
#                 # Check if the current trademark_data is a dictionary
#                 if isinstance(trademark_data, dict):
#                     # Append the current trademark_data to the tradeMarks list in the section
#                     section_data["tradeMarks"].append(trademark_data)

#         # Append the section_data to the sections_list
#         sections_list.append(section_data)

#     # Create a new structure with the "sections" key
#     output_structure = {"sections": sections_list}

#     # Save the updated JSON structure
#     with open(output_json_file, 'w', encoding='utf-8') as f_output:
#         json.dump(output_structure, f_output, ensure_ascii=False, indent=4)

#     print("Trademark numbers removed and grouped by sections successfully.")


# pdf_file_path = r'input_pdf\BT20230215-106.pdf'

# output_json_folder = r'output'          # output json folder path
# if not os.path.exists(output_json_folder):
#     os.makedirs(output_json_folder)
# pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
# output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")

# output_structure_file = r'temp_output\BT20230215-106.json'

# # Example usage:
# pdf_Extraction_Bhutan(pdf_file,output_json_folder)
# process_bulk_trademarks(json_file_path, pdf_file_path)
# update_structure_with_clippings_BHUTAN(output_structure_file, 'output_BT20230215-106.json', output_structure_file, 'BT20230215-106_base64.txt')
# remove_tradeMark_numbers(output_structure_file, output_json_path, pdf_file_path)


import json
import os
from final_structure_02 import *
from coordinates_log_file_03 import *
from pdf_01 import *

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
    output_structure = {"sections": sections_list}

    # Save the updated JSON structure
    with open(output_json_file, 'w', encoding='utf-8') as f_output:
        json.dump(output_structure, f_output, ensure_ascii=False, indent=4)

    print("Trademark numbers removed and grouped by sections successfully.")

pdf_file_path = r'input_pdf\BT20230215-106.pdf'
output_json_folder = r'output'  # output json folder path
if not os.path.exists(output_json_folder):
    os.makedirs(output_json_folder)
pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")

output_structure_file = r'temp_output\BT20230215-106.json'

# Example usage:
pdf_Extraction_Bhutan(pdf_file_path, output_json_folder)
processed_trademarks = process_bulk_trademarks(output_structure_file, pdf_file_path)

if processed_trademarks:
    with open(output_structure_file, 'w', encoding='utf-8') as output_file:
        json.dump(processed_trademarks, output_file, ensure_ascii=False, indent=4)

update_structure_with_clippings_BHUTAN(output_structure_file, 'output_BT20230215-106.json', output_structure_file, 'BT20230215-106_base64.txt')
remove_tradeMark_numbers(output_structure_file, output_json_path)
