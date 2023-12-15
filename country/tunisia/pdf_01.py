import fitz
import json
import os


def is_numero_de_depot_line(line):
    return line.startswith("Numéro de dépôt :")

def extract_data_between_headings_from_pdf(pdf_file, output_file, stop_word=None, exclude_words=None):
    headings = ["MARQUES ETRANGERES", "PUBLICATION DES MARQUES NATIONALES", "MARQUES INTERNATIONALES", "PUBLICATION DES RENOUVELLEMENTS", "PUBLICATION DES RECTIFICATIFS"]
    current_heading = None
    current_section = []
    stop_extraction = False  # Flag to stop extraction if True

    doc = fitz.open(pdf_file)

    output_data = {}
    last_tradeMark_number = {}

    for page_num in range(len(doc)):
        if stop_extraction:
            break  # Stop processing pages if stop_extraction is True

        page = doc.load_page(page_num)
        page_text = page.get_text()

        for line in page_text.split('\n'):
            line = line.strip()

            # Additional cleaning conditions
            if line.strip().isdigit() or len(line.strip()) == 1 or (any(char.isdigit() for char in line) and line.strip().endswith('-')):
                continue

            if stop_word and line.lower() == stop_word.lower():
                stop_extraction = True
                break  # Stop extraction when stop_word is encountered

            # if line == "Muwassafat":
            #     continue

            if line in headings:
                if current_heading is not None and current_section:
                    last_number = last_tradeMark_number.get(current_heading, 0)
                    output_data[current_heading].append({f"tradeMark{last_number}": clean_empty_strings(current_section)})
                    current_section = []  # Reset current_section for the new heading

                current_heading = line
                if current_heading not in output_data:
                    output_data[current_heading] = []

            elif current_heading:
                if is_numero_de_depot_line(line):
                    if current_section:
                        last_number = last_tradeMark_number.get(current_heading, 0) + 1
                        output_data[current_heading].append({f"tradeMark{last_number}": clean_empty_strings(current_section)})
                        last_tradeMark_number[current_heading] = last_number
                        current_section = []  # Start a new section

                include_line = True
                if exclude_words:
                    for exclude_word in exclude_words:
                        line = line.replace(exclude_word, '').strip()

                # Check for duplicates before adding the line
                if include_line and line not in current_section:
                    current_section.append(line)

    doc.close()

    # Append the last section if it exists
    if current_heading is not None and current_section:
        last_number = last_tradeMark_number.get(current_heading, 0) + 1
        output_data[current_heading].append({f"tradeMark{last_number}": clean_empty_strings(current_section)})


    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)
    pdf_filename = os.path.splitext(os.path.basename(pdf_file))[0]
    output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")

    # Save the output_data to a JSON file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(output_data, json_file, ensure_ascii=False, indent=4)

def clean_empty_strings(data_list):
    return [item for item in data_list if item]

# Example usage:
pdf_file = r'input_pdf\TN20230623-252.pdf'
output_json_folder = r'temp_output'  
stop_word = "stop"
exclude_words = ["Classe", "start", "Muwassafat", "N°","425","440","447","455"]

extract_data_between_headings_from_pdf(pdf_file, output_json_folder, stop_word, exclude_words)