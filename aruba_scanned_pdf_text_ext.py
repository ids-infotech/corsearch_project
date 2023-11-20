import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import json
import os

def extract_text_from_pdf_with_images(pdf_file):
    text_per_page = {}

    # Open the PDF file using PyMuPDF
    pdf_document = fitz.open(pdf_file)

    # Extract text starting from page 4
    for page_num in range(3, pdf_document.page_count):
        page = pdf_document.load_page(page_num)

        # Convert the page to a Pixmap
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        # Save the Pixmap as a PNG image
        image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

        # Perform OCR on the image and extract text
        ocr_text = pytesseract.image_to_string(image)

        # Remove empty lines and exclude headers and footers (customize as per your PDF layout)
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
        filtered_lines = [line for line in lines if not (line.startswith("Header") or line.endswith("Footer"))]

        text_per_page[f"trademark{page_num + 1}"] = filtered_lines

    return text_per_page

def save_text_to_json(text_per_page, output_json_file):
    with open(output_json_file, 'w', encoding='utf-8') as json_file:
        json.dump(text_per_page, json_file, ensure_ascii=False, indent=4)

def process_pdfs_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_file = os.path.join(root, file)
                output_json_file = os.path.splitext(pdf_file)[0] + "_output.json"
                text_per_page = extract_text_from_pdf_with_images(pdf_file)
                save_text_to_json(text_per_page, output_json_file)
                print(f"Processed: {pdf_file}")

if __name__ == '__main__':
    folder_path = r'D:\python_projects\Corsearch\new files\Aruba AW'  # Replace with the folder containing PDFs
    process_pdfs_in_folder(folder_path)
