import fitz
import json

def find_and_fix_data(pdf_file):
    
    def fix_structure(data):
        for section, section_data in data.items():
            i = 0
        while i < len(section_data) - 1:  # Decreased the limit by 1 to avoid IndexError
            if section_data[i].startswith('(') and not section_data[i].startswith('(170)'):
                key = section_data[i]
                if i + 1 < len(section_data):
                    value = section_data[i + 1]
                    if not value.startswith(""):
                        section_data[i] = f"{key}\n{value}"
                    else:
                        if value[0].isdigit():
                            section_data[i] = key
                            section_data.insert(i + 1, value)
                        else:
                            section_data[i] = f"{key} {value}"
                            if i + 2 < len(section_data):  # Check if the index is within range
                                del section_data[i + 2]
            i += 1

    exclude_words = ["_____________________________________________", "____________________________________________", ]

    doc = fitz.open(pdf_file)
    found_data = {}
    in_section = False
    current_section = []
    section_counter = 1

    # Start reading from page 7
    for page in range(6, len(doc)):
        text = doc[page].get_text()

        lines = text.split("\n")

        for line in lines:
            words = line.split()
            filtered_words = [word for word in words if word not in exclude_words]
            updated_line = ' '.join(filtered_words)

            if "(111)" in line:
                if in_section:
                    found_data[f"tradeMark {section_counter}"] = current_section
                    current_section = []
                    section_counter += 1

                in_section = True

            if in_section and updated_line.strip():
                current_section.append(updated_line)

    if in_section:
        found_data[f"tradeMark {section_counter}"] = current_section

    doc.close()

    fix_structure(found_data)

    output_data = {}
    for section, section_data in found_data.items():
        output_data[section] = section_data

    with open('output.json', 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)

# Specify the PDF file
pdf_file = 'DZ20230601-406.pdf'

# Call the modified function
find_and_fix_data(pdf_file)



