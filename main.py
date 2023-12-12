import fitz
import pdfplumber
import re
import json
import os
from PIL import Image
import base64
import re
import json
import time
import cv2
import pytesseract
import argparse
import datetime
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import logging  
from pdf_extraction import *  

logging.basicConfig(
    handlers=[
        logging.FileHandler('preprocess_pdf_info.log'),
        logging.FileHandler('preprocess_pdf_error.log'),
    ],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set the level for each handler individually
logging.getLogger().handlers[0].setLevel(logging.INFO)  # info log
logging.getLogger().handlers[1].setLevel(logging.ERROR)  # error log


def is_valid_pdf(pdf_file_path):
    try:
        with fitz.open(pdf_file_path) as pdf_document:
            print("31------------")
            _ = len(pdf_document)
            print(_,"No. of pages")
        return True  # PDF is valid
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error in is_valid_pdf for file {pdf_file_path}: {e}")
        print("38-------")
        return False  # PDF is not valid
    


def handle_corrupted_pdf(pdf_file_path, error_message):
    with open("corrupted_pdf_logs.txt", "a") as log_file:
        logging.info(f"Corrupted PDF: {pdf_file_path}")
        logging.error(f"Error: {error_message}\n\n")
        
        log_file.write(f"Corrupted PDF: {pdf_file_path}\n")
        log_file.write(f"Error: {error_message}\n\n")


def handle_password_protected_pdf(pdf_file_path):
    try:
        pdf_document = fitz.open(pdf_file_path)
        if pdf_document.is_encrypted:
            password = input("Enter the password for the PDF: ")
            pdf_document.authenticate(password)
            return pdf_document
        else:
            return pdf_document
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error processing password encrypted PDF '{pdf_file_path}': {e}")
       
        return None
    
def get_pdf_size(pdf_file_path):
    pdf_size_bytes = os.path.getsize(pdf_file_path)
    pdf_size_mb = pdf_size_bytes / (1024 * 1024)
    formatted_pdf_size = "{:.4f}".format(pdf_size_mb)
    return formatted_pdf_size


# def convert_to_readable_date(date_string):
#     date_parts = date_string.split("+")

#     if len(date_parts) >= 1:
#         date_part = date_parts[0].replace("D:", "").strip()
#         year = date_part[:4]
#         month = date_part[4:6]
#         day = date_part[6:8]
#         time_part = date_part[-6:]
#         formatted_date = f"{year}-{month}-{day}"
#         formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
#         result = f"Year: {year}, Date: {formatted_date}, Time: {formatted_time}"
#         if len(date_parts) == 2:
#             time_zone_part = date_parts[1].strip()
#             result += f", Time Zone: {time_zone_part}"
#         return result
#     else:
#         return "Invalid Date String"


# def extract_country_info(input_str):
#     country_code = input_str[:2]
#     year_str = input_str[2:6]
#     month_str = input_str[6:8]
#     day_str = input_str[8:10]
#     number_str = input_str.split('-')[1].split('.')[0]

#     return {
#         "Country Code": country_code,
#         "Year": year_str,
#         "Month": month_str,
#         "Day": day_str,
#         "Batch": number_str
#     }


# def get_pdf_metadata_and_info(pdf_file_path):
    # pdf_document = fitz.open(pdf_file_path)
    # pdf_metadata = pdf_document.metadata
    # image_count = 0
    # page_count = len(pdf_document)

    # word_count = 0
    # char_count = 0

    # for page_number in range(page_count):
    #     page = pdf_document[page_number]
    #     image_list = page.get_images(full=True)
    #     image_count += len(image_list)
    #     page_text = page.get_text()
    #     words = page_text.split()
    #     word_count += len(words)
    #     char_count += len(page_text)

    # pdf_size = get_pdf_size(pdf_file_path)

    # if 'creationDate' in pdf_metadata:
    #     pdf_metadata['creationDate'] = convert_to_readable_date(
    #         pdf_metadata['creationDate'])
    # if 'modDate' in pdf_metadata:
    #     pdf_metadata['modDate'] = convert_to_readable_date(
    #         pdf_metadata['modDate'])

    # return pdf_metadata, image_count, pdf_size, page_count, word_count, char_count


def get_country_from_config(config_file):
    # Extract country name from the config file name
    # Assuming the config file name follows the pattern: COUNTRY_config.json
    # country = config_file.name.split('-')[0].upper()
    country = os.path.basename(config_file)[:2]
    # file_prefix = os.path.basename(pdf_file)[:2]
    return country

def calculate_eta(start_time, end_time):
    # Calculate the ETA based on the difference between start and end times
    # Adjust this calculation based on your specific requirements
    elapsed_time = end_time - start_time
    eta = start_time + (2 * elapsed_time)  # Assuming the task will take approximately the same time to complete
    return eta

def read_pdf_files(pdf_folder,config_file):
        
    pdf_files = [file for file in os.listdir(pdf_folder) if file.endswith(".pdf")]

    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(pdf_folder, pdf_file)
        logging.info(f"Processing PDF: {pdf_file_path}")
        start_time = datetime.datetime.now()

        file_size = get_pdf_size(pdf_file_path) 
        logging.info(f"Size of PDF : {pdf_file_path}, {file_size}")
        print(f"Processing PDF: {pdf_file_path}")
    
        # Check if the PDF is valid before processing
        if not is_valid_pdf(pdf_file_path):
            error_message = "Invalid or corrupted PDF format."
            print(f"Skipping {pdf_file} due to {error_message}")
            logging.error(f"Skipping {pdf_file} due to {error_message}")

            handle_corrupted_pdf(pdf_file_path, error_message)
            continue
            
        # Handle password-protected PDFs
        pdf_document = handle_password_protected_pdf(pdf_file_path)
        if pdf_document is None:
            print(f"Failed to open {pdf_file}. Please check the password.")
            logging.error(f"Failed to open {pdf_file}. Invalid password.")
            continue
        

        # Determine the country based on the config file name
        country = get_country_from_config(config_file)
        try:
            logging.info(f"Start time for PDF extraction: {start_time}")
            # Call the corresponding PDF extraction function based on the country
            country_extraction_functions = {
                'BT': bhutan_pdf_extraction,
                'MN': mongolia_pdf_extraction,
                'TN': tunisia_pdf_extraction,
                'DZ': algeria_pdf_extraction,
                # 'COUNTRY3': country3_pdf_extraction,
                # Add more countries as needed
            }
            if country in country_extraction_functions:
                print("193===========")
                country_extraction_functions[country](pdf_file_path)
            else:
                print(f"Country '{country}' is not supported for PDF extraction.")
        finally:
            end_time = datetime.datetime.now()
            elapsed_time = end_time - start_time
            eta = start_time + (2 * elapsed_time)
            logging.info(f"End time for PDF extraction: {end_time}")
            logging.info(f"Elapsed Time: {elapsed_time}, ETA: {eta}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PDF Metadata Extractor')
    parser.add_argument("--config", required=True, help='Path to the config file (e.g., config.json)')
    parser.add_argument("--pdf-folder", required=True, help='Path to the folder containing PDF files')

    args = parser.parse_args()

    read_pdf_files(args.pdf_folder, args.config)
    





