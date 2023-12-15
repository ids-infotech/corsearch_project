import json
import re
import os
import logging
import fitz


from pdf_01 import *

logging.basicConfig(filename='trademark_processing.log', level=logging.INFO)




def process_310_320_330(trademark_field, trademark_number=None):
    # Regular expression pattern for the first entry type
    pattern_type1 = re.compile(r'(?:\(310\)\(320\)\(330\):)\s*(\S+)\s+(\d{2}/\d{2}/\d{4})\s+([A-Z]+)')

    # Regular expression pattern for the second entry type
    pattern_type2 = re.compile(r'(?:\(310\)\(320\)\(330\):)\s*([\d\s.\/]+)\s+(\d{2}/\d{2}/\d{4})\s+([A-Z]{2})')

    # Regular expression pattern for the third entry type with multiple sets
    pattern_type3 = re.compile(r'(?:\(310\)\(320\)\(330\):)\s*((?:\d+\s+\d{2}/\d{2}/\d{4}\s+[A-Z]+(?:\s*;)?\s*)+)')

    # Additional pattern to handle the case where data is on the next line
    pattern_next_line = re.compile(r'(\d+)\s+(\d{2}/\d{2}/\d{4})\s+([A-Z]+)')

    # Check if the trademark field matches the first entry type
    match_type1 = pattern_type1.search(trademark_field)
    if match_type1:
        number, date, country = match_type1.groups()
        return [{"number": number, "date": date, "country": country}]

    # Check if the trademark field matches the second entry type
    match_type2 = pattern_type2.search(trademark_field)
    if match_type2:
        number, date, country = match_type2.groups()
        # Remove spaces from the number for the second entry type
        number = ''.join(number.split())
        return [{"number": number, "date": date, "country": country}]

    # Check if the trademark field matches the third entry type
    match_type3 = pattern_type3.search(trademark_field)
    if match_type3:
        # Process each set of data within the third entry type
        sets_data = match_type3.group(1)
        entries = re.findall(pattern_next_line, sets_data)
        return [{"number": number, "date": date, "country": country} for number, date, country in entries]

    # Log a message if no pattern matches and include the trademark number
    logging.warning(f"Pattern didn't match for trademark field {trademark_number}: {trademark_field}")

    # Return default priority when no data is found
    default_priority = {"number": None, "date": None, "country": None}
    logging.warning("No data found for 310, 320, 330 entries.")

    return [default_priority]




def extract_nice_classes_and_goods(values, added_nice_classes):
    output_data = {"classifications": []}
    current_class = None
    current_goods = []

    for line in values:
        match_class = re.match(r'Ангилал (\d+):(.+?)(?=(?:Ангилал \d+:|$))', line)

        if match_class:
            # If there is an existing class, add it to the output data
            if current_class is not None:
                # Check if the class has already been added for this trademark
                if current_class not in added_nice_classes:
                    output_data["classifications"].append({
                        "niceClasses": int(current_class),
                        "goodServiceDescription": ' '.join(current_goods).strip()
                    })
                    added_nice_classes.add(current_class)

            current_class = match_class.group(1)
            current_goods = [match_class.group(2).strip()]
        else:
            current_goods.append(line.strip())

    # Add the last class to the output data
    if current_class is not None and current_class not in added_nice_classes:
        output_data["classifications"].append({
            "niceClasses": int(current_class),
            "goodServiceDescription": ' '.join(current_goods).strip()
        })
        added_nice_classes.add(current_class)

    return output_data


def process_trademark_section(trademark_data):
    added_nice_classes = set()
    filtered_trademark_data = {
        "registrationNumber": None,
        "expiryDate": None,
        "applicationNumber": None,
        "applicationDate": None,
        "publicationNumber": None,
        
        "priorities": [],
        "owners": [],
        "representatives": [],
        "verbalElements": None,
        "disclaimer": None,
        "viennaClasses": ["null"],
        "colors": None,
        "classifications": []  # Initialize classifications list
    }

    in_priorities_section = False
    in_owners_section = False
    in_representatives_section = False
    in_verbal_elements_section = False
    in_disclaimer_section = False
    in_vienna_classes_section = False
    in_colors_section = False
    in_310_section = False

    for entry in trademark_data:
        if entry.startswith('(111)'):
            entry = entry.replace('(111)', 'registrationNumber')
            registration_number = entry.split(':')[1].strip()
            filtered_trademark_data["registrationNumber"] = registration_number

        elif entry.startswith('(450)'):
            entry = entry.replace('(450)', 'publicationNumber')
            publication_number = entry.split(':')[1].strip()
            filtered_trademark_data["publicationNumber"] = publication_number

        elif entry.startswith('(170)'):
            if len(entry.split(':')) > 1:
                entry = entry.replace('(170)', 'expiryDate')
                expiry_date = entry.split(':')[1].strip()
                expiry_date = ':'.join(part.strip() for part in expiry_date.split(':')).strip(':')
                filtered_trademark_data["expiryDate"] = expiry_date
            else:
                next_line_value = ": " + trademark_data[trademark_data.index(entry) + 1].strip()
                next_line_value = ':'.join(part.strip() for part in next_line_value.split(':')).strip(':')
                filtered_trademark_data["expiryDate"] = next_line_value
        elif entry.startswith('(210)'):
            if len(entry.split(':')) > 1:
                entry = entry.replace('(210)', 'applicationNumber')
                application_number = entry.split(':')[1].strip()
                filtered_trademark_data["applicationNumber"] = application_number
        elif entry.startswith('(220)') and len(entry.split(':')) > 1:
            entry = entry.replace('(220)', 'applicationDate')
            application_date = entry.split(':')[1].strip()
            application_date = ':'.join(part.strip() for part in application_date.split(':')).strip(':')
            filtered_trademark_data["applicationDate"] = application_date
        elif entry.startswith('(310, 320, 330) :'):
            priority_data = process_310_320_330(entry)
            if priority_data is not None:
                filtered_trademark_data["priorities"].extend(priority_data)




        elif entry.startswith('(732) :'):
            in_owners_section = True
            filtered_trademark_data["owners"].append({
                "name": None,
                "address": None,
                "country": None
            })
            owner_name = entry.split(':')[1].strip()
            filtered_trademark_data["owners"][-1]["name"] = owner_name
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                filtered_trademark_data["owners"][-1]["address"] = (filtered_trademark_data["owners"][-1]["address"] or "") + " " + next_line_value
                next_line_index += 1
            if not filtered_trademark_data["owners"][-1]["address"]:
                filtered_trademark_data["owners"][-1]["address"] = None
            in_owners_section = False
        elif entry.startswith('(740) :'):
            in_representatives_section = True
            representative_data = {
                "name": None,
                "address": None,
                "country": None
            }
            representative_name = entry.split(':')[1].strip()
            representative_data["name"] = representative_name
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                representative_data["address"] = (representative_data["address"] or "") + " " + next_line_value
                next_line_index += 1
            if not representative_data["address"]:
                representative_data["address"] = None
            filtered_trademark_data["representatives"].append(representative_data)
            in_representatives_section = False
        elif entry.startswith('(541) Нэр :'):
            in_verbal_elements_section = True
            verbal_element_name = entry.split(':')[1].strip()
            ()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('(591)') or next_line_value.startswith('Ангилал'):
                    break
                verbal_element_name += " " + next_line_value
                next_line_index += 1
            filtered_trademark_data["verbalElements"] = verbal_element_name.strip()
            if not filtered_trademark_data["verbalElements"]:
                filtered_trademark_data["verbalElements"] = None
            in_verbal_elements_section = False
        elif entry.startswith('(526) :'):
            in_disclaimer_section = True
            disclaimer_text = entry.split(':')[1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                disclaimer_text += " " + next_line_value
                next_line_index += 1
            filtered_trademark_data["disclaimer"] = disclaimer_text
            if not filtered_trademark_data["disclaimer"]:
                filtered_trademark_data["disclaimer"] = None
            in_disclaimer_section = False
            # ...

        elif entry.startswith('(531) :'):
            in_vienna_classes_section = True
            vienna_classes_data = entry.split(':')[1].strip().split(',')

            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                if ',' in next_line_value:
                    if next_line_value:        
                        vienna_classes_data.extend(next_line_value.split(','))
                else:
                    vienna_classes_data.append(next_line_value)

                next_line_index += 1

    # Filter out empty strings
            vienna_classes_data = [vienna_class.strip() for vienna_class in vienna_classes_data if vienna_class.strip()]

    # Set to null if no data
            if not vienna_classes_data:
                vienna_classes_data = ["null"]

            filtered_trademark_data["viennaClasses"] = vienna_classes_data
            in_vienna_classes_section = False

# ...

        # elif entry.startswith('(531) :'):
        #     in_vienna_classes_section = True
        #     vienna_classes_data = entry.split(':')[1].strip().split(',')
        #     vienna_classes_data = [vienna_class.strip() for vienna_class in vienna_classes_data]
        #     vienna_classes_data = list(filter(None, vienna_classes_data))
        
        #     next_line_index = trademark_data.index(entry) + 1
        #     while next_line_index < len(trademark_data):
        #         next_line_value = trademark_data[next_line_index].strip()
        #         if next_line_value.startswith('('):
        #             break

        # # Check if there's a comma in the line
        #         if ',' in next_line_value:
        #             if next_line_value:
        #                 vienna_classes_data.extend(next_line_value.split(','))
        #         else:
        #             vienna_classes_data.append(next_line_value)

        #         next_line_index += 1

        #     vienna_classes_data = [vienna_class.strip() if vienna_class.strip() else "null" for vienna_class in vienna_classes_data]
        #     filtered_trademark_data["viennaClasses"] = vienna_classes_data
        #     in_vienna_classes_section = False


            # in_vienna_classes_section = True
            # vienna_classes_data = entry.split(':')[1].strip().split(',')
            # vienna_classes_data = [vienna_class.strip() for vienna_class in vienna_classes_data]
            # vienna_classes_data = list(filter(None, vienna_classes_data))
            # if not vienna_classes_data:
            #     vienna_classes_data = ["null"]
            # next_line_index = trademark_data.index(entry) + 1
            # while next_line_index < len(trademark_data):
            #     next_line_value = trademark_data[next_line_index].strip()
            #     if next_line_value.startswith('('):
            #         break
            #     if next_line_value:
            #         vienna_classes_data.extend(next_line_value.split(','))
            #     next_line_index += 1
            # vienna_classes_data = [vienna_class.strip() if vienna_class.strip() else "null" for vienna_class in vienna_classes_data]
            # filtered_trademark_data["viennaClasses"] = vienna_classes_data
            # in_vienna_classes_section = False
        elif entry.startswith('(591) :'):
            in_colors_section = True
            colors_data = entry.split(':')[1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('Ангилал'):
                    break
                colors_data += " " + next_line_value
                next_line_index += 1
            filtered_trademark_data["colors"] = colors_data
            if not filtered_trademark_data["colors"]:
                filtered_trademark_data["colors"] = None
            in_colors_section = False
        elif entry.startswith('Ангилал'):
            nice_classes_and_goods = extract_nice_classes_and_goods(trademark_data[trademark_data.index(entry):], added_nice_classes)
            filtered_trademark_data["classifications"].extend(nice_classes_and_goods["classifications"])

    # Process the "goodServiceDescription" field
    intellectual_index = filtered_trademark_data.get("goodServiceDescription", "").find("Intellectual Property")
    if intellectual_index != -1:
        # If "Intellectual Property" is found, exclude that phrase
        filtered_trademark_data["goodServiceDescription"] = filtered_trademark_data["goodServiceDescription"][:intellectual_index].strip()

    return filtered_trademark_data


def process_bulk_trademarks(json_file, pdf_file_path):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    registration_section = {}
    madrid_section = {}
    

    for section_name, section_data in data.items():
        processed_data = process_trademark_section(section_data)
        key_name = section_name

        if processed_data["registrationNumber"] and processed_data["registrationNumber"].startswith("M-"):
            registration_section[key_name] = [processed_data]
        else:
            madrid_section[key_name] = [processed_data]

    return {
      
        "Registration": registration_section,
        "MADRID REGISTRATION": madrid_section
    }

# Specify the path to the input JSON file
json_file_path = r'temp_output\MN20230531-05.json'
pdf_file_path = r"input_pdf\MN20230531-05.pdf"


find_and_fix_data_MONGOLIA(pdf_file, output_json_folder)

# Process the bulk trademarks
processed_trademarks = process_bulk_trademarks(json_file_path, pdf_file_path)

# Exclude specified words from "goodServiceDescription" field
for section_name, trademarks in processed_trademarks["Registration"].items():
    for trademark in trademarks:
        if "goodServiceDescription" in trademark:
            # Exclude words as needed
            trademark["goodServiceDescription"] = trademark["goodServiceDescription"].replace("Intellectual Property", "").strip()

            # Set representative name to null if not found
            if not trademark["representatives"]:
                trademark["representatives"].append({
                    "name": None,
                    "address": None,
                    "country": None
                })

for section_name, trademarks in processed_trademarks["MADRID REGISTRATION"].items():
    for trademark in trademarks:
        if "goodServiceDescription" in trademark:
            # Exclude words as needed
            trademark["goodServiceDescription"] = trademark["goodServiceDescription"].replace("Intellectual Property", "").strip()

            # Set representative name to null if not found
            if not trademark["representatives"]:
                trademark["representatives"].append({
                    "name": None,
                    "address": None,
                    "country": None
                })

# Specify the path to the output JSON file
output_json_file_path = r'temp_output\MN20230531-05.json'

# Save the modified JSON data into a single file with UTF-8 encoding
with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(processed_trademarks, output_file, ensure_ascii=False, indent=4)
