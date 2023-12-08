import json
import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_trademarks_info(text):
    
    trademarks_info = []
    
    matches = re.finditer(
        r'Applicant\s(.+?)Agent(.+?)Address\sfor\sService\s([^A]+)Application\sNumber\s(\d{3}/\d{4})\sFiling\sDate\s(\w+\s\d{1,2},\s\d{4})\sClass\(es\)\s(.+?)(Applicant|$)',
        text,
        re.DOTALL
    )
    for match in matches:
    
        class_values = re.findall(r'\b\d{1,2}\b', match.group(6))
        nice_class = ", ".join(class_values)
       
        address_for_service = match.group(3).strip()

        second_comma_index = address_for_service.split(',')

        agent1 = match.group(2)
        agent = agent1.split("\n", 1)[0]

        trademark_info = {
            "applicationNumber": match.group(4),
            "applicationDate": match.group(5),
            "owners": {
                "name": match.group(1).strip(),
            },
            "representatives": {
                "name": agent,
                "address": second_comma_index[:-1],
                "country": second_comma_index[-1]
            },
            "verbalElements": "",
            "deviceMarks":"",
            "classifications": {
                "niceClass": nice_class,
                "goodServiceDescription": match.group(6).strip()
            },
            "Colors":"",
            "priorities": {
                "number": "",
                "date": "",
                "country": ""
            },
            "disclaimer": ""
        }
       
        trademarks_info.append(trademark_info)
    return trademarks_info

def extract_priority_claims(text):
    priority_claims = []

    matches = re.finditer(r'Priority Claim\s+Date:\s+([^\n]+)\s+Number:\s+([^\n]+)\s+Country:\s+([^\n]+)', text)

    for match in matches:
        priority_claim = {
            "date": match.group(1).strip(),
            "number": match.group(2).strip(),
            "country": match.group(3).strip()
        }
        priority_claims.append(priority_claim)

    return priority_claims


def create_json_structure(trademarks_info):
    json_structure = {"sections": [{"title": "Applications", "trademarks": trademarks_info}]}
    return json_structure

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def split_on_newline(data):
    if isinstance(data, dict):
        return {key: split_on_newline(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [split_on_newline(item) for item in data]
    elif isinstance(data, str):
        return data.split('\n')
    return data

def main():
    pdf_path = r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\VC\VC20221212-28.pdf"
    output_file = "output_sv.json"

    text = extract_text_from_pdf(pdf_path)
    trademarks_info = extract_trademarks_info(text)
    json_structure = create_json_structure(trademarks_info)
    json_structure_split = split_on_newline(json_structure)
    save_to_json(json_structure_split, output_file)
    priority_claims = extract_priority_claims(text)
    
    for claim in priority_claims:
        print("Priority Claim:")
        print(f"Date: {claim['date']}")
        print(f"Number: {claim['number']}")
        print(f"Country: {claim['country']}")
        print("---")
    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    main()