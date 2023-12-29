import re
import json


def populate_json_structure(structure, data):
    if isinstance(structure, dict):
        for key, value in structure.items():
            if isinstance(value, (dict, list)):
                populate_json_structure(value, data)
            elif key in data:
                structure[key] = data[key]
    elif isinstance(structure, list):
        for item in structure:
            populate_json_structure(item, data)



def extract_data(sample_text, regex_patterns, json_structure):

    extracted_data = {}
    for key, pattern in regex_patterns.items():
        match = re.search(pattern, sample_text, re.IGNORECASE)
        if match:
            extracted_data[key] = match.group()

    populated_structure = json_structure.copy()  # copy to avoid modifying the original structure
    populate_json_structure(populated_structure, extracted_data)
    return populated_structure


if __name__ == "__main__":
    pass