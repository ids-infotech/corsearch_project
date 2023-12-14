import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text, config):
    data_entries = []
    application_number_list = []
    owner_name_list = []
    representatives_address_list_1 = []
    representatives_address_list_2 = []
    cleaned_goods_data = []

    for section_config in config["applicableFor"]["sections"]:
        
        if section_config["title"] == "Applications":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(0)
                application_number_list.append(applicationNumber)
                cleaned_list = [item.replace('\n', '').replace('Filing Date', '') for item in application_number_list]

                application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_220 = application_pattern.search(pdf_text[match.end():])
                application_date = match_220.group(0) if match_220 else ""

                onwers_name = re.compile(section_config["trademarks"]["owners"]["name"])
                match_E_06 = onwers_name.search(pdf_text[match.end():])
                onwers_name =  match_E_06.group(0) if  match_E_06 else ""
                owner_name_list.append(onwers_name)
                cleaned_list_owner = [item.replace('\n', '').replace('Applicant', '') for item in owner_name_list]

                representatives_name = re.compile(section_config["trademarks"]["representatives"]["name"])
                match_E_09 = representatives_name.search(pdf_text[match.end():])
                representatives_name =  match_E_09.group(1) if  match_E_09 else ""

                representatives_address = re.compile(section_config["trademarks"]["representatives"]["address"])
                match_E_07 = representatives_address.search(pdf_text[match.end():])
                representatives_address_1 =  match_E_07.group(2) if match_E_07 else ""
                representatives_address_list_1.append(representatives_address_1)
                representatives_address_2 =  match_E_07.group(3) if match_E_07 else ""
                representatives_address_list_2.append(representatives_address_2)
                
                goods = re.compile(section_config["trademarks"]["classifications"]["goodServiceDescription"])
                match_E_16 =  goods.search(pdf_text[match.end():])
                goods =  match_E_16.group(0) if  match_E_16 else ""
                goods_data = goods.split('\n')
                text_to_remove = "COMMERCE AND INTELLECTUAL PROPERTY OFFICE "
                cleaned_list_goods = [item for item in goods_data if item != text_to_remove and item != " " and item != "" and item != "___________________________________________________________________________________ "]
                
                pattern = re.compile(r"^\d+", re.MULTILINE)
                matches = pattern.findall(goods)

                priorities_number = re.compile(section_config["trademarks"]["priorities"]["number"])
                match_E_09 = priorities_number.search(pdf_text[match.end():])
                priorities_number =  match_E_09.group(1) if  match_E_09 else ""
                

                priorities_date = re.compile(section_config["trademarks"]["priorities"]["date"])
                match_E_09 = priorities_date.search(pdf_text[match.end():])
                priorities_date =  match_E_09.group(1) if  match_E_09 else ""
                

                priorities_country = re.compile(section_config["trademarks"]["priorities"]["country"])
                match_E_09 = priorities_country.search(pdf_text[match.end():])
                priorities_country =  match_E_09.group(0) if  match_E_09 else ""
                split_text = priorities_country.split('\n', 1)
                result = split_text[0]
                split_text = result.split(':', 1)
                if len(split_text) < 2:
                    result = "Null"
                else:
                    result = split_text[1]

                
                # if cleaned_list[0] == ' Priority Claim ':
                #     registration_pattern = re.compile(r'Priority Claim\s*\S*\s*\n', re.DOTALL)
                #     for match in registration_pattern.finditer(pdf_text):
                #         applicationNumber = match.group(0)
                #         application_number_list.append(applicationNumber)
                #         cleaned_list = [item.replace('\n', '').replace('Priority Claim', '').replace('Filing Date', '') for item in application_number_list]
                #         if len(cleaned_list) == 2:
                #             cleaned_list = cleaned_list[1]
                #             # print(cleaned_list)
                #         if len(cleaned_list) == 3:
                #             cleaned_list = cleaned_list[2]
                #             # print(cleaned_list)
                #         if len(cleaned_list) == 4:
                #             cleaned_list = cleaned_list[3]
                #             # print(cleaned_list)
                        

                #         section_data["trademarks"].append({
                #         "applicationNumber": cleaned_list,
                #             "applicationDate": "",
                #             "owners": {
                #                 "name": cleaned_list_owner
                #             },
                #             "representatives": {
                #                 "name": "",
                #                 "address": "",
                #                 "country": ""
                #             },
                #             "verbalElements": "",
                #             "deviceMarks": "",
                #             "classifications": {
                #                 "niceClass": "",
                #                 "goodServiceDescription": ""
                #             },
                #             "Colors": "",
                #             "priorities": {
                #                 "number": "",
                #                 "date": "",
                #                 "country": ""
                #             },
                #             "Disclaimer": ""
                #         })
                #     data_entries.append(section_data)
                        

                section_data["trademarks"].append({
                "applicationNumber": cleaned_list,
                    "applicationDate": application_date,
                    "owners": {
                        "name": cleaned_list_owner
                    },
                    "representatives": {
                        "name": representatives_name,
                        "address": representatives_address_1.split(',')[:-1],
                        "country": representatives_address_1.split(',')[-1] + representatives_address_2
                    },
                    "verbalElements": "",
                    "deviceMarks": "",
                    "classifications": {
                        "niceClass": matches[:],
                        "goodServiceDescription": cleaned_list_goods
                    },
                    "Colors": "",
                    "priorities": {
                        "number": priorities_number,
                        "date": priorities_date,
                        "country": result
                    },
                    "Disclaimer": ""
                })
                application_number_list.clear()
                owner_name_list.clear()
                representatives_address_list_1.clear()
                representatives_address_list_2.clear()
                matches.clear()
                
            data_entries.append(section_data)

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
        # print(pdf_text)

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
