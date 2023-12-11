import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text, config):
    data_entries = []

    for section_config in config["applicableFor"]["sections"]:
        if section_config["title"] == "Registrations":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["registrationNumber"])
            application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
            expiry_pattern = re.compile(section_config["trademarks"]["expiryDate"])

            owners_patterns = section_config["trademarks"]["owners"]
            owners_pattern = {
                "name": re.compile(owners_patterns[0]["name"]),
                "address": re.compile(owners_patterns[0]["address"]),
                "country": re.compile(owners_patterns[0]["country"])
            }

            for match in registration_pattern.finditer(pdf_text):
                registration_number = match.group(1) if match.group(1) else ""

                match_220 = application_pattern.search(pdf_text[match.end():])
                application_date = match_220.group(1) if match_220 else ""

                match_180 = expiry_pattern.search(pdf_text[match.end():])
                expiry_date = match_180.group(1) if match_180 else ""

                match_732 = owners_pattern["name"].search(pdf_text[match.end():])
                owner_name = match_732.group(1) if match_732 else ""

                match_732_address = owners_pattern["address"].search(pdf_text[match.end():])
                owner_address = f"{match_732_address.group(1)} {match_732_address.group(2)}" if match_732_address and match_732_address.group(2) else ""


                match_732_country = owners_pattern["country"].search(pdf_text[match.end():])
                owner_country = match_732_country.group(1) if match_732_country else ""

                section_data["trademarks"].append({
                    "registrationNumber": registration_number,
                    "applicationDate": application_date,
                    "expiryDate": expiry_date,
                    "owners": [
                        {
                            "name": owner_name.strip(),
                            "address": owner_address.strip(),
                            "country": owner_country.strip()
                        }
                    ]
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
with open("owners.json", "w", encoding= 'utf-8') as output_file:
    json.dump(result, output_file, indent=4)

# Display the result
print("Data extracted and saved to extracted_data.json")
