import cv2
import os
import pytesseract
import base64
import json
import fitz  # PyMuPDF library for working with PDFs

# Path to the folder containing images
folder_path = r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images\pdf_ss"
output_folder = r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images\pdf_ss\application_ss"  # Define the folder to save cropped images

# DPI of the images
input_dpi = 72

# Path to Tesseract executable (change this based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to extract coordinates from a PDF
def extract_coordinates_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    all_coords = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if b['type'] == 0:  # Type 0 indicates a text block
                x0, y0, x1, y1 = b['bbox']
                all_coords.append((x0, y0, x1, y1))

    return all_coords

# Function to get text from logo images if available
def extract_logo_text(logo_folder):
    logo_text = None

    for filename in os.listdir(logo_folder):
        if filename.endswith(".jpeg") or filename.endswith(".png"):
            logo_img_path = os.path.join(logo_folder, filename)
            logo_img = cv2.imread(logo_img_path)

            # Convert the logo image to grayscale
            gray_logo = cv2.cvtColor(logo_img, cv2.COLOR_BGR2GRAY)

            # Use pytesseract to extract text from the logo image
            extracted_text = pytesseract.image_to_string(gray_logo)
            if extracted_text:
                logo_text = extracted_text.strip()
                break

    return logo_text

def get_line_with_application_number(img):
    # Perform OCR on the image to extract text
    text = pytesseract.image_to_string(img)

    # Split the text into lines
    lines = text.split('\n')

    # Look for lines containing patterns that match an application number
    application_number_line = None
    for line in lines:
        # Implement a pattern matching or text search logic for application numbers
        if "Application Number" in line:  # Example pattern
            application_number_line = line
            break

    return application_number_line

# Function to split images based on horizontal lines
def split_images_with_horizontal_lines(folder, output_folder):
    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(folder, filename)
            img = cv2.imread(img_path)

            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply a Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Apply Canny edge detection to find edges
            edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

            # Find contours
            contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Collect potential line positions
            line_positions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h > 2 and w > 400 and abs(w - img.shape[1]) < 10:  # Adjust these values based on line size and image width
                    line_positions.append(y)

            line_positions.sort()

            # Extract coordinates from the PDF
            pdf_file_path = r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\VC\VC20221212-28.pdf"  # Replace with the path to your PDF
            logo_folder = r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images"
            coordinates = extract_coordinates_from_pdf(pdf_file_path)

            # Get text from logo images
            logo_text = extract_logo_text(logo_folder)

            if len(line_positions) >= 1:
                for i in range(len(line_positions) + 1):
                    if i == 0:
                        top = 0
                    else:
                        top = max(0, line_positions[i - 1] - 10)  # Adjust the top position

                    if i == len(line_positions):
                        bottom = img.shape[0]
                    else:
                        bottom = min(img.shape[0], line_positions[i] + 10)  # Adjust the bottom position

                    # Crop and save the image to the output folder
                    cropped_img = img[top:bottom, :]
                    output_path = os.path.join(output_folder, f"cropped_{filename.split('.')[0]}_{i}.png")
                    cv2.imwrite(output_path, cropped_img)
                    print(f"Image '{filename}' part {i} cropped and saved successfully.")

                    # Convert cropped image to base64
                    cropped_img_base64 = base64.b64encode(cv2.imencode('.png', cropped_img)[1]).decode()

                    application_number_line = get_line_with_application_number(img)

                    # Update JSON data with coordinates
                    json_data = {
                        'filename': filename,
                        'part': i,
                        'base64_content': cropped_img_base64,
                        'coordinates': coordinates[i] if i < len(coordinates) else None,  # Using coordinates from PDF
                        'logo_text': logo_text if logo_text else 'Null', # Logo text or 'Null' if not found
                        'application_number': application_number_line
                    }

                    # Save JSON file
                    json_filename = f"cropped_{filename.split('.')[0]}_{i}.json"
                    json_output_path = os.path.join(output_folder, json_filename)
                    with open(json_output_path, "w") as json_file:
                        json.dump(json_data, json_file, indent=4)

                    print(f"Image '{filename}' part {i} cropped, saved, and JSON updated successfully.")

# Call the function
split_images_with_horizontal_lines(folder_path, output_folder)
