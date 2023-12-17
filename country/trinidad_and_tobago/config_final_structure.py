import json
import pdfplumber
import re
import os
import logging
import fitz

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

config = load_config('config_regex_updated.json')

'''CALLING REGULAR EXPRESSIONS FROM CONFIG.JSON'''
application_number_regex = config['applicableFor']['sections'][0]['trademarks']['applicationNumber']
application_date_regex = config['applicableFor']['sections'][0]['trademarks']['applicationDate']
name_regex = config['applicableFor']['sections'][0]['trademarks']['owners']['name']
address_regex = config['applicableFor']['sections'][0]['trademarks']['owners']['address'] 
nice_class_regex = config['applicableFor']['sections'][0]['trademarks']['classifications']['niceClass']
goodServiceDescription_regex = config['applicableFor']['sections'][0]['trademarks']['classifications']['goodServiceDescription']
rep_name_regex = config['applicableFor']['sections'][0]['trademarks']['representatives']['name']
rep_address_regex = config['applicableFor']['sections'][0]['trademarks']['representatives']['address']
disclaimer_regex = config['applicableFor']['sections'][0]['trademarks']['disclaimer']
verbalElements_regex = config['applicableFor']['sections'][0]['trademarks']['verbalElements']
viennaClasses_regex = config['applicableFor']['sections'][0]['trademarks']['viennaClasses']
color_regex = config['applicableFor']['sections'][0]['trademarks']['color']
priorities_number_regex = config['applicableFor']['sections'][0]['trademarks']['priorities']['number']
priorities_date_regex = config['applicableFor']['sections'][0]['trademarks']['priorities']['date']
priorities_country_regex = config['applicableFor']['sections'][0]['trademarks']['priorities']['country']

'''MADRID MARKS'''
registrationNumber_regex = config['applicableFor']['sections'][2]['trademarks']['registrationNumber']
SubsequentDesignationDate_regex = config['applicableFor']['sections'][2]['trademarks']['SubsequentDesignationDate']

def extract_trademarks_combined(text):

    # Get all upward and downward matches
    upward_matches = list(re.finditer(r"(Trade Marks Journal, Publication Date:.*?)(?=\b\d{5,}\b\s+Class)", text, re.DOTALL))
    downward_matches = list(re.finditer(r"(\b\d{5,}\b\s+Class[\s\S]*?)(?=\b\d{5,}\b\s+Class|$)", text))
    
    if len(upward_matches) != len(downward_matches):
        raise ValueError("The number of upward and downward matches is not the same.")
    
    trademarks_info = []
    
    for i in range(len(upward_matches)):
        upward_text = upward_matches[i].group(1)
        downward_text = downward_matches[i].group(1)
        
        '''REGEX FOR  viennaClasses'''
        # Define the regex pattern for CFE text
        pattern_for_cfe_text = re.compile(viennaClasses_regex, re.DOTALL)
        cfe_text_match = re.search(pattern_for_cfe_text, upward_text)
        cfe_text = cfe_text_match.group(1).strip() if cfe_text_match else None

        '''REGEX FOR VERBAL ELEMENTS'''
        # Isolate the last line of upward_text
        last_line = upward_text.strip().split('\n')[-1]

        # Add a space after "2023" if it's present
        last_line = re.sub(r"(2023)([A-Z])", r"\1 \2", last_line)

        # Updated regex pattern to include numbers and special characters
        pattern_for_verbal_elements = re.compile(verbalElements_regex)
        verbal_elements_match = re.search(pattern_for_verbal_elements, last_line)
        verbal_elements = verbal_elements_match.group().strip() if verbal_elements_match else None

        '''COLOURS (issue would be spelling)'''
        # Define the regex pattern for capturing the line including the phrase up to the first full stop
        pattern_for_colors_line = re.compile(color_regex)
        colors_line_match = re.search(pattern_for_colors_line, upward_text)
        colors_line = colors_line_match.group(1).strip() if colors_line_match else None

        '''DISCLAIMER'''
        # The pattern assumes the verbal element is in uppercase and up to three words, or starts with 'CFE'
        pattern_for_registration_text = re.compile(disclaimer_regex,re.DOTALL)

        # Search for the pattern
        registration_text_match = re.search(pattern_for_registration_text, upward_text)
        disclaimer_text = registration_text_match.group(1).strip().replace('\n', '') if registration_text_match else None

        '''PRIORITIES NUMBER'''
        # Define the regex pattern for capturing the number between "APPLICATION NO." and "DATED"
        pattern_for_application_no = re.compile(priorities_number_regex, re.DOTALL)
        application_no_match = re.search(pattern_for_application_no, upward_text)
        priorities_no = application_no_match.group(1).strip() if application_no_match else None

        '''PRIORITIES DATE'''
        # Define the regex pattern for capturing the date after "DATED"
        pattern_for_date = re.compile(priorities_date_regex, re.DOTALL)
        date_match = re.search(pattern_for_date, upward_text)
        date_text = date_match.group(1).strip() if date_match else None

        '''PRIORITIES COUNTRY'''
        # Define the regex pattern for extracting the country name
        pattern_for_country_name = re.compile(priorities_country_regex, re.DOTALL)
        country_name_match = re.search(pattern_for_country_name, upward_text)
        country_name = country_name_match.group(1).strip() if country_name_match else None


        '''APPLICATION NUMBER'''
        pattern_application_number = re.compile(application_number_regex)
        application_number_match = re.search(pattern_application_number, downward_text)
        application_number = application_number_match.group(1) if application_number_match else None

        # Extract the necessary data from the downward_text
        '''DATE RECEIVED'''
        # Extract 'Date Received' using regex
        date_received_match = re.search(application_date_regex, downward_text)
        application_date = date_received_match.group(1) if date_received_match else None
        
        '''OWNER NAME'''
        # Extract owner names from the beginning of each line in uppercase
        pattern_for_owner_name = re.compile(name_regex, re.MULTILINE)
        name_match = re.search(pattern_for_owner_name, downward_text)
        owner_name = name_match.group(1).strip() if name_match else None

        '''OWNER ADDRESS'''
        # Extract address using regex
        pattern_for_owner_address =  re.compile(address_regex, re.DOTALL)
        address_match = re.search(pattern_for_owner_address, downward_text)
        owner_address = address_match.group(1).strip().replace('\n', '') if address_match else None
        owner_country = address_match.group(2).strip() if address_match else None
        # Concatenate country to address
        if owner_address and owner_country:
            owner_address += f", {owner_country}"

        '''NICE CLASS'''
        # Extract class number using regex
        pattern_for_class_number = re.compile(nice_class_regex)
        class_number_match = re.search(pattern_for_class_number, downward_text)
        class_number = class_number_match.group(1).strip() if class_number_match else None
        
        '''goodServiceDescription'''
        # Extract text after "Class Number" until UPPERCASE words are found
        pattern_for_class_text = re.compile(goodServiceDescription_regex, re.DOTALL)
        class_text_match = re.search(pattern_for_class_text, downward_text)
        class_text = class_text_match.group(1).strip().replace('\n', ',')  if class_text_match else None

        '''REPRESENTATIVE NAME'''
        # Extract text after "Address for" up to the end of the line
        pattern_for_representative_name = re.compile(rep_name_regex, re.MULTILINE)
        rep_name_match = re.search(pattern_for_representative_name, downward_text)
        rep_name = rep_name_match.group(1).strip() if rep_name_match else None

        '''REPRESENTATIVE ADDRESS'''
        # Extract text in front of "Service"
        pattern_for_rep_address = re.compile(rep_address_regex, re.MULTILINE)
        rep_address_match = re.search(pattern_for_rep_address, downward_text)
        rep_address = rep_address_match.group(1).strip() if rep_address_match else None
        
        # Create a combined dictionary with all the extracted data
        trademarks = {
            "applicationNumber": application_number,
            "applicationDate": application_date,
            "owners": {
                "name": owner_name,
                "address": owner_address,
                "country": owner_country
            },
            "verbalElements": verbal_elements,
            "deviceElements": "",
            "classifications": {
                "niceClass": class_number,
                "goodServiceDescription": class_text
            },
            "disclaimer": disclaimer_text,
            "representatives": {
                "name": rep_name,
                "address": rep_address,
                "country": ""
            },
            "viennaClasses": cfe_text,
            "color": colors_line,
            "priorities": {
                "number": priorities_no,
                "date": date_text,
                "country": country_name
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
    )

    for match in matches:
        trademarks_text = match.group(1)

        '''OWNER NAME'''
        pattern_for_owner_name = re.compile(name_regex, re.MULTILINE)
        name_match = re.search(pattern_for_owner_name, trademarks_text)
        owner_name = name_match.group(1).strip() if name_match else None
        
        '''APPLICATION NUMBER'''
        pattern_application_number = re.compile(application_number_regex)
        application_number_match = re.search(pattern_application_number, trademarks_text)
        application_number = application_number_match.group(1) if application_number_match else None

        trademarks = {
            "applicationNumber": application_number,
                    "owners": {
                        "name": owner_name
                    },
                    "deviceElements": ""
        }
        trademarks_info_corrections.append(trademarks)

    return trademarks_info_corrections


def extract_trademarks_info_int_applications(text):
    trademarks_info_int_applications = []

    # Get all upward and downward matches
    upward_matches = list(re.finditer(r"(Trade Marks Journal, Publication Date:.*?)(?=\b\d{5,}\b\s+Class)", text, re.DOTALL))
    downward_matches = list(re.finditer(r"(\b\d{5,}\b\s+Class[\s\S]*?)(?=\b\d{5,}\b\s+Class|$)", text))
    
    if len(upward_matches) != len(downward_matches):
        raise ValueError("The number of upward and downward matches is not the same.")
    
    trademarks_info = []
    
    for i in range(len(upward_matches)):
        upward_text = upward_matches[i].group(1)
        downward_text = downward_matches[i].group(1)

        
        '''registrationNumber_regex NUMBER'''
        pattern_application_number = re.compile(registrationNumber_regex)
        application_number_match = re.search(pattern_application_number, downward_text)
        application_number = application_number_match.group(1) if application_number_match else None
        

        # Extract the necessary data from the downward_text
        '''SubsequentDesignationDate_regex RECEIVED'''
        # Extract 'Date Received' using regex
        date_received_match = re.search(SubsequentDesignationDate_regex, downward_text)
        application_date = date_received_match.group(1) if date_received_match else None
        
        '''OWNER NAME'''
        # Extract owner names from the beginning of each line in uppercase
        pattern_for_owner_name = re.compile(name_regex, re.MULTILINE)
        name_match = re.search(pattern_for_owner_name, downward_text)
        owner_name = name_match.group(1).strip() if name_match else None

        '''OWNER ADDRESS'''
        # Extract address using regex
        pattern_for_owner_address =  re.compile(address_regex, re.DOTALL)
        address_match = re.search(pattern_for_owner_address, downward_text)
        owner_address = address_match.group(1).strip().replace('\n', '') if address_match else None
        owner_country = address_match.group(2).strip() if address_match else None
        # Concatenate country to address
        if owner_address and owner_country:
            owner_address += f", {owner_country}"

        '''NICE CLASS'''
        # Extract class number using regex
        pattern_for_class_number = re.compile(nice_class_regex)
        class_number_match = re.search(pattern_for_class_number, downward_text)
        class_number = class_number_match.group(1).strip() if class_number_match else None
        
        '''goodServiceDescription'''
        # Extract text after "Class Number" until UPPERCASE words are found
        pattern_for_class_text = re.compile(goodServiceDescription_regex, re.DOTALL)
        class_text_match = re.search(pattern_for_class_text, downward_text)
        class_text = class_text_match.group(1).strip().replace('\n', ',')  if class_text_match else None

        '''REPRESENTATIVE NAME'''
        # Extract text after "Address for" up to the end of the line
        pattern_for_representative_name = re.compile(rep_name_regex, re.MULTILINE)
        rep_name_match = re.search(pattern_for_representative_name, downward_text)
        rep_name = rep_name_match.group(1).strip() if rep_name_match else None

        '''REPRESENTATIVE ADDRESS'''
        # Extract text in front of "Service"
        pattern_for_rep_address = re.compile(rep_address_regex, re.MULTILINE)
        rep_address_match = re.search(pattern_for_rep_address, downward_text)
        rep_address = rep_address_match.group(1).strip() if rep_address_match else None

        '''PRIORITIES COUNTRY'''
        # Define the regex pattern for extracting the country name
        pattern_for_country_name = re.compile(priorities_country_regex, re.DOTALL)
        country_name_match = re.search(pattern_for_country_name, upward_text)
        country_name = country_name_match.group(1).strip() if country_name_match else None

        trademarks = {
            "registrationNumber": application_number,
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
                        "country": country_name
                    }
        }
        trademarks_info_int_applications.append(trademarks)
    return trademarks_info_int_applications


def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def create_json_structure(trademarks_info, trademarks_info_corrections, trademarks_info_int_applications):
    json_structure = {
        "sections": [{"title": "Applications", "trademarks": trademarks_info},
                     {"title": "Corrections", "trademarks": trademarks_info_corrections},
                     {"title": "International Applications (Madrid)", "trademarks": trademarks_info_int_applications}]
                                }
    
    return json_structure

def main():
    pdf_path = "TT20231025-41.pdf"
    output_file = f"TRIAL_OUTPUT_{pdf_path}.json"

    text = extract_text_from_pdf(pdf_path)
    trademarks_info = extract_trademarks_combined(text)
    trademarks_info_corrections = extract_trademarks_info_corrections(text)
    trademarks_info_int_applications = extract_trademarks_info_int_applications(text)

    json_structure = create_json_structure(trademarks_info, trademarks_info_corrections, trademarks_info_int_applications)
    save_to_json(json_structure, output_file)
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
