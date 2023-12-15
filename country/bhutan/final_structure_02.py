import json
import re
import pycountry
import logging

from pdf_01 import *


logging.basicConfig(filename='trademark_processing.log', level=logging.INFO)

def process_310_320_330(trademark_field, trademark_number=None):
    # Regular expression pattern for the first entry type
    pattern_type1 = re.compile(r'(?:\(310\)\(320\)\(330\):)\s*(\S+)\s+(\d{2}/\d{2}/\d{4})\s+([A-Z]+)')

    # Regular expression pattern for the second entry type
    pattern_type2 = re.compile(r'(?:\(310\)\(320\)\(330\):)\s*([\d\s.\/]+)\s+(\d{2}/\d{2}/\d{4})\s+([A-Z]{2})')

    # Regular expression pattern for the third entry type with multiple sets
    pattern_type3 = re.compile(r'(?:\(310\)\(320\)\(330\):)\s*((?:\d+\s+\d{2}/\d{2}/\d{4}\s+[A-Z]+;\s*)+)')

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
        entries = re.findall(r'(\d+)\s+(\d{2}/\d{2}/\d{4})\s+([A-Z]+);', sets_data)
        return [{"number": number, "date": date, "country": country} for number, date, country in entries]

    # Log a message if no pattern matches and include the trademark number
    logging.warning(f"Pattern didn't match for trademark field {trademark_number}: {trademark_field}")

    # Return default priority when no data is found
    default_priority = {"number": None, "date": None, "country": None}
    logging.warning("No data found for 310, 320, 330 entries.")

    return [default_priority]



def get_country_names(value):
    for country in pycountry.countries:
        # Use a regular expression to match the full word of the country in the address
        if re.search(r'\b{}\b'.format(re.escape(country.name.lower())), value.lower()):
            # Check if the country is "United States" and replace it with "United States of America"
            return "United States of America" if country.name == "United States" else country.name
    return None

def process_trademark_section_BHUTAN(trademark_data):
    classifications = []
    classification_lines = []
    filtered_trademark_data = {
        "applicationNumber": None,
        "applicationDate": None,
        "owners": [
            {
                "name": "Null",
                "address": "Null",
                "country": None
            }
        ],
        "representatives": [
            {
                "name": None,
                "address": None,
                "country": None
            }
        ],
        "disclaimer": None,
        "colors": None,
        "verbalElements": None,
        "priorities": [],
        "classifications": classifications
    }

    owner_name = ""
    owner_address = ""
    owner_country = ""

    in_representative_section = False
    rep_address = ""
    rep_country = ""

    current_nice_classes = None
    current_goods = ''
    found_511 = False
    verbal_elements = None
    color_value = None
    disclaimer_value = None

    for entry in trademark_data:
        if entry.startswith('(210)'):
            entry = entry.replace('(210)', 'applicationNumber')
            application_number = entry.split(':')[1].strip()
            filtered_trademark_data["applicationNumber"] = application_number

        elif entry.startswith('(220)'):
            entry = entry.replace('(220)', 'applicationDate')
            application_date = entry.split(':')[1].strip()
            filtered_trademark_data["applicationDate"] = application_date

        elif entry.startswith('(731) Applicant Name'):
            in_owners_section = True
            owner_name += entry.split(':')[-1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index]
                if next_line_value.startswith('('):
                    break
                owner_name += ' '+next_line_value
                next_line_index += 1

        elif entry.startswith('(731) Applicant Address'):
            in_owners_section = True
            owner_address += entry.split(':')[-1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index]
                if next_line_value.startswith('('):
                    break
                owner_address += ' ' + next_line_value
                country_name = get_country_names(next_line_value)
                if country_name:
                    owner_country = country_name
                next_line_index += 1

        elif entry.startswith('(750) Representative:'):
            in_representative_section = True
            rep_address += entry.split(':')[-1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index]
                if next_line_value.startswith('('):
                    break
                rep_address += ' ' + next_line_value
                country_name = get_country_names(next_line_value)
                if country_name:
                    rep_country = country_name
                next_line_index += 1
            in_representative_section = False

        elif entry.startswith('(526)'):
            in_disclaimer_section = True
            disclaimer_value = entry.split(':')[1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index]
                if next_line_value.startswith('('):
                    break
                next_line_index += 1
            in_disclaimer_section = False

        elif entry.startswith('(571) Claims'):
            in_color_section = True
            color_value = entry.split(':')[1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index]
                if next_line_value.startswith('(310)(320)(330):'):
                    in_color_section = False
                    break
                color_value += ' ' + next_line_value.strip()
                next_line_index += 1
        

        # elif entry.startswith('(571) Claims'):
        #     in_color_section = True
        #     color_value = entry.split(':')[1].strip()
        #     next_line_index = trademark_data.index(entry) + 1
        #     while next_line_index < len(trademark_data):
        #         next_line_value = trademark_data[next_line_index]
        #         if next_line_value.startswith('(310)(320)(330):'):
        #             break
        #         next_line_index += 1
        #     in_color_section = False

        elif entry.startswith('(540)'):
            verbal_elements = entry.split(':')[1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index]
                next_line_index += 1
                if next_line_value.startswith('('):
                    break
                verbal_elements += ' ' + next_line_value

        elif entry.startswith('(310)(320)(330):'):
            priority_data = process_310_320_330(entry)
            if priority_data is not None:
                filtered_trademark_data["priorities"].extend(priority_data)

            

        elif entry.startswith('(511) :') or entry.startswith('(511) Goods/Services:'):
            classification_lines = []
            found_511 = True
            content = entry.split(":")[1].strip()
            match = re.match(r'^(\d+)', content)
            if match:
                niceClass = match.group()
                goods = content[len(niceClass):].strip()
                classification_lines.append({"niceClass": niceClass, "goodServiceDescription": goods})
            else:
                classification_lines.append({"niceClass": "", "goodServiceDescription": content})
        elif found_511 and entry.strip() != ']':
            match = re.match(r'^(\d*)\s+(.*)$', entry.strip())
            if match:
                niceClass, goods = match.groups()
                classification_lines.append({"niceClass": niceClass, "goodServiceDescription": goods})
            else:
                if classification_lines:
                    classification_lines[-1]["goodServiceDescription"] += ' ' + entry.strip()
                else:
                    classification_lines.append({"niceClass": "", "goodServiceDescription": entry.strip()})

    filtered_trademark_data["classifications"] = classification_lines
    filtered_trademark_data["verbalElements"] = verbal_elements if verbal_elements else None
    filtered_trademark_data["colors"] = color_value if color_value else None
    filtered_trademark_data["disclaimer"] = disclaimer_value if disclaimer_value else None

    # Assign the extracted owner name and address to the filtered data
    filtered_trademark_data["owners"] = [
        {
            "name": owner_name,
            "address": owner_address,
            "country": owner_country if owner_country else None # Placeholder for country, update as needed
        }
    ]

    filtered_trademark_data["representatives"] = [
    {
        "name": rep_address if rep_address else None,
        "address": None,
        "country": rep_country if rep_country else None  # Placeholder for country, update as needed
    }
]


    return filtered_trademark_data


def process_bulk_trademarks(json_file, pdf_file_path):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    madrid_section = {}
    national_section = {}

    for section_name, section_data in data.items():
        processed_data = process_trademark_section_BHUTAN(section_data)

        # Skip iteration if processed_data is None
        if processed_data is None:
            continue

        key_name = section_name

        if processed_data["applicationNumber"].startswith("BT/M/") or processed_data["applicationNumber"].startswith("A/M/") or processed_data["applicationNumber"].startswith("B/M/"):
            madrid_section[key_name] = [processed_data]
        else:
            national_section[key_name] = [processed_data]

    output_data = {
        "Madrid mark": madrid_section,
        "National mark": national_section
    }
    output_json_file_path = r'temp_output\BT20230215-106.json'


    with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)



json_file_path = r'temp_output\BT20230215-106.json'
pdf_file_path = r'input_pdf\BT20230215-106.pdf'

# pdf_Extraction_Bhutan(pdf_file,output_json_folder)


# processed_trademarks = process_bulk_trademarks(json_file_path, pdf_file_path)


# output_json_file_path = r'temp_output\BT20230215-106.json'


# with open(output_json_file_path, 'w', encoding='utf-8') as output_file:
#     json.dump(processed_trademarks, output_file, ensure_ascii=False, indent=4)
