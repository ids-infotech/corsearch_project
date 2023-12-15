import json
import logging

def update_structure_with_clippings_TUNISIA(input_structure_file, input_clippings_file, output_structure_file, log_file):
    # Set up logging with a simplified log format
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(message)s')

    # Load data from structure.json
    with open(input_structure_file, 'r', encoding='utf-8') as f_structure:
        structure_data = json.load(f_structure)

    # Load data from clippings.json
    with open(input_clippings_file, 'r', encoding='utf-8') as f_clippings:
        clippings_data = json.load(f_clippings)

    # Specify the nested keys
    nested_keys = headings = ["MARQUES ETRANGERES", "PUBLICATION DES MARQUES NATIONALES", "MARQUES INTERNATIONALES"]  # Add your actual nested keys

    # Statistics counters
    total_entries = 0
    added_clippings = 0
    added_device_element = 0
    added_binary_content = 0
    missing_clippings = 0
    missing_device_element = 0
    missing_binary_content = 0

    # Iterate over each nested key
    for nested_key in nested_keys:
        # Check if the nested key exists in the structure data
        if nested_key in structure_data:
            # Access the nested trademark data
            nested_trademark_data = structure_data[nested_key]

            # Iterate over trademark sections in the nested structure
            for trademark_name, trademark_data in nested_trademark_data.items():
                # Extract the registration number from the trademark data
                application_number = trademark_data[0].get("applicationNumber") if trademark_data else None

                # Increment total_entries counter
                total_entries += 1

                # Check if the registration number exists in clippings_data
                if application_number in clippings_data:
                    # Extract content data from clippings_data
                    content_data = clippings_data[application_number].get("content_data", [])

                    # Track whether clippings, deviceElement, and binaryContent were added for this trademark
                    clippings_added = False
                    device_element_added = False
                    binary_content_added = False

                    # Track missing data
                    missing_data = []

                    # Log information for this trademark
                    log_info = f"Application Number: {application_number}"

                    # Check if "coordinates" field exists in any entry_data
                    coordinates_exist = any("coordinates" in entry_data for entry_data in content_data)

                    # Log whether coordinates were found or not
                    if coordinates_exist:
                        logging.info(f"{log_info}")
                    else:
                        logging.info(f"No coordinates found for {log_info}")
                        missing_data.append("Coordinates")
                    new_entries = []  # Initialize an empty list outside the loop
                    for i, entry_data in enumerate(content_data):
                        # Check if "coordinates" field exists in entry_data
                        if "coordinates" in entry_data:
                            # Extract coordinates from clippings_data
                            x0 = entry_data["coordinates"].get("x0", 0.0)
                            y0 = entry_data["coordinates"].get("y0", 0.0)
                            x1 = entry_data["coordinates"].get("x1", 0.0)
                            y1 = entry_data["coordinates"].get("y1", 0.0)
                          
                            new_entry1 = entry_data.get("deviceElements", "")
                            new_entry =  {
                                    "point1": [x0, y0],
                                    "point2": [x1, y1],
                                    "binaryContent": entry_data.get("binaryContent", "")
                                }
                            new_entries.append(new_entry)
                            nested_trademark_data[trademark_name][0]["deviceElements"] = new_entry1
                            nested_trademark_data[trademark_name][0]["clippings"] = new_entries





                    # Iterate over content data entries
                    # for i, entry_data in enumerate(content_data):
                    #     # Check if "coordinates" field exists in entry_data
                    #     if "coordinates" in entry_data:
                    #         # Extract coordinates from clippings_data
                    #         x0 = entry_data["coordinates"].get("x0", 0.0)
                    #         y0 = entry_data["coordinates"].get("y0", 0.0)
                    #         x1 = entry_data["coordinates"].get("x1", 0.0)
                    #         y1 = entry_data["coordinates"].get("y1", 0.0)

                    #         # Create a new entry based on the structure of the original trademark entry
                    #         if isinstance(trademark_data, list):
                    #             # If trademark_data is a list, assume it contains dictionaries
                    #             new_entry = {
                    #                 "deviceElements": entry_data.get("deviceElements", ""),
                    #                 "clippings": {
                    #                     "point1": [x0, y0],
                    #                     "point2": [x1, y1],
                    #                     "binaryContent": entry_data.get("binaryContent", "")
                    #                 }
                    #             }
                    #         else:
                    #             # If trademark_data is a dictionary
                    #             new_entry = trademark_data.copy()

                    #             # Set coordinates, binaryContent, and deviceElements for the new entry
                    #             new_entry["clippings"] = {
                    #                 "point1": [x0, y0],
                    #                 "point2": [x1, y1],
                    #                 "binaryContent": entry_data.get("binaryContent", "")
                    #             }
                    #             new_entry["deviceElements"] = entry_data.get("deviceElements", "")

                    #         # Append the new entry to the trademark entries
                    #         nested_trademark_data[trademark_name].append(new_entry)

                            # Set clippings_added to True
                            clippings_added = True

                            # Set device_element_added to True if "deviceElements" field exists in entry_data
                            if "deviceElements" in entry_data:
                                device_element_added = True
                            else:
                                missing_data.append("Device Element")

                            # Set binary_content_added to True if "binaryContent" field exists in entry_data
                            if "binaryContent" in entry_data:
                                binary_content_added = True
                            else:
                                missing_data.append("Binary Content")

                        # Log information for each entry
                        entry_info = f"Entry {i + 1} - "
                        if "coordinates" in entry_data:
                            entry_info += "Coordinates found"
                        else:
                            entry_info += "No coordinates found"

                        logging.info(f"{log_info}: {entry_info}")

                    # Log whether clippings, deviceElement, and binaryContent were added or not for this trademark
                    additional_info = []
                    if clippings_added:
                        added_clippings += 1
                        additional_info.append("Clippings added")
                    if device_element_added:
                        added_device_element += 1
                        additional_info.append("Device Element added")
                    if binary_content_added:
                        added_binary_content += 1
                        additional_info.append("Binary Content added")

                    # Log whether data was added or not for this trademark
                    if additional_info:
                        logging.info(f"{', '.join(additional_info)} ")
                    else:
                        logging.info(f"No data added for {log_info}")

                    # Log missing data
                    if missing_data:
                        logging.info(f"Missing data: {', '.join(missing_data)}")
                        # Increment missing data counters
                        if "Clippings" in missing_data:
                            missing_clippings += 1
                        if "Device Element" in missing_data:
                            missing_device_element += 1
                        if "Binary Content" in missing_data:
                            missing_binary_content += 1

            logging.info(f"Successfully processed nested key: {nested_key}")
        else:
            logging.warning(f"The key '{nested_key}' does not exist in the structure data.")

    # Log summary
    logging.info(f"\nTotal application entry - {total_entries}")
    logging.info(f"Added Clippings - {added_clippings}")
    logging.info(f"Added Device Element - {added_device_element}")
    logging.info(f"Added Binary Content - {added_binary_content}")
    logging.info(f"Missing Clippings - {missing_clippings}")
    logging.info(f"Missing Device Element - {missing_device_element}")
    logging.info(f"Missing Binary Content - {missing_binary_content}")
    output_structure_file = r'temp_output\TN20230623-252.json'

    # Save the updated structure.json
    with open(output_structure_file, 'w', encoding='utf-8') as f_updated_structure:
        json.dump(structure_data, f_updated_structure, ensure_ascii=False, indent=4)

    print("Structure file updated successfully.")

output_structure_file = r'temp_output\TN20230623-252.json'

# Example usage:
update_structure_with_clippings_TUNISIA(output_structure_file, 'output_252.json', output_structure_file, 'TN20230623-252_base64.txt')
