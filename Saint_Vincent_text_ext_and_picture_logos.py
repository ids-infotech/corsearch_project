import fitz  # PyMuPDF
import os
import json
import pdfplumber
from PIL import Image
import cv2
import numpy as np
from PIL import Image, ImageDraw


def extract_text_exclude_header_footer(pdf_file_path):
    text_per_page = []
    pdf_document = fitz.open(pdf_file_path)
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text_area = page.rect  # Entire page area
        text = ""
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            bbox = fitz.Rect(b["bbox"])
            if bbox.y0 > text_area.y1 * 0.9 or bbox.y1 < text_area.y0 * 1.1:
                continue  # Exclude text outside the 10% top and bottom of the page
            if "lines" in b:
                for l in b["lines"]:
                    text += " ".join([s["text"] for s in l["spans"]]) + "\n"
            elif "text" in b:
                text += b["text"] + "\n"  # If 'lines' key not present but 'text' is, add the entire block text
        lines = text.split('\n')  # Split text into lines based on '\n'
        cleaned_lines = [line.strip() for line in lines if line.strip()]  # Remove empty lines and strip leading/trailing spaces
        text_per_page.append(cleaned_lines)
    return text_per_page

def extract_images_by_index(pdf_file_path, output_folder):
    pdf_document = fitz.open(pdf_file_path)
    images_per_page = []
    for page_num in range(pdf_document.page_count):
        page_images = []
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            img_data = img[0]
            image = pdf_document.extract_image(img_data)
            image_bytes = image["image"]
            image_extension = image["ext"]
            image_path = os.path.join(output_folder, f"image_page_{page_num}_index_{img_index}.{image_extension}")
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            page_images.append({'image_index': img_index, 'image_path': image_path})
        images_per_page.append({'page': page_num, 'images': page_images})
    return images_per_page

def generate_json(text, images):
    data = {'trademark': text}
    with open('output.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

def remove_string_from_json(input_json_path, output_json_path, string_to_remove):
    with open(input_json_path, 'r') as json_file:
        data = json.load(json_file)
    
    def remove_string_recursive(obj):
        if isinstance(obj, list):
            return [remove_string_recursive(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: remove_string_recursive(value) for key, value in obj.items()}
        elif isinstance(obj, str):
            return obj.replace(string_to_remove, '')

    cleaned_data = remove_string_recursive(data)
    
    with open(output_json_path, 'w') as output_file:
        json.dump(cleaned_data, output_file, indent=4)

def remove_empty_strings(input_json_path, output_json_path):
    with open(input_json_path, 'r') as json_file:
        data = json.load(json_file)

    def remove_empty_strings_recursive(obj):
        if isinstance(obj, list):
            return [remove_empty_strings_recursive(item) for item in obj if item or isinstance(item, bool)]
        elif isinstance(obj, dict):
            return {key: remove_empty_strings_recursive(value) for key, value in obj.items() if value or isinstance(value, bool)}
        elif isinstance(obj, str):
            return obj.strip()

    cleaned_data = remove_empty_strings_recursive(data)
    
    with open(output_json_path, 'w') as output_file:
        json.dump(cleaned_data, output_file, indent=4)


def extract_text_blocks_and_screenshots(pdf_file_path, output_folder):
    text_blocks_per_page = []

    with pdfplumber.open(pdf_file_path) as pdf:
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            words = page.extract_words()
            page_image = page.to_image(resolution=300)
            img = page_image.original
            
            for block_index, word in enumerate(words):
                bbox = (word['x0'], word['top'], word['x1'], word['bottom'])
                # Exclude text outside the 10% top and bottom of the page
                page_height = img.height
                if bbox[1] > page_height * 0.9 or bbox[3] < page_height * 0.1:
                    continue
                
                # Extract block coordinates
                block_coordinates = {
                    'x0': bbox[0],
                    'y0': bbox[1],
                    'x1': bbox[2],
                    'y1': bbox[3],
                    'text': word['text']
                }
                
                # Draw bounding box on the image
                draw = ImageDraw.Draw(img)
                draw.rectangle([(bbox[0], bbox[1]), (bbox[2], bbox[3])], outline="red")
                
            page_image.save(f"{output_folder}/page_{page_num}_with_blocks.png")
            text_blocks_per_page.append({'page': page_num, 'image_path': f"{output_folder}/page_{page_num}_with_blocks.png"})

    return text_blocks_per_page

# Example usage
pdf_file_path = r'D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\VC\VC20221212-28.pdf'
output_images_folder = r'D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images'
cleaned_json_path = r'D:\python_projects\Corsearch\new files\cleaned_output_without_empty.json'
final_output_path = r'D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images\final_output_sv.json'
output_folder = r'D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images\pdf_ss'

# Ensure the output folder exists
os.makedirs(output_images_folder, exist_ok=True)

# Extract text from PDF per page, excluding header/footer
extracted_text_per_page = extract_text_exclude_header_footer(pdf_file_path)

# Extract images by index and save to folder, organized per page
extracted_images_per_page = extract_images_by_index(pdf_file_path, output_images_folder)

# Generate JSON with text, text coordinates, and images organized per page
generate_json(extracted_text_per_page, extracted_images_per_page)

# Remove a specific string from the generated JSON
string_to_remove = 'COMMERCE AND INTELLECTUAL PROPERTY OFFICE'
remove_string_from_json('output.json', 'cleaned_output_sv.json', string_to_remove)

# Remove empty strings from the JSON
remove_empty_strings('cleaned_output_sv.json', 'cleaned_output_without_empty.json')

# Get text coordinates from cleaned JSON and PDF
text_blocks_per_page = extract_text_blocks_and_screenshots(pdf_file_path, output_folder)

for page_info in text_blocks_per_page:
    print(f"Page {page_info['page']} image with text blocks saved to: {page_info['image_path']}\n")

