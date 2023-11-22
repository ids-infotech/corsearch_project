import json
import os
import re
import logging
import fitz

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

def process_trademark_section(trademark_data):
    filtered_trademark_data = {
        "registrationNumber": None,
        "expiryDate": None,
        "applicationNumber": None,
        "applicationDate": None,
        "publicationNumber": None,
        "publicationDate": None,  # Added this line
        "priorities": [],
        "owners": [],
        "representatives": [],
        "verbalElements": None,
        "deviceElements": [],
        "disclaimer": None,
        "viennaClasses": [
            "null"
        ],
        "colors": None,
        
        
    }

   

    for entry in trademark_data:
        if entry.startswith('(111)'):
            entry = entry.replace('(111)', 'registrationNumber')
            registration_number = entry.split(':')[1].strip()
            filtered_trademark_data["registrationNumber"] = registration_number
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
            in_priorities_section = True
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                priority_data = next_line_value.split(' ')
                if len(priority_data) >= 4:
                    priority_entry = {
                        "number": priority_data[0],
                        "date": f"{priority_data[1]} {priority_data[2]} {priority_data[3]}",
                        "country": ' '.join(priority_data[4:])
                    }
                    filtered_trademark_data["priorities"].append(priority_entry)
                next_line_index += 1
            if not filtered_trademark_data["priorities"]:
                filtered_trademark_data["priorities"].append({
                    "number": None,
                    "date": None,
                    "country": None
                })
            in_priorities_section = False
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
            filtered_trademark_data["representatives"].append({
                "name": None,
                "address": None,
                "country": None
            })
            representative_name = entry.split(':')[1].strip()
            filtered_trademark_data["representatives"][-1]["name"] = representative_name
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                filtered_trademark_data["representatives"][-1]["address"] = (filtered_trademark_data["representatives"][-1]["address"] or "") + " " + next_line_value
                next_line_index += 1
            if not filtered_trademark_data["representatives"][-1]["address"]:
                filtered_trademark_data["representatives"][-1]["address"] = None
            in_representatives_section = False
        elif entry.startswith('(541) Нэр :'):
            in_verbal_elements_section = True
            verbal_element_name = entry.split(':')[1].strip()
            filtered_trademark_data["verbalElements"] = verbal_element_name
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
        elif entry.startswith('(531) :'):
            in_vienna_classes_section = True
            vienna_classes_data = entry.split(':')[1].strip().split(',')
            vienna_classes_data = [vienna_class.strip() for vienna_class in vienna_classes_data]
            vienna_classes_data = list(filter(None, vienna_classes_data))
            if not vienna_classes_data:
                vienna_classes_data = ["null"]
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                if next_line_value:
                    vienna_classes_data.extend(next_line_value.split(','))
                next_line_index += 1
            vienna_classes_data = [vienna_class.strip() if vienna_class.strip() else "null" for vienna_class in vienna_classes_data]
            filtered_trademark_data["viennaClasses"] = vienna_classes_data
            in_vienna_classes_section = False
        
        elif entry.startswith('(591) :'):
            in_colors_section = True
            colors_data = entry.split(':')[1].strip()
            next_line_index = trademark_data.index(entry) + 1
            while next_line_index < len(trademark_data):
                next_line_value = trademark_data[next_line_index].strip()
                if next_line_value.startswith('('):
                    break
                colors_data += " " + next_line_value
                next_line_index += 1
            filtered_trademark_data["colors"] = colors_data
            if not filtered_trademark_data["colors"]:
                filtered_trademark_data["colors"] = None
            in_colors_section = False
        elif entry.startswith('(450) :'):
            in_publication_number_section = True
            publication_number_entry = entry.split(':')[1].strip().split()
            if len(publication_number_entry) == 1:
                filtered_trademark_data["publicationNumber"] = publication_number_entry[0]
            elif len(publication_number_entry) == 2:
                filtered_trademark_data["publicationNumber"] = publication_number_entry[0]
                filtered_trademark_data["publicationDate"] = publication_number_entry[1]
            in_publication_number_section = False
    # filtered_trademark_data["deviceElements"] =
    return filtered_trademark_data

def process_bulk_trademarks(json_file, pdf_file_path):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    registration_section = {}
    madrid_section = {}
    extracted_info = extract_info_from_filename(pdf_file_path)

    for section_name, section_data in data.items():
        processed_data = process_trademark_section(section_data)
        key_name = section_name  # Keep the "tradeMark" prefix in the keys

        # Check if the registrationNumber starts with 'M'
        if processed_data["registrationNumber"].startswith("M"):
            registration_section[key_name] = [processed_data]
        else:
            madrid_section[key_name] = [processed_data]

    return {
        "extracted_info": extracted_info,  # Add extracted_info at the top level
        "Registration": registration_section,
        "MADRID REGISTRATION": madrid_section
    }

# Specify the path to the input JSON file

