import fitz  # PyMuPDF
import json
import re


def extract_heading():
    pass


def get_headings_of_sections(config):
    # Initialize variables
    start_heading_pattern = re.compile(config.get(
        'start_heading_pattern', r'Numéro de dépôt :'))
    end_heading_pattern = re.compile(
        config.get('end_heading_pattern', r'Numéro de dépôt :'))

    identifier_pattern = re.compile(config.get(
        'identifier_pattern', r'TN/E.*'))

    return start_heading_pattern, end_heading_pattern, identifier_pattern


def extract_text(pdf_path, config_path, output_json_path):
    # Load PDF document
    doc = fitz.open(pdf_path)

    # Load config from JSON file
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    start_heading_pattern, end_heading_pattern, identifier_pattern = get_headings_of_sections(
        config)

    extracted_data = {}  # Use a nested dictionary for extracted data

    # Iterate through pages
    for page_number in range(doc.page_count):
        page = doc[page_number]
        text = page.get_text()

        page_text_len = len(text)
        extracted_text_len = 0

        # extracted_sub_sections = []

        print(f"\nExxtracting text from page {page_number}")

        sub_section = 1

        while extracted_text_len <= page_text_len:

            # Find the start and end indices using regular expressions
            start_match = start_heading_pattern.search(
                text, extracted_text_len)

            end_match = end_heading_pattern.search(
                text, start_match.end() if start_match else extracted_text_len)

            # Extract text based on matches
            if start_match:
                start_index = start_match.start()
                if end_match:
                    end_index = end_match.start()
                else:
                    end_index = len(text)

                extracted_text_len += len(text[start_index:end_index])

                extracted_text = text[start_index:end_index].strip()

                # identifier_match = identifier_pattern.search(
                #     extracted_text)  # Add this line to find the identifier

                # Get the identifier if found
                # identifier = identifier_match.group().strip() if identifier_match else None

                #  Store extracted text and identifier in the nested dictionary
                extracted_data[f'Page_{page_number + 1}_{sub_section}'] = {
                    'content': [text for text in extracted_text.split("\n") if text.strip()],
                }

                print(f"extracted subsection {sub_section}")
                sub_section += 1

            else:
                extracted_data[f'Page_{page_number + 1}'] = {
                    'content': [],
                }
                print(f"NO subsections found")
                break

    # Close the PDF document
    doc.close()
    # Save extracted data to JSON file with utf-8 encoding
    with open(output_json_path, 'w', encoding='utf-8') as output_file:
        json.dump(extracted_data, output_file, ensure_ascii=False, indent=2)


# Example usage
pdf_path = 'Tunsia No. 424 date 4-1-21.pdf'
config_path = 'Tunisa config.json'
output_json_path = 'output.json'  # You can replace this with a dynamic path
extract_text(pdf_path, config_path, output_json_path)