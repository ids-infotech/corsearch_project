import json
import pycountry
import re

from pdf_01 import *

# Initialize a global counter for tradeMark numbers
global_trade_mark_counter = -1
country_names = set(country.name.lower() for country in pycountry.countries)

def split_data(input_data):
    classifications = []
    for entry in input_data:
        # Extract niceClass and goodSeviceDescription using regular expressions
        match = re.match(r'(\d+)\s+(.+)', entry)
        if match:
            nice_class, description = match.groups()
            # Create a dictionary for each entry and append it to the classifications list
            classifications.append({
                "niceClass": nice_class,
                "goodServiceDescription": description.strip()
            })
    return classifications

def transform_data(input_file, output_file):
    global global_trade_mark_counter  # Declare the global variable

    with open(input_file, 'r', encoding='utf-8') as file:
        original_data = json.load(file)

    transformed_data = {}

    for category, entries in original_data.items():
        # Reset the counter at the beginning of each category
        global_trade_mark_counter = -1

        new_entries = {}
        for entry in entries:
            global_trade_mark_counter += 1  # Increment the tradeMark number for each entry
            trade_mark_key = f"tradeMark {global_trade_mark_counter}"  # Include a space in the key

            filtered_trademark_data = {
                "applicationNumber": None,
                "applicationDate": None,
              
                "expiryDate": None,
            
                "owners": [
                    {
                        "name": None,
                        "address": "Null",
                        "country": None
                    }
                ],
                "representatives": [
                    {
                        "name": None,
                        "address": None,
                        "country": None
                    }
                ],
                "verbalElements": None,
            }

            owner_name = ""
            in_owners_section = False
            owner_address = ""
            in_owner_address_section = False
            owner_country = None
            rep_name = ""
            in_representative_section = False
            rep_address = ""
            country_found = False
            verbal_element = ""
            classifications = []
            produits_data = ""

            for key, value in entry.items():
                new_info = []
                for i, info in enumerate(value):
                    if info.startswith('Numéro de dépôt'):
                        info = info.replace('Numéro de dépôt', 'applicationNumber')
                        application_number = info.split(':')[1].strip()
                        filtered_trademark_data["applicationNumber"] = application_number
                        new_info.append(f"applicationNumber: {application_number}")

                    elif info.startswith('Date de dépôt'):
                        info = info.replace('Date de dépôt', 'applicationDate')
                        application_date = info.split(':')[1].strip()
                        filtered_trademark_data["applicationDate"] = application_date
                        new_info.append(f"applicationDate: {application_date}")

                    elif info.startswith('Nom de la Marque:'):
                        verbal_element += info.split(':')[-1].strip()
                        next_line_index = i + 1
                        while next_line_index < len(value):
                            next_line_value = value[next_line_index]
                            if next_line_value.startswith('Titulaire'):
                                break
                            verbal_element += ' ' + next_line_value
                            next_line_index += 1

                    elif info.startswith('Titulaire'):
                        in_owners_section = True
                        owner_name += info.split(':')[-1].strip()
                        next_line_index = i + 1
                        while next_line_index < len(value):
                            next_line_value = value[next_line_index]
                            if next_line_value.startswith('Adresse') or next_line_value.startswith('Mandataire'):
                                break
                            owner_name += ' ' + next_line_value
                            next_line_index += 1

                    elif info.startswith('Adresse'):
                        owner_address += info.split(':')[-1].strip()
                        in_owner_address_section = True
                        next_line_index = i + 1
                        while next_line_index < len(value):
                            next_line_value = value[next_line_index]
                            if next_line_value.startswith('Mandataire'):
                                break
                            owner_address += ' ' + next_line_value
                            next_line_index += 1

    
                        for country_name in country_names:
                            if country_name.lower() in owner_address.lower() or country_name.lower().replace(" ", "") in owner_address.lower():
                                owner_country = "United States of America" if country_name == "united states" else country_name.capitalize()
                                break

                        filtered_trademark_data["owners"][0]["address"] = owner_address.strip() or None
                        filtered_trademark_data["owners"][0]["country"] = owner_country

                        in_owner_address_section = False



                        # in_owner_address_section = True
                        # owner_address += info.split(':')[-1].strip()
                        # next_line_index = i + 1
                        # while next_line_index < len(value):
                        #     next_line_value = value[next_line_index]
                        #     if next_line_value.startswith('Mandataire'):
                        #         break
                        #     owner_address += ' ' + next_line_value
                        #     next_line_index += 1

                        #     for country_name in country_names:
                        #         if country_name in owner_address or country_name.replace(" ", "") in owner_address:
                        #             owner_country = country_name
                        #             break

                        #     if owner_country:
                        #         break

                    elif info.startswith('Mandataire'):
                        in_representative_section = True
                        rep_name += info.split(':')[-1].strip()
                        next_line_index = i + 1
                        while next_line_index < len(value):
                            next_line_value = value[next_line_index]
                            if next_line_value.startswith('Produits ou services désignés :'):
                                break
                            rep_name += ' ' + next_line_value
                            next_line_index += 1

                            for country_name in country_names:
                                if country_name in rep_name.lower() or country_name.replace(" ", "") in rep_name.lower():
                                    filtered_trademark_data["representatives"][0]["country"] = country_name.capitalize()
                                    country_found = True
                                    break

                            if country_found:
                                break

                    elif info.startswith('Echéance'):
                        info = info.replace('Echéance', 'expiryDate')
                        expiry_date = info.split(':')[-1].strip()
                        filtered_trademark_data["expiryDate"] = expiry_date
                        new_info.append(f"expiryDate: {expiry_date}")

                    elif info.startswith('Produits ou services désignés :'):
                        found_produits = True
                        parts = info.split(":")
                        if len(parts) > 1:
                            produits_data += parts[1].strip()
                        if info.endswith(']'):
                            found_produits = False
                        next_line_index = i + 1
                        while next_line_index < len(value):
                            next_line_value = value[next_line_index].strip()
                            if next_line_value.startswith('Produits ou services désignés :') or next_line_value.endswith(']') or 'Echéance' in next_line_value:
                                break
                            produits_data += ' ' + next_line_value 
                            next_line_index += 1
                            if next_line_value.endswith(']'):
                                found_produits = False
                                break


                filtered_trademark_data["verbalElements"] = verbal_element.strip() or None
                if '.' in produits_data:
                    if produits_data.count('.') == 1:
                        produits_data_list = [item.strip() for item in produits_data.split('."')]
                    else:
                        produits_data_list = [item.strip() for item in produits_data.split('.')]
                else:
                    produits_data_list = [produits_data.strip()]
                # print(produits_data_list)
              
                
                produits_data_list = list(filter(None, produits_data_list))  # Remove empty strings from the list
               
                #function calling 
                classifications_data=split_data(produits_data_list)
                filtered_trademark_data["classifications"] = [classifications_data]
               
               
              
                
                  

                if in_owners_section:
                    filtered_trademark_data["owners"][0]["name"] = owner_name.strip()
                    in_owners_section = False

                # if in_owner_address_section:
                #     filtered_trademark_data["owners"][0]["address"] = owner_address.strip() or None
                #     filtered_trademark_data["owners"][0]["country"] = owner_country
                #     in_owner_address_section = False

                if in_representative_section:
                    filtered_trademark_data["representatives"][0]["name"] = rep_name.strip()
                    filtered_trademark_data["representatives"][0]["address"] = rep_address.strip() or None
                    in_representative_section = False

                if (
                    filtered_trademark_data["applicationNumber"] is not None
                    and filtered_trademark_data["applicationDate"] is not None
                ):
                    new_entries[trade_mark_key] = [filtered_trademark_data]

        transformed_data[category] = new_entries

    with open(output_file, 'w', encoding='utf-8') as output_file:
        json.dump(transformed_data, output_file, ensure_ascii=False, indent=4)

# Example usage
json_file_path = r'temp_output\TN20230623-252.json'
output_json_file_path = r'temp_output\TN20230623-252.json'
transform_data(json_file_path, output_json_file_path)