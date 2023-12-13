import json
import fitz  # PyMuPDF
import pdfplumber
import re

def read_config(config_file):
    with open(config_file, 'r', encoding='utf-8') as config:
        return json.load(config)

def extract_images_from_page(page):
    images = page.get_images(full=True)
    return images

def extract_text_from_page(page):
    text = page.get_text()
    return text

def extract_field(text, regex_pattern):
    matches = re.finditer(regex_pattern, text)
    return [match.group(1) for match in matches] if matches else None

def extract_trademarks_info(page, config):
    trademarks_info = []

    text = extract_text_from_page(page)
    file_number_pattern = re.compile(config["applicableFor"]["sections"][0]["trademarks"]["applicationNumber"])
    mark_name_pattern = re.compile(config["applicableFor"]["sections"][0]["trademarks"]["verbalElements"])
    applicant_pattern = re.compile(config["applicableFor"]["sections"][0]["trademarks"]["owners"]["name"])
    filing_date_pattern = re.compile(config["applicableFor"]["sections"][0]["trademarks"]["applicationDate"])
    agent_pattern = re.compile(config["applicableFor"]["sections"][0]["trademarks"]["representatives"]["name"])
    class_pattern = re.compile(config["applicableFor"]["sections"][0]["trademarks"]["classifications"]["niceClass"])

    # Debug prints
    print("Text:", text)

    file_numbers = extract_field(text, file_number_pattern)
    mark_names = extract_field(text, mark_name_pattern)
    applicants = extract_field(text, applicant_pattern)
    filing_dates = extract_field(text, filing_date_pattern)
    agents = extract_field(text, agent_pattern)
    classes = extract_field(text, class_pattern)

    # Debug prints
    print("File Numbers:", file_numbers)
    print("Mark Names:", mark_names)
    print("Applicants:", applicants)
    print("Filing Dates:", filing_dates)
    print("Agents:", agents)
    print("Classes:", classes)

    # Assuming all lists have the same length
    for i in range(len(file_numbers)):
        # Check if there are elements in applicants list and if the current index is valid
        if i < len(applicants):
            trademark_info = {
            "applicationNumber": file_numbers[i],
            "applicationDate": filing_dates[i],
            "owners": {
                    "name": applicants[i] if applicants[i] else "null",
                    "address": "",
                    "country": ""
                },
            "representatives": {
                    "name": "",
                    "address": "",
                    "country": ""
                },
                "verbalElements": mark_names[i] if mark_names[i] else "",
                "classifications": {
                    "niceClass": "",
                    "goodServiceDescription": ""
                },
                "priorities": {
                    "number": "",
                    "date": "",
                    "country": ""
                },
                "disclaimer": ""
            }
            trademarks_info.append(trademark_info)

    return trademarks_info


def extract_trademarks_info_from_pdf(pdf_path, config):
    trademarks_info = []

    doc = fitz.open(pdf_path)
    for page_number in range(doc.page_count):
        page = doc[page_number]
        trademarks_info_page = extract_trademarks_info(page, config)
        trademarks_info.extend(trademarks_info_page)

    return trademarks_info

def create_json_structure(config, trademarks_info):
    json_structure = {
        "sections": [
            {
                "title": config["applicableFor"]["sections"][0]["title"],
                "trademarks": trademarks_info
            }
        ]
    }
    return json_structure

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def main():
    config_file = "LC-2015-2023.json"
    pdf_path = "LC\LC20231016-42.pdf"
    output_file = "output.json"

    config = read_config(config_file)
    trademarks_info = extract_trademarks_info_from_pdf(pdf_path, config)
    json_structure = create_json_structure(config, trademarks_info)
    save_to_json(json_structure, output_file)
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()
