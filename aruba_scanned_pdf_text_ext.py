import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
import json

def extract_text_from_pdf_with_images(pdf_file):
    text_per_page = []

    # Open the PDF file using PyMuPDF
    pdf_document = fitz.open(pdf_file)

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)

        # Convert the page to a Pixmap
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        # Save the Pixmap as a PNG image
        image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

        # Perform OCR on the image and extract text, splitting by newlines
        ocr_text = pytesseract.image_to_string(image).split('\n')
        text_per_page.append({"page_number": page_num + 1, "text": ocr_text})

    return text_per_page

def save_text_to_json(text_per_page, output_json_file):
    with open(output_json_file, 'w', encoding='utf-8') as json_file:
        json.dump(text_per_page, json_file, ensure_ascii=False, indent=4)

def process_pdfs_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_file = os.path.join(root, file)
                output_json_file = os.path.splitext(pdf_file)[0] + "_output_1.json"
                text_per_page = extract_text_from_pdf_with_images(pdf_file)
                save_text_to_json(text_per_page, output_json_file)
                print(f"Processed: {pdf_file}")

if __name__ == '__main__':
    folder_path = r'D:\python_projects\Corsearch\new files\Aruba AW'  # Replace with the folder containing PDFs
    process_pdfs_in_folder(folder_path)
