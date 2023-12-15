import fitz
import json
import os 

def pdf_Extraction_Bhutan(pdf_file, output_json_folder):
    def fix_structure(data):
        for section, section_data in data.items():
            i = 0
            while i < len(section_data) -1:
                if section_data[i].startswith('(210):'):
                    key = section_data[i]
                    if i + 1 < len(section_data):
                        value = section_data[i + 1]
                        # Check if the value already has a colon
                        if not value.startswith(":"):
                            section_data[i] = f"{key}  {value}"
                        else:
                            section_data[i] = f"{key} {value}"
                        del section_data[i + 1]
                i += 1

    exclude_words = [ "Representative","Application", "Number", "Disclaimer", "Colour", "Date", "Goods/Services", "Successfull","Examination","Marks"
                     ]

    doc = fitz.open(pdf_file)
    found_data = {}
    in_section = False
    current_section = []
    section_counter = 1

    for page in range(len(doc)):
        text = doc[page].get_text()

        lines = text.split("\n")

        for line in lines:
            # Exclude specific words from the line before processing
            words = line.split()
            filtered_words = [word for word in words if word not in exclude_words]
            updated_line = ' '.join(filtered_words)

            if "(210)" in line:
                if in_section:
                    found_data[f"tradeMark {section_counter}"] = current_section
                    current_section = []
                    section_counter += 1

                in_section = True

            if in_section and updated_line.strip():  # Check for non-empty lines
                current_section.append(updated_line)

    if in_section:
        found_data[f"tradeMark {section_counter}"] = current_section

    doc.close()

    # Fix the data structure
    fix_structure(found_data)

    # Save the modified data into a JSON file section-wise excluding the first tradeMark field
    output_data = {}
    for idx, (section, section_data) in enumerate(found_data.items()):
        output_data[f"tradeMark {idx}"] = section_data

    # Exclude the first tradeMark field if present
    if "tradeMark 0" in output_data:
        del output_data["tradeMark 0"]


    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)
    pdf_filename = os.path.splitext(os.path.basename(pdf_file))[0]
    output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")

    

    with open(output_json_path, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)

# Specify the PDF file
pdf_file = r'input_pdf\BT20230215-106.pdf'
output_json_folder = r'temp_output'

# Call the merged function
pdf_Extraction_Bhutan(pdf_file,output_json_folder)
