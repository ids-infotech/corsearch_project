import json
import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


def extract_trademarks_info(text):
    trademarks_info = []

    # Updated regular expressions
    matches = re.finditer(
        r"(\b\d{5,}\b\s+Class[\s\S]*?)(?=\b\d{5,}\b\s+Class|$)",
        text
        # print(text)
    )

    for match in matches:
        trademarks_text = match.group(1)
        
        '''DATE RECEIVED'''
        # Extract 'Date Received' using regex
        date_received_match = re.search(r"Date Received (\w+ \d+, \d{4})", trademarks_text)
        application_date = date_received_match.group(1) if date_received_match else ""
        
        '''OWNER NAME'''
        # Extract name using regex  
        # pattern_for_owner_name = re.compile(r'\b([A-Z\s]+)\b(?=\d{5}|\bDate Received\b)')
        # name_match = re.search(pattern_for_owner_name, trademarks_text)
        # Extract owner names from the beginning of each line in uppercase
        pattern_for_owner_name = re.compile(r'^([A-Z\s]+)\b', re.MULTILINE)
        name_match = re.search(pattern_for_owner_name, trademarks_text)
        owner_name = name_match.group(1).strip() if name_match else ""

        '''OWNER ADDRESS'''
        # Extract address using regex
        pattern_for_owner_address =  re.compile(r'(?<=whose trade or business address is at)(.*?),\s*([\w\s]+)\.', re.DOTALL)
        address_match = re.search(pattern_for_owner_address, trademarks_text)
        owner_address = address_match.group(1).strip().replace('\n', '') if address_match else ""
        owner_country = address_match.group(2).strip() if address_match else ""
        # Concatenate country to address
        if owner_address and owner_country:
            owner_address += f", {owner_country}"

        '''NICE CLASS'''
        # Extract class number using regex
        pattern_for_class_number = re.compile(r'Class (\d+)')
        class_number_match = re.search(pattern_for_class_number, trademarks_text)
        class_number = class_number_match.group(1).strip() if class_number_match else ""
        
        '''goodServiceDescription'''
        # Extract text after "Class Number" until UPPERCASE words are found
        pattern_for_class_text = re.compile(r'Class \d+\s*(.*?)\b[A-Z]+\b', re.DOTALL)
        class_text_match = re.search(pattern_for_class_text, trademarks_text)
        class_text = class_text_match.group(1).strip().replace('\n', ',')  if class_text_match else ""

        '''REPRESENTATIVE NAME'''
        # Extract text after "Address for" up to the end of the line
        pattern_for_representative_name = re.compile(r'Address for (.+)$', re.MULTILINE)
        rep_name_match = re.search(pattern_for_representative_name, trademarks_text)
        rep_name = rep_name_match.group(1).strip() if rep_name_match else ""

        '''REPRESENTATIVE ADDRESS'''
        # Extract text in front of "Service"
        pattern_for_rep_address = re.compile(r'Service (.+)$', re.MULTILINE)
        rep_address_match = re.search(pattern_for_rep_address, trademarks_text)
        rep_address = rep_address_match.group(1).strip() if rep_address_match else ""

        trademarks = {
            "applicationNumber": re.search(r"(\d+)\s+Class", trademarks_text).group(1),
            "applicationDate": application_date,
            "owners": {
                "name": owner_name,
                "address": owner_address,
                "country": owner_country
            },
            "verbalElements": "",
            "deviceElements": "",
            "classifications": {
                "niceClass": class_number,
                "goodServiceDescription": class_text
            },
            "disclaimer": "",
            "representatives": {
                "name": rep_name,
                "address": rep_address,
                "country": ""
            },
            "viennaClasses": "",
            "color": "",
            "priorities": {
                "number": "",
                "date": "",
                "country": ""
            }
        }
        trademarks_info.append(trademarks)

    return trademarks_info

def extract_trademarks_info_corrections(text):
    trademarks_info_corrections = []

    # Updated regular expressions
    matches = re.finditer(
        r"(\b\d{5,}\b\s+Class[\s\S]*?)(?=\b\d{5,}\b\s+Class|$)",
        text
        # print(text)
    )

    for match in matches:
        trademarks_text = match.group(1)

        '''OWNER NAME'''
        # Extract name using regex  
        # pattern_for_owner_name = re.compile(r'\b([A-Z\s]+)\b(?=\d{5}|\bDate Received\b)')
        # name_match = re.search(pattern_for_owner_name, trademarks_text)
        # Extract owner names from the beginning of each line in uppercase
        pattern_for_owner_name = re.compile(r'^([A-Z\s]+)\b', re.MULTILINE)
        name_match = re.search(pattern_for_owner_name, trademarks_text)
        owner_name = name_match.group(1).strip() if name_match else ""
        
        trademarks = {
            "applicationNumber": re.search(r"(\d+)\s+Class", trademarks_text).group(1),
                    "owners": {
                        "name": owner_name
                    },
                    "deviceElements": ""
        }
        trademarks_info_corrections.append(trademarks)

    return trademarks_info_corrections

def extract_trademarks_info_int_applications(text):
    trademarks_info_int_applications = []

    # Updated regular expressions
    matches = re.finditer(
        r"(\b\d{5,}\b\s+Class[\s\S]*?)(?=\b\d{5,}\b\s+Class|$)",
        text
        # print(text)
    )

    
    for match in matches:

        trademarks_text = match.group(1)

        '''OWNER NAME'''
        # Extract name using regex  
        # pattern_for_owner_name = re.compile(r'\b([A-Z\s]+)\b(?=\d{5}|\bDate Received\b)')
        # name_match = re.search(pattern_for_owner_name, trademarks_text)
        # Extract owner names from the beginning of each line in uppercase
        pattern_for_owner_name = re.compile(r'^([A-Z\s]+)\b', re.MULTILINE)
        name_match = re.search(pattern_for_owner_name, trademarks_text)
        owner_name = name_match.group(1).strip() if name_match else ""
        
        '''DATE RECEIVED'''
        # Extract 'Date Received' using regex
        date_received_match = re.search(r"Date Received (\w+ \d+, \d{4})", trademarks_text)
        application_date = date_received_match.group(1) if date_received_match else ""

        '''OWNER ADDRESS'''
        # Extract address using regex
        pattern_for_owner_address =  re.compile(r'(?<=whose trade or business address is at)(.*?),\s*([\w\s]+)\.', re.DOTALL)
        address_match = re.search(pattern_for_owner_address, trademarks_text)
        owner_address = address_match.group(1).strip().replace('\n', '') if address_match else ""
        owner_country = address_match.group(2).strip() if address_match else ""
        # Concatenate country to address
        if owner_address and owner_country:
            owner_address += f", {owner_country}"

        '''REPRESENTATIVE NAME'''
        # Extract text after "Address for" up to the end of the line
        pattern_for_representative_name = re.compile(r'Address for (.+)$', re.MULTILINE)
        rep_name_match = re.search(pattern_for_representative_name, trademarks_text)
        rep_name = rep_name_match.group(1).strip() if rep_name_match else ""

        '''REPRESENTATIVE ADDRESS'''
        # Extract text in front of "Service"
        pattern_for_rep_address = re.compile(r'Service (.+)$', re.MULTILINE)
        rep_address_match = re.search(pattern_for_rep_address, trademarks_text)
        rep_address = rep_address_match.group(1).strip() if rep_address_match else ""


        '''NICE CLASS'''
        # Extract class number using regex
        pattern_for_class_number = re.compile(r'Class (\d+)')
        class_number_match = re.search(pattern_for_class_number, trademarks_text)
        class_number = class_number_match.group(1).strip() if class_number_match else ""
        
        '''goodServiceDescription'''
        # Extract text after "Class Number" until UPPERCASE words are found
        pattern_for_class_text = re.compile(r'Class \d+\s*(.*?)\b[A-Z]+\b', re.DOTALL)
        class_text_match = re.search(pattern_for_class_text, trademarks_text)
        class_text = class_text_match.group(1).strip().replace('\n', ',')  if class_text_match else ""

        
        trademarks = {
            "registrationNumber": re.search(r"(\d+)\s+Class", trademarks_text).group(1),
                    "SubsequentDesignationDate": application_date,
                    "owners": {
                        "name": owner_name,
                        "address": owner_address
                    },
                    "onwers": {
                        "country": owner_country
                    },
                    "representatives": {
                        "name": rep_name,
                        "address": rep_address,
                        "country": ""
                    },
                    "verbalElements": "",
                    "classifications": {
                        "niceClass": class_number,
                        "goodServiceDescription": class_text
                    },
                    "priorities": {
                        "country": ""
                    }
        }
        trademarks_info_int_applications.append(trademarks)
    return trademarks_info_int_applications


def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

# def create_json_structure(trademarks_info):
#     json_structure = {"sections": [{"title": "Applications", "trademarks": trademarks_info}]}
    
#     return json_structure

# def main():
#     pdf_path = "TT20231101-42.pdf"
#     output_file = f"output_tt_upwards_{pdf_path}.json"

#     text = extract_text_from_pdf(pdf_path)
#     trademarks_info = extract_trademarks_info(text)
#     json_structure = create_json_structure(trademarks_info)
#     save_to_json(json_structure, output_file)
#     print(f"Output saved to {output_file}")

# if __name__ == "__main__":
#     main()


'''CREATES STRUCTURE ONE BY ONE'''
def create_json_structure(trademarks_info, trademarks_info_corrections, trademarks_info_int_applications):
    json_structure = {
        "sections": [
            {"title": "Applications", "trademarks": trademarks_info},
            {"title": "Corrections", "trademarks": trademarks_info_corrections},
            {"title": "International Applications", "trademarks": trademarks_info_int_applications}
        ]
    }
    return json_structure

def main():
    pdf_path = "TT20231101-42.pdf"
    output_file = f"output_tt_{pdf_path}.json"

    text = extract_text_from_pdf(pdf_path)
    trademarks_info = extract_trademarks_info(text)
    trademarks_info_corrections = extract_trademarks_info_corrections(text)
    trademarks_info_int_applications = extract_trademarks_info_int_applications(text)

    json_structure = create_json_structure(trademarks_info, trademarks_info_corrections, trademarks_info_int_applications)
    save_to_json(json_structure, output_file)
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()

