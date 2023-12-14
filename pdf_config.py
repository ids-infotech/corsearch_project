import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text, config):
    data_entries = []
    data_entries_1 = []

    for section_config in config["applicableFor"]["sections"]:
        if section_config["title"] == "Renewal":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(1) if match.group(1) else ""

                application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_220 = application_pattern.search(pdf_text[match.end():])
                application_date = match_220.group(1) if match_220 else ""

                registrationNumber = re.compile(section_config["trademarks"]["registrationNumber"])
                match_180 = registrationNumber.search(pdf_text[match.end():])
                registrationNumber = match_180.group(1) if match_180 else ""


                registrationDate = re.compile(section_config["trademarks"]["registrationDate"])
                match_E_04 = registrationDate.search(pdf_text[match.end():])
                registrationDate =  match_E_04.group(1) if  match_E_04 else ""


                onwers_name = re.compile(section_config["trademarks"]["owners"]["name"])
                match_E_06 = onwers_name.search(pdf_text[match.end():])
                onwers_name =  match_E_06.group(1) if  match_E_06 else ""

                onwers_address = re.compile(section_config["trademarks"]["owners"]["addrress"])
                match_E_07 = onwers_address.search(pdf_text[match.end():])
                onwers_address =  match_E_07.group(1) if  match_E_07 else ""

                onwers_country = re.compile(section_config["trademarks"]["owners"]["country"])
                match_E_08 =  onwers_country.search(pdf_text[match.end():])
                onwers_country =  match_E_08.group(1) if  match_E_08 else ""

                renewalDate = re.compile(section_config["trademarks"]["renewalDate"])
                match_E_05 = renewalDate.search(pdf_text[match.end():])
                renewalDate =  match_E_05.group(1) if  match_E_05 else ""

                expiryDate = re.compile(section_config["trademarks"]["expiryDate"])
                match_E_05 = expiryDate.search(pdf_text[match.end():])
                expiryDate =  match_E_05.group(1) if  match_E_05 else ""

                representatives_name = re.compile(section_config["trademarks"]["representatives"]["name"])
                match_E_09 = representatives_name.search(pdf_text[match.end():])
                representatives_name =  match_E_09.group(1) if  match_E_09 else ""

                nice = re.compile(section_config["trademarks"]["classifications"]["niceClass"])
                match_E_16 =  nice.search(pdf_text[match.end():])
                nice =  match_E_16.group(1) if  match_E_16 else ""

                # verbalElements = re.compile(section_config["trademarks"]["verbalElements"])
                # match_E_12 = verbalElements.search(pdf_text[match.end():])
                # verbalElements =  match_E_12.group(1) if  match_E_12 else ""
        
                section_data["trademarks"].append({
                    "applicationNumber": applicationNumber,
                    "applicationDate": application_date,
                    "registrationNumber": registrationNumber,
                    "registrationDate": registrationDate,
                    "owners": [
                        {
                            "name": onwers_name.strip(),
                            "addrress": onwers_address.strip(),
                            "country": onwers_country.strip()
                        }
                    ],
           
                    "renewalDate":renewalDate,
                    "expiryDate":expiryDate,
                    # "verbalElements":verbalElements,
                    "representatives": [
                        {
                            "name":representatives_name.strip(),
                            # "addrress": representatives_country.strip(),
                            # "country": representatives_country.strip()
                        }
                    ],

                    "classifications": [
                        {
                            "niceClass": nice.strip(),                          
                        }
                    ]
                })
            data_entries.append(section_data)
        
        if section_config["title"] == "Registration":
            section_data = {"title": section_config["title"], "trademarks": []}

            registration_pattern = re.compile(section_config["trademarks"]["applicationNumber"])
            for match in registration_pattern.finditer(pdf_text):
                applicationNumber = match.group(1) if match.group(1) else ""

                application_pattern = re.compile(section_config["trademarks"]["applicationDate"])
                match_220 = application_pattern.search(pdf_text[match.end():])
                application_date = match_220.group(1) if match_220 else ""

                registrationNumber = re.compile(section_config["trademarks"]["registrationNumber"])
                match_180 = registrationNumber.search(pdf_text[match.end():])
                registrationNumber = match_180.group(1) if match_180 else ""


                registrationDate = re.compile(section_config["trademarks"]["registrationDate"])
                match_E_04 = registrationDate.search(pdf_text[match.end():])
                registrationDate =  match_E_04.group(1) if  match_E_04 else ""


                onwers_name = re.compile(section_config["trademarks"]["owners"]["name"])
                match_E_06 = onwers_name.search(pdf_text[match.end():])
                onwers_name =  match_E_06.group(1) if  match_E_06 else ""

                onwers_address = re.compile(section_config["trademarks"]["owners"]["addrress"])
                match_E_07 = onwers_address.search(pdf_text[match.end():])
                onwers_address =  match_E_07.group(1) if  match_E_07 else ""

                onwers_country = re.compile(section_config["trademarks"]["owners"]["country"])
                match_E_08 =  onwers_country.search(pdf_text[match.end():])
                onwers_country =  match_E_08.group(1) if  match_E_08 else ""

              

                expiryDate = re.compile(section_config["trademarks"]["expiryDate"])
                match_E_05 = expiryDate.search(pdf_text[match.end():])
                expiryDate =  match_E_05.group(1) if  match_E_05 else ""

                representatives = re.compile(section_config["trademarks"]["representatives"]["name"])
                match_E_09 = representatives.search(pdf_text[match.end():])
                representatives =  match_E_09.group(1) if  match_E_09 else ""



                # representatives_country = re.compile(section_config["trademarks"]["representatives"]["country"])
                # match_E_09 = representatives_country.search(pdf_text[match.end():])
                # representatives_country =  match_E_09.group(1) if  match_E_09 else ""

                nice = re.compile(section_config["trademarks"]["classifications"]["niceClass"])
                match_E_16 =  nice.search(pdf_text[match.end():])
                nice =  match_E_16.group(1) if  match_E_16 else ""

                # verbalElements = re.compile(section_config["trademarks"]["verbalElements"])
                # match_E_12 = verbalElements.search(pdf_text[match.end():])
                # verbalElements =  match_E_12.group(1) if  match_E_12 else ""

                number = re.compile(section_config["trademarks"]["priority"]["number"])
                match_E_16 =  number.search(pdf_text[match.end():])
                number =  match_E_16.group(1) if  match_E_16 else ""


                date = re.compile(section_config["trademarks"]["priority"]["date"])
                match_E_16 =  date.search(pdf_text[match.end():])
                date =  match_E_16.group(1) if  match_E_16 else ""


                country = re.compile(section_config["trademarks"]["priority"]["country"])
                match_E_16 =   country.search(pdf_text[match.end():])
                country =  match_E_16.group(1) if  match_E_16 else ""




        
                section_data["trademarks"].append({
                    "applicationNumber": applicationNumber,
                    "applicationDate": application_date,
                    "registrationNumber": registrationNumber,
                    "registrationDate": registrationDate,
                    "owners": [
                        {
                            "name": onwers_name.strip(),
                            "addrress": onwers_address.strip(),
                            "country": onwers_country.strip()
                        }
                    ],
           
                    # "renewalDate":renewalDate,
                    "expiryDate":expiryDate,
                    # "verbalElements":verbalElements,
                    "representatives": [
                         {
                           "name":representatives.strip(),
                            # "addrress": representatives_country.strip(),
                            # "country": representatives_country.strip()
                        }
                    ],

                    "classifications": [
                        {
                            "niceClass": nice.strip(),                          
                        }
                    ],
                    "priority": [
                        {
                            "number": number.strip(),
                            "date": date.strip(), 
                            "country": country.strip(),                          
                        }
                    ],

                    
                })
            data_entries_1.append(section_data)

    return data_entries,data_entries_1

# Load PDF text (replace 'your_pdf_path.pdf' with the actual path)
with fitz.open("AW20220716-07.pdf") as pdf_document:
    pdf_text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text()

# Load configuration JSON
with open("AW-20190101-20211231.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file,)

# Extract data from PDF
result = extract_data_from_pdf(pdf_text, config)

# Save data to a JSON file
with open("pdf_config.json", "w",  encoding="utf-8") as output_file:
    json.dump(result, output_file, indent=4, ensure_ascii=False)

# Display the result
print("Data extracted and saved to extracted_data.json")
