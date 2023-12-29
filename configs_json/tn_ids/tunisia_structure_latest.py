import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text, config):
    applications_section = []
    madrid_section = []
    renewals_section = []
    correction_section = []

    for section_config in config["applicableFor"]["sections"]:
        if section_config["title"] == "Applications":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(1).strip() if match.group(1) else None

                application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_application_pattern = application_pattern.search(pdf_text[match.end():])
                application_date = match_application_pattern.group(1).strip() if match_application_pattern else None

                onwers_name_pattern = re.compile(section_config["trademarks"]["owners"]["name"])
                match_owners_name = onwers_name_pattern.search(pdf_text[match.end():])
                owners_name =  match_owners_name.group(1).strip().replace('\n', '') if  match_owners_name else None
    
                owners_address_pattern = re.compile(section_config["trademarks"]["owners"]["address"])
                match_owners_address = owners_address_pattern.search(pdf_text[match.end():])
                owners_address =  match_owners_address.group(1).strip().replace('\n', '') if  match_owners_address else None

                owners_country_pattern = re.compile(section_config["trademarks"]["owners"]["country"])
                match_owners_country =  owners_country_pattern.search(pdf_text[match.end():])
                owners_country =  match_owners_country.group(1).strip().replace('\n','') if  match_owners_country else None

                representatives_country_pattern = re.compile(section_config["trademarks"]["representative"]["country"])
                match_rep_country = representatives_country_pattern.search(pdf_text[match.end():])
                representatives_country=  match_rep_country.group(1).strip().replace('\n', '') if  match_rep_country else None

                representatives_address_pattern = re.compile(section_config["trademarks"]["representative"]["address"])
                match_rep_address = representatives_address_pattern.search(pdf_text[match.end():])
                representatives_address =  match_rep_address.group(1).strip().replace('\n', '') if  match_rep_address else None

                representatives_name_pattern = re.compile(section_config["trademarks"]["representative"]["name"])
                match_representatives_name = representatives_name_pattern.search(pdf_text[match.end():])
                representatives_name =  match_representatives_name.group(1).strip().replace('\n', '') if  match_representatives_name else None

                nice_class_pattern = re.compile(section_config["trademarks"]["classifications"]["niceClass"])
                match_nice_class =  nice_class_pattern.search(pdf_text[match.end():])
                nice_class =  match_nice_class.group(1).strip() if  match_nice_class else None
                

                section_data["trademarks"].append({
                    "applicationNumber": applicationNumber,
                    "applicationDate": application_date,
                    "deviceElements" : "",
                    "verbalElements": None,
                    "owners": [
                        {
                            "name": owners_name,
                            "address": owners_address,
                            "country": owners_country
                        }
                    ],
                    "representative": [
                        {
                           "name":representatives_name,
                            "address": representatives_address,
                            "country": representatives_country
                        }
                    ],
                    "classifications": [
                        {
                            "niceClass": nice_class,
                            "goodServiceDescription": "FIX FOR MULTIPLE",                         
                        }
                    ],

                    
                })
            applications_section.append(section_data)
        
        if section_config["title"] == "Madrid Applications":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(1).strip() if match.group(1) else None

                application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_application_pattern = application_pattern.search(pdf_text[match.end():])
                application_date = match_application_pattern.group(1).strip() if match_application_pattern else None

                onwers_name_pattern = re.compile(section_config["trademarks"]["owners"]["name"])
                match_owners_name = onwers_name_pattern.search(pdf_text[match.end():])
                owners_name =  match_owners_name.group(1).strip().replace('\n', '') if  match_owners_name else None

                owners_address_pattern = re.compile(section_config["trademarks"]["owners"]["address"])
                match_owners_address = owners_address_pattern.search(pdf_text[match.end():])
                owners_address =  match_owners_address.group(1).strip().replace('\n','')  if  match_owners_address else None

                owners_country_pattern = re.compile(section_config["trademarks"]["owners"]["country"])
                match_owners_country =  owners_country_pattern.search(pdf_text[match.end():])
                owners_country =  match_owners_country.group(1).strip().replace('\n','') if  match_owners_country else None

                representatives_name_pattern = re.compile(section_config["trademarks"]["representative"]["name"])
                match_representatives_name = representatives_name_pattern.search(pdf_text[match.end():])
                representatives_name =  match_representatives_name.group(1).strip().replace('\n', '') if  match_representatives_name else None

                nice_class_pattern = re.compile(section_config["trademarks"]["classifications"]["niceClass"])
                match_nice_class =  nice_class_pattern.search(pdf_text[match.end():])
                nice_class =  match_nice_class.group(1).strip() if  match_nice_class else None

                goods_description_madrid_pattern = re.compile(section_config["trademarks"]["classifications"]["goodServiceDescription"])
                match_goods_description_madrid =  goods_description_madrid_pattern.search(pdf_text[match.end():])
                goodServiceDescription_madrid =  match_goods_description_madrid.group(1).strip().replace('\n','') if  match_goods_description_madrid else None

                # verbalElements_pattern = re.compile(section_config["trademarks"]["verbalElements"])
                # match_verbal_element = verbalElements_pattern.search(pdf_text[match.end():])
                # verbalElements =  match_verbal_element.group(1).strip().replace('\n','') if  match_verbal_element else None

                verbalElements_pattern = re.compile(section_config["trademarks"]["verbalElements"])
                match_verbal_element = verbalElements_pattern.search(pdf_text[match.end():])
                verbalElements = match_verbal_element.group(1).replace('\n','') if match_verbal_element and match_verbal_element.group(1).strip() else None

                section_data["trademarks"].append({
                    "applicationNumber": applicationNumber,
                    "applicationDate": application_date,
                    "owners": [
                        {
                            "name": owners_name,
                            "address": owners_address,
                            "country": owners_country
                        }
                    ],
                    "deviceElements" : None,
                    "verbalElements": verbalElements,
                    "representative": [
                        {
                           "name":representatives_name,
                           "address" : None,
                           "country" : None
                        }
                    ],

                    "classifications": [
                        {
                            "niceClass": nice_class,
                            "goodServiceDescription": "GETTING WRONG TEXT"                        
                        }
                    ],               
                })
            madrid_section.append(section_data)

        if section_config["title"] == "Renewals":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(1).strip() if match.group(1) else None

                application_date_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_application_pattern = application_date_pattern.search(pdf_text[match.end():])
                application_date = match_application_pattern.group(1).strip() if match_application_pattern else None

                onwers_name_pattern = re.compile(section_config["trademarks"]["owners"]["name"])
                match_owners_name = onwers_name_pattern.search(pdf_text[match.end():])
                owners_name =  match_owners_name.group(1).strip() if  match_owners_name else None

                owners_address_pattern = re.compile(section_config["trademarks"]["owners"]["address"])
                match_owners_address = owners_address_pattern.search(pdf_text[match.end():])
                owners_address =  match_owners_address.group(1).strip().replace('\n','')  if  match_owners_address else None

                owners_country_pattern = re.compile(section_config["trademarks"]["owners"]["country"])
                match_owners_country =  owners_country_pattern.search(pdf_text[match.end():])
                owners_country =  match_owners_country.group(1).strip().replace('\n','') if  match_owners_country else None

                representatives_name_pattern = re.compile(section_config["trademarks"]["representative"]["name"])
                match_representatives_name = representatives_name_pattern.search(pdf_text[match.end():])
                representatives_name =  match_representatives_name.group(1).strip().replace('\n', '') if  match_representatives_name else None

                nice_class_pattern = re.compile(section_config["trademarks"]["classifications"]["niceClass"])
                match_nice_class =  nice_class_pattern.search(pdf_text[match.end():])
                nice_class =  match_nice_class.group(1).strip() if  match_nice_class else None

                goodServiceDescription_renewals_pattern = re.compile(section_config["trademarks"]["classifications"]["goodServiceDescription"])
                match_goodsServiceDescription_renewals = goodServiceDescription_renewals_pattern.search(pdf_text[match.end():])
                goodsServiceDescription_renewals =  match_goodsServiceDescription_renewals.group(1).strip().replace('\n','') if  match_goodsServiceDescription_renewals else None

                expiry_date_pattern = re.compile(section_config["trademarks"]["publicationEvent"]["expiryDate"])
                match_expiry_date = expiry_date_pattern.search(pdf_text[match.end():])
                expiry_date =  match_expiry_date.group(1).strip().replace('\n','') if  match_expiry_date else None

                section_data["trademarks"].append({
                    "applicationNumber": applicationNumber,
                    "applicationDate": application_date,
                    "owners": [
                        {
                            "name": owners_name,
                            "address": owners_address,
                            "country": owners_country
                        }
                    ],
           
                    "representative": [
                         {
                           "name":representatives_name,
                           "address" : None,
                           "country" : None
                        }
                    ],

                    "classifications": [
                        {
                            "niceClass": nice_class,
                            "goodServiceDescription": goodsServiceDescription_renewals                     
                        }
                    ],
                    "publicationEvent" : [
                        {
                        "expiryDate": expiry_date
                        }
                    ]              
                })
            renewals_section.append(section_data)
        
        if section_config["title"] == "Corrections":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(2).strip() if match.group(1) else None

                comments_pattern = re.compile(section_config["trademarks"]["comments"])
                match_comments_pattern = comments_pattern.search(pdf_text[match.end():])
                comments = match_comments_pattern.group(1).strip().replace('\n','') if match_comments_pattern else None

                application_date_pattern_corrections = re.compile(section_config["trademarks"]["applicationDate"])
                match_application_date_corrections = application_date_pattern_corrections.search(pdf_text[match.end():])
                application_date = match_application_date_corrections.group(1).strip() if match_application_date_corrections else None
                
                onwers_name_pattern = re.compile(section_config["trademarks"]["owners"]["name"])
                match_owners_name = onwers_name_pattern.search(pdf_text[match.end():])
                owners_name =  match_owners_name.group(1).strip() if  match_owners_name else None

                owners_address_pattern = re.compile(section_config["trademarks"]["owners"]["address"])
                match_owners_address = owners_address_pattern.search(pdf_text[match.end():])
                owners_address =  match_owners_address.group(1).strip().replace('\n','')  if  match_owners_address else None

                owners_country_pattern = re.compile(section_config["trademarks"]["owners"]["country"])
                match_owners_country =  owners_country_pattern.search(pdf_text[match.end():])
                owners_country =  match_owners_country.group(1).strip().replace('\n','') if  match_owners_country else None

                representatives_country_pattern_corrections = re.compile(section_config["trademarks"]["representative"]["country"])
                match_representatives_country = representatives_country_pattern_corrections.search(pdf_text[match.end():])
                rep_country_corrections =  match_representatives_country.group(1).strip().replace('\n', '') if  match_representatives_country else None

                representatives_address_pattern_corrections = re.compile(section_config["trademarks"]["representative"]["address"])
                match_representative_address = representatives_address_pattern_corrections.search(pdf_text[match.end():])
                rep_address_corrections =  match_representative_address.group(1).strip().replace('\n', '') if  match_representative_address else None

                representatives_name_pattern_corrections = re.compile(section_config["trademarks"]["representative"]["name"])
                match_representatives_name = representatives_name_pattern_corrections.search(pdf_text[match.end():])
                rep_name_corrections =  match_representatives_name.group(1).strip().replace('\n', '') if  match_representatives_name else None

                section_data["trademarks"].append({
                        "applicationNumber": applicationNumber,
                        
                        "applicationDate": application_date,
                        "owners": [
                        {
                            "name": owners_name,
                            "address": owners_address,
                            "country": owners_country
                        }
                    ],
                        "comments" : comments,
                    "representative": [
                         {
                           "name":rep_name_corrections,
                           "address" : rep_address_corrections,
                           "country" : rep_country_corrections
                        }
                    ],
                })

            correction_section.append(section_data)
            print(section_data)

    return correction_section

# Load PDF text (replace 'your_pdf_path.pdf' with the actual path)
# Define start and end page numbers (Python uses 0-indexing)
start_page = 824
end_page = 827

# with fitz.open("TN20220722-440.pdf") as pdf_document:
#     pdf_text = ""
#     for page_num in range(pdf_document.page_count):
#         page = pdf_document[page_num]
#         pdf_text += page.get_text()

with fitz.open("TN20210401-424.pdf") as pdf_document:
    pdf_text = ""
    # Adjust the range in the loop to go from start_page to end_page
    for page_num in range(start_page, end_page):
        page = pdf_document[page_num]
        pdf_text += page.get_text()

print(pdf_text)

# Load configuration JSON
with open("TN-2019-2023_regex.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file,)

# Extract data from PDF
result = extract_data_from_pdf(pdf_text, config)

# Save data to a JSON file
with open("TN20210401-424_correction_section.json", "w",  encoding="utf-8") as output_file:
    json.dump(result, output_file, indent=4, ensure_ascii=False)

# Display the result
print("Data extracted and saved to extracted_data.json")
