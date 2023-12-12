# #pass the output json

import json
import re



# Function to process individual trademark sections
def process_trademark_section(trademark_data):
    # Initialize a dictionary to store filtered trademark data
    filtered_trademark_data = {
        "registrationNumber": None,
        "applicationDate": None,
        "registrationDate": None,
        "applicationNumber": None,
        "representatives": [{
            "name": None,
        }],
        "priorities": [],
        "owners": [],
        "classifications": {
            "niceClass": None,
            "goodService Description": None
        },
        "verbalElements": None,
    }

    # Loop through each entry in the trademark data
    for entry in trademark_data:
        # Extract and process information based on entry prefixes
        if entry.startswith('(111)'):
            entry = entry.replace('(111)', '')
            registration_number = entry.split('(111) ')[0].strip()
            filtered_trademark_data["registrationNumber"] = registration_number
        elif entry.startswith('(210)'):
            entry = entry.replace('(210)', '')
            application_number = entry.split('(210) ')[0].strip()
            filtered_trademark_data["applicationNumber"] = application_number
        elif entry.startswith('(151)'):
            entry = entry.replace('(151)', '')
            application_date = entry.split('(151) ')[0].strip()
            filtered_trademark_data["applicationDate"] = application_date
        elif entry.startswith('(732) '):
            in_owners_section = True
            filtered_trademark_data["owners"].append({
                "name": None,
                "address": None,
                "country": None
            })
            owner_name = entry.split('(732)')[1].strip()
            filtered_trademark_data["owners"][-1]["name"] = owner_name
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                filtered_trademark_data["owners"][-1]["address"] = (
                        filtered_trademark_data["owners"][-1]["address"] or "") + " " + next_line_value
                next_line_index += 1
            if not filtered_trademark_data["owners"][-1]["address"]:
                filtered_trademark_data["owners"][-1]["address"] = None
            in_owners_section = False
        elif entry.startswith('(511) '):
            in_classifications_section = True
            filtered_trademark_data["classifications"]["niceClass"] = entry.split('(511)')[1].strip()
            next_line_index = trademark_data.index(entry) + 1

            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                # Append the line to goodService Description
                filtered_trademark_data["classifications"]["goodService Description"] = (
                        filtered_trademark_data["classifications"]["goodService Description"] or "") + " " + next_line_value
                next_line_index += 1
               
            if not filtered_trademark_data["classifications"]["goodService Description"]:
                filtered_trademark_data["classifications"]["goodService Description"] = None

  


            in_classifications_section = False
        elif entry.startswith('(300) '):
            in_priorities_section = True
            filtered_trademark_data["priorities"].append({
                "number": None,
                "date": None,
                "country": None
            })
            priorities_info = entry.split('(300)')[1].strip().split(',')

            # Extract the country (if available)
            if len(priorities_info) > 1:
                filtered_trademark_data["priorities"][-1]["country"] = priorities_info[0].strip()

            # Extract the remaining information for date and number
            remaining_info = ', '.join(priorities_info[1:]).strip()
            date_and_number = remaining_info.split(',')

            # Extract the date
            filtered_trademark_data["priorities"][-1]["date"] = date_and_number[0].strip()

            # Extract the number (if available)
            if len(date_and_number) > 1:
                filtered_trademark_data["priorities"][-1]["number"] = date_and_number[1].strip()

            in_priorities_section = False
        elif entry.startswith('(740) '):
            in_representatives_section = True
            filtered_trademark_data["representatives"].append
            representative_name = entry.split('(740)')[1].strip()
            filtered_trademark_data["representatives"][-1]["name"] = representative_name
            in_representatives_section = False
        elif entry.startswith('() Нэр :'):
            in_verbal_elements_section = True
            verbal_element_name = entry.split(':')[1].strip()
            filtered_trademark_data["verbalElements"] = verbal_element_name
            if not filtered_trademark_data["verbalElements"]:
                filtered_trademark_data["verbalElements"] = None
            in_verbal_elements_section = False

    # Check if priorities information is available
    if not filtered_trademark_data["priorities"]:
        # If priorities information is missing, add a default entry
        filtered_trademark_data["priorities"].append({
            "number":None,
            "date":None,
            "country":None,
        })

    return filtered_trademark_data

def process_bulk_trademarks(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    processed_sections = {}
    for section_name, section_data in data.items():
        processed_data = process_trademark_section(section_data)
        processed_sections[section_name] = [processed_data]

    return processed_sections

# Specify the path to the input JSON file
json_file_path = 'output.json'

# Process the bulk trademarks
processed_trademarks = process_bulk_trademarks(json_file_path)

# Specify the path to the output JSON file
output_json_file_path = 'final.json'

# Modify your processed_trademarks data structure if needed
start_page_number = 7
processed_trademarks["start_page"] = start_page_number

# Save the modified JSON data into a file with UTF-8 encoding
with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(processed_trademarks, output_file, ensure_ascii=False, indent=4)






# #pass the output json

# import json
# import re
# # Function to process individual trademark sections
# def process_trademark_section(trademark_data):
#     # Initialize a dictionary to store filtered trademark data
#     filtered_trademark_data = {
#         "registrationNumber": None,
#         "applicationDate": None,
#         "registrationDate": None,
#         "applicationNumber": None,
#         "representatives": [{
#             "name": None,
#         }],
#         "priorities": [],
#         "owners": [],
#         "classifications": {
#             "niceClass": None,
#             "goodService Description": None
#         },
#         "verbalElements": None,
#     }

#     # Loop through each entry in the trademark data
#     for entry in trademark_data:
#         # Extract and process information based on entry prefixes
#         if entry.startswith('(111)'):
#             entry = entry.replace('(111)', '')
#             registration_number = entry.split('(111) ')[0].strip()
#             filtered_trademark_data["registrationNumber"] = registration_number
#         elif entry.startswith('(210)'):
#             entry = entry.replace('(210)', '')
#             application_number = entry.split('(210) ')[0].strip()
#             filtered_trademark_data["applicationNumber"] = application_number
#         elif entry.startswith('(151)'):
#             entry = entry.replace('(151)', '')
#             application_date = entry.split('(151) ')[0].strip()
#             filtered_trademark_data["applicationDate"] = application_date
#         elif entry.startswith('(732) '):
#             in_owners_section = True
#             filtered_trademark_data["owners"].append({
#                 "name": None,
#                 "address": None,
#                 "country": None
#             })
#             owner_name = entry.split('(732)')[1].strip()
#             filtered_trademark_data["owners"][-1]["name"] = owner_name
#             next_line_index = trademark_data.index(entry) + 1
#             while next_line_index < len(trademark_data):
#                 next_line_value = trademark_data[next_line_index].strip()
#                 if next_line_value.startswith('('):
#                     break
#                 filtered_trademark_data["owners"][-1]["address"] = (
#                         filtered_trademark_data["owners"][-1]["address"] or "") + " " + next_line_value
#                 next_line_index += 1
#             if not filtered_trademark_data["owners"][-1]["address"]:
#                 filtered_trademark_data["owners"][-1]["address"] = None
#             in_owners_section = False
#         elif entry.startswith('(511) '):
#             in_classifications_section = True
#             filtered_trademark_data["classifications"]["niceClass"] = entry.split('(511)')[1].strip()
#             next_line_index = trademark_data.index(entry) + 1

#             while next_line_index < len(trademark_data):
#                 next_line_value = trademark_data[next_line_index].strip()
#                 if next_line_value.startswith('('):
#                     break
#                 # Append the line to goodService Description
#                 filtered_trademark_data["classifications"]["goodService Description"] = (
#                         filtered_trademark_data["classifications"]["goodService Description"] or "") + " " + next_line_value
#                 next_line_index += 1
               
#             if not filtered_trademark_data["classifications"]["goodService Description"]:
#                 filtered_trademark_data["classifications"]["goodService Description"] = None

  


#             in_classifications_section = False
#         elif entry.startswith('(300) '):
#             in_priorities_section = True
#             filtered_trademark_data["priorities"].append({
#                 "number": None,
#                 "date": None,
#                 "country": None
#             })
#             priorities_info = entry.split('(300)')[1].strip().split(',')

#             # Extract the country (if available)
#             if len(priorities_info) > 1:
#                 filtered_trademark_data["priorities"][-1]["country"] = priorities_info[0].strip()

#             # Extract the remaining information for date and number
#             remaining_info = ', '.join(priorities_info[1:]).strip()
#             date_and_number = remaining_info.split(',')

#             # Extract the date
#             filtered_trademark_data["priorities"][-1]["date"] = date_and_number[0].strip()

#             # Extract the number (if available)
#             if len(date_and_number) > 1:
#                 filtered_trademark_data["priorities"][-1]["number"] = date_and_number[1].strip()

#             in_priorities_section = False
#         elif entry.startswith('(740) '):
#             in_representatives_section = True
#             filtered_trademark_data["representatives"].append
#             representative_name = entry.split('(740)')[1].strip()
#             filtered_trademark_data["representatives"][-1]["name"] = representative_name
#             in_representatives_section = False
#         elif entry.startswith('() Нэр :'):
#             in_verbal_elements_section = True
#             verbal_element_name = entry.split(':')[1].strip()
#             filtered_trademark_data["verbalElements"] = verbal_element_name
#             if not filtered_trademark_data["verbalElements"]:
#                 filtered_trademark_data["verbalElements"] = None
#             in_verbal_elements_section = False

#     # Check if priorities information is available
#     if not filtered_trademark_data["priorities"]:
#         # If priorities information is missing, add a default entry
#         filtered_trademark_data["priorities"].append({
#             "number":None,
#             "date":None,
#             "country":None,
#         })

#     return filtered_trademark_data

# def process_bulk_trademarks(json_file):
#     with open(json_file, 'r', encoding='utf-8') as file:
#         data = json.load(file)

#     processed_sections = {}
#     for section_name, section_data in data.items():
#         processed_data = process_trademark_section(section_data)
#         processed_sections[section_name] = [processed_data]

#     return processed_sections

# # Specify the path to the input JSON file
# json_file_path = 'output.json'

# # Process the bulk trademarks
# processed_trademarks = process_bulk_trademarks(json_file_path)

# # Specify the path to the output JSON file
# output_json_file_path = 'final.json'

# # Modify your processed_trademarks data structure if needed
# start_page_number = 7
# processed_trademarks["start_page"] = start_page_number

# # Save the modified JSON data into a file with UTF-8 encoding
# with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
#     json.dump(processed_trademarks, output_file, ensure_ascii=False, indent=4)


# # Remove specific lines from the file
# with open(output_json_file_path, 'r', encoding='utf-8') as file:
#     lines = file.readlines()

# # Filter lines to remove unwanted ones
# filtered_lines = [line for line in lines if not (
#     line.startswith("Bulletin Officiel") or "2023" in line or line.strip() == "_" * len(line.strip())
# )]

# # Write the filtered lines back to the file
# with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
#     output_file.writelines(filtered_lines)