import json

def update_structure_with_clippings(input_structure_file, input_clippings_file, output_structure_file):
    # Load data from structure.json
    with open(input_structure_file, 'r', encoding='utf-8') as f_structure:
        structure_data = json.load(f_structure)

    # Load data from clippings.json
    with open(input_clippings_file, 'r', encoding='utf-8') as f_clippings:
        clippings_data = json.load(f_clippings)

    # Iterate over trademark sections in structure.json
    for trademark_name, trademark_data in structure_data.items():
        # Check if the trademark name exists in clippings_data
        if trademark_name in clippings_data:
            # Extract content data from clippings_data
            content_data = clippings_data[trademark_name].get("content_data", [])

            # Iterate over content data entries
            for i, entry_data in enumerate(content_data):
                # Check if "coordinates" field exists in entry_data
                if "coordinates" in entry_data:
                    # Extract coordinates from clippings_data
                    x0 = entry_data["coordinates"].get("x0", 0.0)
                    y0 = entry_data["coordinates"].get("y0", 0.0)
                    x1 = entry_data["coordinates"].get("x1", 0.0)
                    y1 = entry_data["coordinates"].get("y1", 0.0)

                    # If trademark_data is a list, assume it contains dictionaries
                    if isinstance(trademark_data, list):
                        # Create a new entry for each content_data entry
                        new_entry = {
                            "clippings": {
                                "point1": [x0, y0],
                                "point2": [x1, y1],
                                "binaryContent": entry_data.get("binaryContent", ""),
                                "deviceElements": entry_data.get("deviceElements", "")

                            },
                            
                        }
                    else:
                        # Create a new entry based on the structure of the original trademark entry
                        new_entry = trademark_data.copy()

                        # Set coordinates and binaryContent for the new entry
                        new_entry["deviceElements"] = entry_data.get("deviceElements", "")
                        new_entry["clippings"] = {
                            "point1": [x0, y0],
                            "point2": [x1, y1]
                        }

                        new_entry["binaryContent"] = entry_data.get("binaryContent", "")
                        

                       

                    # Append the new entry to the trademark entries
                    structure_data[trademark_name].append(new_entry)

    # Save the updated structure.json
    with open(output_structure_file, 'w', encoding='utf-8') as f_updated_structure:
        json.dump(structure_data, f_updated_structure, ensure_ascii=False, indent=4)

    #print("Structure file updated successfully.")

# Example usage:
update_structure_with_clippings('final.json', 'output_DZ20230601-406.pdf.json', 'DZ-406.json')
