import fitz
import re
import json
from image_processing import *
import os 

resolution = 200

def bhutan_pdf_extraction(pdf_file_path):
    
    pdf_document = fitz.open(pdf_file_path)
    pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")
    section_data = {}
    section_num = 1

    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        page_text = page.get_text('text')

        matches = pattern.findall(page_text)

        for match in matches:
            if "(511) – NICE classification for goods and services" in match:
                continue
            if section_num not in section_data:
                section_data[section_num] = {"content": []}
            content_lines = [line for line in match.split('\n') if line.strip()]
            section_data[section_num]["content"].extend(content_lines)
            if "(210)" in match:
                section_num += 1

    pdf_document.close()


    data_extraction = "output.json"
    output_json_folder = r'D:\final_corsearch\output_json'          # output json folder path

    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)

    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")    
    # print(output_json_path,"42")

    image_folder = create_image_folder(pdf_file_path)
    coordinates_file = output_json_path

   
    output_data = json.dumps(section_data, indent=4, ensure_ascii=False)
    with open(data_extraction, "w", encoding="utf-8") as json_file:
        json_file.write(output_data)
        
    # locate_data_in_pdf(pdf_file_path)
    define_coordinates_from_pdf(pdf_file_path, data_extraction, output_json_path)
    extract_and_save_image(pdf_file_path, coordinates_file, image_folder, resolution)


def mongolia_pdf_extraction(pdf_file_path):
    
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
        'Монгол', 'Оюуны', 'Өмчийн', 'Газар',"үйлчилгээний", "тэмдэг.", 'Нэр ','УЛСЫН', 'БҮРТГЭЛД','БАРААНЫ','ТЭМДЭГ','АВСАН']

    doc = fitz.open(pdf_file_path)
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

    data_extraction = "output.json"
    output_json_folder = r'D:\final_corsearch\output_json'          # output json folder path

    if not os.path.exists(output_json_folder):
        os.makedirs(output_json_folder)

    pdf_filename = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_json_path = os.path.join(output_json_folder, f"{pdf_filename}.json")    
    # print(output_json_path,"42")

    image_folder = create_image_folder(pdf_file_path)
    coordinates_file = output_json_path

    with open('pdf.json', 'w', encoding='utf-8') as output_file:
      data_extraction = json.dump(output_data, output_file, ensure_ascii=False, indent=4)

    define_coordinates_from_pdf(pdf_file_path, data_extraction, output_json_path)
    extract_and_save_image(pdf_file_path, coordinates_file, image_folder, resolution)



























# import os
# import json
# import fitz  # PyMuPDF
# import re
# from image_processing import *

# def process_page(page):
#     """Extract text and page number from a page."""
#     page_text = page.get_text("text")
#     return page_text, page.number

# def correct_text_segmentation(content_data, delimiter):
#     """Correct text segmentation issues."""
#     corrected_data = []
#     for page_text in content_data:
#         split_texts = page_text['text'].split(delimiter)
#         corrected_data.append({'text_on_page': page_text['text_on_page'], 'text': split_texts[0]})
#         if len(split_texts) > 1:
#             corrected_data.append({'text_on_page': page_text['text_on_page'] + 1, 'text': split_texts[1]})
#     return corrected_data

# def merge_duplicate_pages(content_data):
#     """Merge texts from duplicate pages."""
#     consolidated_data = {}
#     for entry in content_data:
#         page_num = entry["text_on_page"]
#         text = entry["text"].strip()
#         if not text:
#             continue
#         consolidated_data[page_num] = consolidated_data.get(page_num, '') + " " + text
#     merged_data = [{"text_on_page": k, "text": v.strip()} for k, v in consolidated_data.items()]
#     merged_data.sort(key=lambda x: x["text_on_page"])
#     return merged_data

# def extract_data_from_pdf(pdf_file_path):
#     """Main function to extract data from PDF and save it as JSON."""
#     # Regular expression pattern for matching specific text sections
#     pattern = re.compile(r"\(210\)[\s\S]*?(?=\(210\)|$)")

#     # Open the PDF file
#     pdf_document = fitz.open(pdf_file_path)
#     text_pages = {}

#     # Process each page
#     for page in pdf_document:
#         text, pn = process_page(page)
#         text_pages[pn] = text

#     # Concatenate text from all pages
#     extracted_text = " ".join(text_pages.values())
#     matches = pattern.findall(extracted_text)

#     # Extract and structure section data
#     section_data = {}
#     section_num = 1

#     for match in matches:
#         if "(511) \u2013 NICE classification for goods and services" in match:
#             continue

#         section_data[section_num] = {'page_number': [], 'content': [], 'content_data': []}
#         start_index = extracted_text.find(match)
#         page_nums = []
#         current_pos = 0
#         for pn, txt in text_pages.items():
#             current_pos += len(txt)
#             if start_index < current_pos:
#                 page_nums.append(pn)
#                 if current_pos > start_index + len(match):
#                     break

#         section_data[section_num]['page_number'] = [pn + 1 for pn in page_nums]

#         content_lines = [line for line in match.split("\n") if line.strip()]
#         section_data[section_num]["content"].extend(content_lines)

#         segment_start = start_index
#         current_content_data = []

#         for pn in page_nums:
#             segment_end = min(segment_start + len(text_pages[pn]), start_index + len(match))
#             while extracted_text[segment_end] not in [" ", "\n", "\t"] and segment_end > segment_start:
#                 segment_end -= 1

#             segment = extracted_text[segment_start:segment_end]
#             if segment.strip():
#                 current_content_data.append({"text_on_page": pn + 1, "text": segment.strip()})
#             segment_start = segment_end

#         section_data[section_num]["content_data"].extend(current_content_data)

#         delimiter = 'Successfull Examination Marks'
#         section_data[section_num]["content_data"] = correct_text_segmentation(section_data[section_num]["content_data"], delimiter)
#         section_data[section_num]["content_data"] = merge_duplicate_pages(section_data[section_num]["content_data"])

#         for entry in section_data[section_num]["content_data"]:
#             text = entry["text"]
#             lines = [line for line in text.split('\n') if line.strip()]
#             entry["text"] = lines

#         section_num += 1

#     pdf_document.close()

#     output_json_path = f"{pdf_file_path.split('.')[0]}output_today.json"
#     with open(output_json_path, "w", encoding="utf-8") as json_file:
#         json.dump(section_data, json_file, ensure_ascii=False, indent=4)

#     return output_json_path

# # Example usage
# pdf_file_path = "BT20211006-98.pdf"
# result_json = extract_data_from_pdf(pdf_file_path)
# print(f"Data extracted and saved to {result_json}")