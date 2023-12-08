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


    # Upwards regular expressions
    matches = re.finditer(r"(Trade Marks Journal, Publication Date:.*?)(?=\b\d{5,}\b\s+Class)", text, re.DOTALL)
    # print(text)
    
    for match in matches:
        trademarks_text = match.group(1)
        
        '''REGEX FOR  viennaClasses'''
        # Define the regex pattern for CFE text
        pattern_for_cfe_text = re.compile(r"CFE \(\d+\)\s*(.*?)(?=\n\n|CFE \(\d+\)|$)", re.DOTALL)
        cfe_text_match = re.search(pattern_for_cfe_text, trademarks_text)
        cfe_text = cfe_text_match.group(1).strip() if cfe_text_match else ""

        '''REGEX FOR VERBAL ELEMENTS'''
        # Isolate the last line of trademarks_text
        last_line = trademarks_text.strip().split('\n')[-1]

        # Add a space after "2023" if it's present
        last_line = re.sub(r"(2023)([A-Z])", r"\1 \2", last_line)

        # Updated regex pattern to include numbers and special characters
        pattern_for_verbal_elements = re.compile(r"([A-Z&]{2,}(?:\s[A-Z&0-9]{1,}){0,2})$")
        verbal_elements_match = re.search(pattern_for_verbal_elements, last_line)
        verbal_elements = verbal_elements_match.group().strip() if verbal_elements_match else ""

        '''COLOURS (issue would be spelling)'''
        # Define the regex pattern for capturing the line including the phrase up to the first full stop
        pattern_for_colors_line = re.compile(r"(THE APPLICANT CLAIMS THE COLOURS.*?\.)")
        colors_line_match = re.search(pattern_for_colors_line, trademarks_text)
        colors_line = colors_line_match.group(1).strip() if colors_line_match else ""

        '''DISCLAIMER'''
        # The pattern assumes the verbal element is in uppercase and up to three words, or starts with 'CFE'
        pattern_for_registration_text = re.compile(
            r"(REGISTRATION OF THIS MARK SHALL GIVE.*?)(?=\n[A-Z]{2,}(?:\s[A-Z]{2,}){0,2}$|\nCFE)",
            re.DOTALL
        )

        # Search for the pattern
        registration_text_match = re.search(pattern_for_registration_text, trademarks_text)
        disclaimer_text = registration_text_match.group(1).strip().replace('\n', '') if registration_text_match else ""

        '''PRIORITIES NUMBER'''
        # Define the regex pattern for capturing the number between "APPLICATION NO." and "DATED"
        pattern_for_application_no = re.compile(r"APPLICATION NO\.\s*(\d+/\d+,\d+)\s*DATED", re.DOTALL)
        application_no_match = re.search(pattern_for_application_no, trademarks_text)
        priorities_no = application_no_match.group(1).strip() if application_no_match else ""

        '''PRIORITIES DATE'''
        # Define the regex pattern for capturing the date after "DATED"
        pattern_for_date = re.compile(r"DATED\s*(.*?)(?=\.)", re.DOTALL)
        date_match = re.search(pattern_for_date, trademarks_text)
        date_text = date_match.group(1).strip() if date_match else ""

        '''PRIORITIES COUNTRY'''
        # Define the regex pattern for extracting the country name
        pattern_for_country_name = re.compile(r"BASED ON A\s*(.*?)(?=\n|APPLICATION)", re.DOTALL)
        country_name_match = re.search(pattern_for_country_name, trademarks_text)
        country_name = country_name_match.group(1).strip() if country_name_match else ""

        trademarks = {
            "applicationNumber": "",
            "applicationDate": "",
            "owners": {
                "name": "",
                "address": "",
                "country": ""
            },
            "verbalElements": verbal_elements,
            "deviceElements": "",
            "classifications": {
                "niceClass": "",
                "goodServiceDescription": ""
            },
            "disclaimer": disclaimer_text,
            "representatives": {
                "name": "",
                "address": "",
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

        '''REGEX FOR VERBAL ELEMENTS'''
        # Isolate the last line of trademarks_text
        last_line = trademarks_text.strip().split('\n')[-1]

        # Add a space after "2023" if it's present
        last_line = re.sub(r"(2023)([A-Z])", r"\1 \2", last_line)

        # Updated regex pattern to include numbers and special characters
        pattern_for_verbal_elements = re.compile(r"([A-Z&]{2,}(?:\s[A-Z&0-9]{1,}){0,2})$")
        verbal_elements_match = re.search(pattern_for_verbal_elements, last_line)
        verbal_elements = verbal_elements_match.group().strip() if verbal_elements_match else ""

        '''PRIORITIES COUNTRY'''
        # Define the regex pattern for extracting the country name
        pattern_for_country_name = re.compile(r"BASED ON A\s*(.*?)(?=\n|APPLICATION)", re.DOTALL)
        country_name_match = re.search(pattern_for_country_name, trademarks_text)
        country_name = country_name_match.group(1).strip() if country_name_match else ""
    
        trademarks = {
            "registrationNumber": "",
                    "SubsequentDesignationDate": "",
                    "owners": {
                        "name": "",
                        "address": ""
                    },
                    "onwers": {
                        "country": ""
                    },
                    "representatives": {
                        "name": "",
                        "address": "",
                        "country": ""
                    },
                    "verbalElements": verbal_elements,
                    "classifications": {
                        "niceClass": "",
                        "goodServiceDescription": ""
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
    output_file = f"output_tt_upwards_{pdf_path}.json"

    text = extract_text_from_pdf(pdf_path)
    trademarks_info = extract_trademarks_info(text)
    trademarks_info_corrections = extract_trademarks_info_corrections(text)
    trademarks_info_int_applications = extract_trademarks_info_int_applications(text)

    json_structure = create_json_structure(trademarks_info, trademarks_info_corrections, trademarks_info_int_applications)
    save_to_json(json_structure, output_file)
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
