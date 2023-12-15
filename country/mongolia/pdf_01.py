import fitz
import json
import os


def find_and_fix_data_MONGOLIA(pdf_file, output_json_folder):
    def fix_structure(data):
        for section, section_data in data.items():
            i = 0
            while i < len(section_data):
                if section_data[i].startswith('(') and not section_data[i].startswith('(170)'):
                    key = section_data[i]
                    if i + 1 < len(section_data):
                        value = section_data[i + 1]
                        # Check if the value already has a colon
                        if not value.startswith(":"):
                            section_data[i] = f"{key} : {value}"
                        else:
                            section_data[i] = f"{key} {value}"
                        del section_data[i + 1]
                i += 1

    exclude_words = ["Улсын", "бүртгэлийн", "дугаар", "Бүртгэлийн", "хүчинтэй", "байх", "хугацаа", "Мэдүүлгийн",
                     "улсын", "анхдагч", "огноо", "Давамгайлах", "Хэвлэлийн", "Эзэмшигчийн", "Итгэмжлэгдсэн",
                     "төлөөлөгчийн", "Хамгаалагдахгүй", 'үг,', "дүрс", "Барааны", "тэмдгийн", "дүрсийн", "олон",
                     "улсын", "ангилал", "дардас.", "нэр", "Барааны", "тэмдгийн", "өнгийн", "ялгаа", "Барааны",
                     "тэмдгийн", "бараа,", "үйлчилгээний", "олон", "улсын", "ангилал,", "ашиглах", "бараа",
        'Монгол', 'Оюуны', 'Өмчийн', 'Газар',"үйлчилгээний", "тэмдэг.", 'Нэр ','УЛСЫН', 'БҮРТГЭЛД','БАРААНЫ','ТЭМДЭГ','АВСАН',"Office",
        "of","Mongolia","REGISTERED","TRADEMARK","жагсаалт", "(511)"
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

            if "(111)" in line:
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

    # Save the modified data into a JSON file section-wise
    output_data = {}
    for section, section_data in found_data.items():
        output_data[section] = section_data

    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)
    pdf_filename = os.path.splitext(os.path.basename(pdf_file))[0]
    output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")

    with open(output_json_path, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)

# Specify the PDF file
pdf_file = r'input_pdf\MN20230531-05.pdf'

output_json_folder = r'temp_output'  
       
# if not os.path.exists(output_json_folder):
#     os.makedirs(output_json_folder)
#     pdf_filename = os.path.splitext(os.path.basename(pdf_file))[0]
# output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")



# Call the merged function
find_and_fix_data_MONGOLIA(pdf_file, output_json_folder)

