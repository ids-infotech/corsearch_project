import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text, config):
    data_entries = []
    application_number = []

    for section_config in config["applicableFor"]["sections"]:
        
        if section_config["title"] == "Applications":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(0)
                application_number.append(applicationNumber)
                cleaned_list = [item.replace('\n', '').replace('Filing Date', '') for item in application_number]

                application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_220 = application_pattern.search(pdf_text[match.end():])
                application_date = match_220.group(1) if match_220 else ""
                print(application_date)

                if cleaned_list[0] == ' Priority Claim ':
                    registration_pattern = re.compile(r'Priority Claim\s*\S*\s*\n', re.DOTALL)
                    for match in registration_pattern.finditer(pdf_text):
                        applicationNumber = match.group(0)
                        application_number.append(applicationNumber)
                        # print(application_number[1])
                        cleaned_list = [item.replace('\n', '').replace('Priority Claim', '').replace('Filing Date', '') for item in application_number]
                        if len(cleaned_list) == 2:
                            cleaned_list = cleaned_list[1]
                            # print(cleaned_list)
                        if len(cleaned_list) == 3:
                            cleaned_list = cleaned_list[2]
                            # print(cleaned_list)
                        if len(cleaned_list) == 4:
                            cleaned_list = cleaned_list[3]
                            # print(cleaned_list)
                        

                        section_data["trademarks"].append({
                "applicationNumber": cleaned_list,
                    "applicationDate": application_date,
                    "owners": {
                        "name": ""
                    },
                    "representatives": {
                        "name": "",
                        "address": "",
                        "country": ""
                    },
                    "verbalElements": "",
                    "deviceMarks": "",
                    "classifications": {
                        "niceClass": "",
                        "goodServiceDescription": ""
                    },
                    "Colors": "",
                    "priorities": {
                        "number": "",
                        "date": "",
                        "country": ""
                    },
                    "Disclaimer": ""
                })
                    data_entries.append(section_data)
                        

                section_data["trademarks"].append({
                "applicationNumber": cleaned_list,
                    "applicationDate": "",
                    "owners": {
                        "name": ""
                    },
                    "representatives": {
                        "name": "",
                        "address": "",
                        "country": ""
                    },
                    "verbalElements": "",
                    "deviceMarks": "",
                    "classifications": {
                        "niceClass": "",
                        "goodServiceDescription": ""
                    },
                    "Colors": "",
                    "priorities": {
                        "number": "",
                        "date": "",
                        "country": ""
                    },
                    "Disclaimer": ""
                })
                application_number.clear()
            data_entries.append(section_data)
            break

    return data_entries

def save_text_to_file(text, file_path):
    with open(file_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)

# Load PDF text (replace 'your_pdf_path.pdf' with the actual path)
with fitz.open(r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\VC\VC20221212-28.pdf") as pdf_document:
    pdf_text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text()

# Load configuration JSON
with open(r"D:\python_projects\Corsearch\new files\config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file,)

# Extract data from PDF
result = extract_data_from_pdf(pdf_text, config)

# Save data to a JSON file
with open("pdf_config.json", "w",  encoding="utf-8") as output_file:
    json.dump(result, output_file, indent=4, ensure_ascii=False)

# Save PDF text to a text file
save_text_to_file(pdf_text, "output.txt")

# Display the result
print("Data extracted and saved to extracted_data.json")
