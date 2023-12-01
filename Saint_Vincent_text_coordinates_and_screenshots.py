import json
import pdfplumber
from PIL import Image

def capture_screenshots(json_file_path, pdf_file_path, output_folder):
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    with pdfplumber.open(pdf_file_path) as pdf:
        for page_num, trademark_info in enumerate(json_data['trademark']):
            page = pdf.pages[page_num]
            block_coords = None

            for line in trademark_info:
                for box in page.extract_text_lines():
                    text = box['text']
                    if line in text:
                        x0, y0, x1, y1 = box['x0'], box['top'], box['x1'], box['bottom']

                        if block_coords:
                            block_coords = block_coords + [(x0, y0), (x1, y1)]
                        else:
                            block_coords = [(x0, y0), (x1, y1)]

            if block_coords:
                x0, y0 = min(coord[0] for coord in block_coords), min(coord[1] for coord in block_coords)
                x1, y1 = max(coord[0] for coord in block_coords), max(coord[1] for coord in block_coords)

                img = page.to_image(resolution=72)
                img_path = f"{output_folder}/page_{page_num + 1}_screenshot.png"
                img.save(img_path)

                img_pil = Image.open(img_path)
                img_crop = img_pil.crop((x0, y0, x1, y1))
                img_crop.save(img_path)


# Replace 'trademark_data.json' with the actual path to your JSON file
json_file_path = r'D:\python_projects\Corsearch\new files\cleaned_output_without_empty.json'
# Replace 'your_pdf_file.pdf' with the actual path to your PDF file
pdf_file_path = r'D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\VC\VC20221212-28.pdf'
# Replace 'output_folder' with the desired folder to save the screenshots
output_folder = r'D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images\pdf_ss'

capture_screenshots(json_file_path, pdf_file_path, output_folder)
