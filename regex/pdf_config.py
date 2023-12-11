import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text, config):
    data_entries = []

    for section_config in config["applicableFor"]["sections"]:
        if section_config["title"] == "Registrations":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["registrationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                registration_number = match.group(1) if match.group(1) else ""

                application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_220 = application_pattern.search(pdf_text[match.end():])
                application_date = match_220.group(1) if match_220 else ""

                expiry_pattern = re.compile(section_config["trademarks"]["expiryDate"])
                match_180 = expiry_pattern.search(pdf_text[match.end():])
                expiry_date = match_180.group(1) if match_180 else ""

                section_data["trademarks"].append({
                    "registrationNumber": registration_number,
                    "applicationDate": application_date,
                    "expiryDate": expiry_date
                })

            data_entries.append(section_data)

    return data_entries

# Load PDF text (replace 'your_pdf_path.pdf' with the actual path)
with fitz.open("MG20220230-102.pdf") as pdf_document:
    pdf_text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text()

# Load configuration JSON
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Extract data from PDF
result = extract_data_from_pdf(pdf_text, config)

# Save data to a JSON file
with open("pdf_config.json", "w") as output_file:
    json.dump(result, output_file, indent=4)

# Display the result
print("Data extracted and saved to extracted_data.json")
