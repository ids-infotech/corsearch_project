import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text, config):
    data_entries = []
    country_names = []

    for section_config in config["applicableFor"]["sections"]:
        if section_config["title"] == "Registrations":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["registrationNumber"])
            application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
            expiry_pattern = re.compile(section_config["trademarks"]["expiryDate"])

            # Dynamic owner section pattern from the config
            owner_pattern = re.compile(section_config["trademarks"]["owners"][0]["name"])

            # Dynamic representative section pattern from the config
            representative_pattern = re.compile(section_config["trademarks"]["representatives"][0]["name"])

            for match in registration_pattern.finditer(pdf_text):
                registration_number = match.group(1) if match.group(1) else ""

                match_220 = application_pattern.search(pdf_text[match.end():])
                application_date = match_220.group(1) if match_220 else ""

                match_180 = expiry_pattern.search(pdf_text[match.end():])
                expiry_date = match_180.group(1) if match_180 else ""

                # Find owner's name and address using the dynamic pattern
                match_owner = owner_pattern.search(pdf_text[match.end():])
                owner_info = match_owner.group(1).strip() if match_owner else ""

                # Split on the first occurrence of "/n"
                name_parts = owner_info.split("\n", 1)
                owner_name = name_parts[0].strip() if name_parts else ""

                # Remove newline characters from the address
                owner_address = name_parts[1].replace("\n", "").strip() if len(name_parts) > 1 else ""

                # Iterate through stored country names and check if they are in the address
                owner_country = ""
                for country_name in country_names:
                    if country_name.lower() in owner_address.lower():
                        owner_country = country_name
                        break

                # Find representative's name using the dynamic pattern
                match_representative = representative_pattern.search(pdf_text[match.end():])

                # Check if (740) is present before extracting the representative name
                if "(740)" in pdf_text[match.end():]:
                    representative_name = match_representative.group(1).strip() if match_representative else None
                else:
                    representative_name = None

                # Find (511) entries and extract niceClasses and goodServiceDescription
                match_511 = re.search(r"\(511\)\s*([\s\S]*?)(?=\(\d+\)|$)", pdf_text[match.end():])
                if match_511:
                    classification_text = match_511.group(1).strip()

                    # Split based on \n and check if each part starts with a number
                    classification_parts = classification_text.split("\n")
                    classifications = []

                    nice_classes = ""
                    goods_service_description = ""

                    for part in classification_parts:
                        # Check if the part starts with a number
                        if re.match(r"^\d+", part):
                            # If nice_classes already has content, add it to classifications
                            if nice_classes:
                                classifications.append({
                                    "niceClasses": nice_classes,
                                    "goodServiceDescription": goods_service_description
                                })
                                nice_classes = ""
                                goods_service_description = ""

                            nice_classes = part.strip()
                        else:
                            goods_service_description += part.strip() + " "

                    # Add the last set of nice_classes and goods_service_description
                    classifications.append({
                        "niceClasses": nice_classes,
                        "goodServiceDescription": goods_service_description.strip()
                    })

                    section_data["trademarks"].append({
                        "registrationNumber": registration_number,
                        "applicationDate": application_date,
                        "expiryDate": expiry_date,
                        "owners": [
                            {
                                "name": owner_name,
                                "address": owner_address,
                                "country": owner_country
                            }
                        ],
                        "representatives": [
                            {
                                "name": representative_name,
                                "address": "",
                                "country": "",
                            }
                        ],
                        "classifications": classifications
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
with open("c2.json", "r") as config_file:
    config = json.load(config_file)

# Extract data from PDF
result = extract_data_from_pdf(pdf_text, config)

# Save data to a JSON file
with open("classifications.json", "w", encoding='utf-8') as output_file:
    json.dump(result, output_file, indent=4, ensure_ascii=False)

# Display the result
print("Data extracted and saved to own_country.json")
