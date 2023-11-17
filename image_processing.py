import pdfplumber
import json
import fitz  # PyMuPDF
import os
from PIL import Image
import base64
import re

def process_pdf(pdf_file):
    # Check the prefix of the PDF file
    file_prefix = os.path.basename(pdf_file)[:2]

    # Call the corresponding functions based on the prefix
    if file_prefix == 'BT':
        process_bhutan_pdf(pdf_file)
    elif file_prefix == 'MN':
        process_mongolia_pdf(pdf_file)
    else:
        print(f"Unsupported file prefix: {file_prefix}")



''' EXTRACTING COORDINATES OF TEXT FROM THE PDF '''
# Define the amount to increase 'y1' by when the condition is met
# y1_increase = 20  # Replace with the actual amount you want to increase by

def define_coordinates_from_pdf_for_application_screenshots_bhutan(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
    
    # Load the JSON file containing the previously extracted text (if it exists)
    try:
        with open(extracted_text_json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        # Handle the case where the file is not found
        print("[-] Existing file not found")
        return
    except Exception as e:
        # Handle other exceptions (e.g., file read errors) and print the error message
        print(e)
        return

    # Extract text from the PDF and store it in extracted_text_dict
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize variables to store the minimum and maximum coordinates
        min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

        # Iterate through each page in the PDF
        for page_number, page in enumerate(pdf.pages, start=1):
            # Initialize a dictionary to store extracted text for the current page
            extracted_text_dict[str(page_number)] = {
                "page_number": page_number,
                "extracted_texts": []
            }
            print("[*] page number:", page_number)
            print("----------------------")
            
            '''GET PAGE HEIGHT'''
            # Get the height of the page
            page_height = page.height

            # Retrieve the current page (0-based index)
            page = pdf.pages[page_number - 1]  # Pages are 0-based index

            # Extract words from the page with their bounding box coordinates
            words_with_bounding_box = page.extract_words()

            # Initialize a dictionary to group words into lines based on y-coordinates
            lines = {}
            for word in words_with_bounding_box:
                # Round y-coordinate to handle floating-point inaccuracies
                y0 = round(word["top"], 2)
                y1 = round(word["bottom"], 2)
                if (y0, y1) in lines:
                    # Append word data to an existing line
                    lines[(y0, y1)]["text"].append(word["text"])
                    lines[(y0, y1)]["x0"].append(word["x0"])
                    lines[(y0, y1)]["x1"].append(word["x1"])
                else:
                    # Create a new line entry
                    lines[(y0, y1)] = {
                        "text": [word["text"]],
                        "x0": [word["x0"]],
                        "x1": [word["x1"]],
                    }

            # Sort lines by y-coordinates
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])

            # Iterate through existing data entries
            for page_data_key, page_data in existing_data.items():
                # Skip this entry if it has no 'content_data'
                if not page_data.get("content_data"):
                    continue

                # Iterate through content entries for the current page
                for content_entry in page_data["content_data"]:
                    # Get the start and end patterns
                    start = content_entry["text"][0]
                    end = content_entry["text"][-1]

                    # Initialize a flag to track if a match is found
                    match = False

                    # Initialize variables to calculate the minimum and maximum coordinates
                    min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

                    # Iterate through sorted lines
                    for (y0, y1), line_info in sorted_lines:
                        text = " ".join(line_info["text"])

                        if match:
                            # to get the maximum coordinates of the text
                            # determine the smallest x0 and y0 coordinates (the top-left corner) and 
                            # largest x1 and y1 coordinates (the bottom-right corner) for a text block
                            # These are then used to calculate the overall coordinates for the entire text extracted between the "start" and "end" patterns.
                            min_x0 = min(min_x0, min(line_info["x0"]))
                            min_y0 = min(min_y0, y0)
                            max_x1 = max(max_x1, max(line_info["x1"]))
                            max_y1 = max(max_y1, y1)

                         # Compare text to the start pattern
                        start_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in start.split(" ") if i]

                        # Mark a match when the start pattern is found
                        if start_found and not match:
                            match = True
  
                        '''MANUALLY INCREASING THE y1 COORDINATE'''
#                         # Check if the last line starts with "(540):" and increase 'y1' if it does
#                         if match and content_entry["text"][-1].startswith("(540):"):
#                             max_y1 += y1_increase
                                            
                            
                        # Compare text to the end pattern
                        end_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in end.split(" ") if i]

                        if end_found and match:
                            
                            '''USING PAGE HEIGHT TO GET THE y1 COORDINATE'''
                            if content_entry["text"][-1].startswith("(540):"):
                                # Define y1_increase based on the bottom of the page
                                y1_increase = page_height - y1
                                max_y1 += y1_increase
                            
                            # Add the extracted text and its coordinates to the dictionary
                            extracted_text_dict[str(page_number)]["extracted_texts"].append({
                                "extracted_text": content_entry['text'],
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1,
                            })
                            # Print a message indicating that the text has been successfully extracted
                            match = False
                            print("[+] extracted the text => ",
                                  '\n'.join(content_entry['text']), "\n")

                            # Update the content_data entry with coordinates
                            content_entry["coordinates"] = {
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1
                            }
                            break

    # Save the modified JSON file with coordinates added
    with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, separators=(',', ': '))

    # Save the defined coordinates to a new JSON file with formatting
    with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
        json.dump(extracted_text_dict, output_json_file, indent=4, separators=(',', ': '))


skipped_rectangles = {}

# The coordinates are in the format (x0, y0, x1, y1) - top left and bottom right corners.
# x0 is the horizontal coordinate (from the left) of the top-left corner. [LEFT VERTICLE LINE goes LEFT(lower number) or RIGHT (higher number)]
# y0 is the vertical coordinate (from the top) of the top-left corner. [TOP HORIZONTAL LINE goes UP (lower number) and DOWN(higher number) ]
# x1 is the horizontal coordinate (from the left) of the bottom-right corner. [RIGHT VERTICLE LINE goes LEFT (lower number) or RIGHT (higher number)]
# y1 is the vertical coordinate (from the top) of the bottom-right corner. [BOTTOM HORIZONTAL LINE goes UP(lower number) or DOWN(higher number)]

''' TAKING SCREENSHOTS BASED ON THE COORDINATES '''
def extract_and_save_image_for_application_screenshots_bhutan(pdf_file, coordinates_file, output_folder, resolution=200):
    padding = 14.5
    try:
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Open the PDF file
        pdf_document = fitz.open(pdf_file)
        
        # Load coordinates from the JSON file
        with open(coordinates_file, "r") as json_file:
            coordinates_data = json.load(json_file)
        
        # Initialize a list to store extracted image data for each page
        extracted_images_per_page = {}
        for key, entry in coordinates_data.items():
            page_number = entry["page_number"]

            page = pdf_document[page_number - 1]
            page_width = page.rect.width  # Get the page width
            
            for i, text in enumerate(entry["extracted_texts"]):
                x0 = text["x0"] - padding
                y0 = text["y0"] - padding
                x1 = page_width - 40  # USING PAGE WIDTH TO AVOID ERROR OF MISSING DATA 
                y1 = text["y1"] + padding
                page = pdf_document[page_number - 1] 
                rect = fitz.Rect(x0, y0, x1, y1)
#               print(rect)
                image = page.get_pixmap(
                    matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect)
                
                # Example check before processing each rectangle
                if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:
                    # MANUAL COORDINATES FOR THE FIRST LINES (67, 60 , page_width -40, 90)
                    rect = fitz.Rect(67, 60 , page_width -40 , 90)

                    # SAVING IMAGE FOR THE ONE LINE SCREENSHOTS
                    image = page.get_pixmap(matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect)
                    image_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}_invalid.png")
                    image.save(image_filename)
                    print(f"Extracted image saved as {image_filename}")
                    
                    # If needed, convert the screenshot to GIF format
                    gif_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}_invalid.gif")
                    image_pil = Image.open(image_filename)
                    image_pil.save(gif_filename, "GIF")
                    print(f"Converted PNG to GIF: {gif_filename}")
                    
                    # Encode the image as a base64 string
                    with open(image_filename, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                    # Get just the filename without the path
                    base_filename = os.path.basename(image_filename)
                
                    # Create a dictionary with the base filename as the key and base64 data as the value
                    image_data = {
                        base_filename: base64_image
                    }
                
                    # Save the base64 data in a JSON file
                    base64_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}_invalid.json")
                    with open(base64_filename, "w") as json_file:
                        json.dump(image_data, json_file, indent=4)
                
                    # Append the base64 data to the original coordinates_data
                    text["base64"] = base64_image

                    print(f"Skipping invalid rectangle coordinates: {x0}, {y0}, {x1}, {y1}")
                    print(f"Using predefined coordinates for skipped rectangle on page {page_number}")
                    
                    # Increment the skipped rectangle count for this page
                    if page_number not in skipped_rectangles:
                        skipped_rectangles[page_number] = 0
                    skipped_rectangles[page_number] += 1
                    
                    continue

                # SAVE THE EXTRACTED IMAGE
                image_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.png")
                image.save(image_filename)
                print(f"Extracted image saved as {image_filename}")

                # Now, convert the PNG image to GIF format using Pillow
                gif_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.gif")
                image_pil = Image.open(image_filename)
                image_pil.save(gif_filename, "GIF")
        
                print(f"Converted PNG to GIF: {gif_filename}")
        
                # Encode the image as a base64 string
                with open(image_filename, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
                # Get just the filename without the path
                base_filename = os.path.basename(image_filename)
        
                # Create a dictionary with the base filename as the key and base64 data as the value
                image_data = {
                    base_filename: base64_image
                }
                
                # Save the base64 data in a JSON file
                base64_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.json")
                with open(base64_filename, "w") as json_file:
                    json.dump(image_data, json_file, indent=4)

                # Append the base64 data to the original coordinates_data
                text["base64"] = base64_image
            
        # Save the updated coordinates_data back to the coordinates file
        with open(coordinates_file, "w") as json_file:
            json.dump(coordinates_data, json_file, indent=4)
        
        # Now, outside of the for-loop, after all processing is done, we report the skipped rectangles
        for page, count in skipped_rectangles.items():
            print(f"SKIPPED {count} RECTANGLES ON PAGE {page} of {pdf_file_path}")
        
        # WRITE THE MISSED RECTANGLES IN A .TXT FILE
        with open(f'skipped_rectangles_in_{pdf_file_path}.txt', 'w') as f:
            for page, count in skipped_rectangles.items():
                f.write(f"Page {page}: Skipped {count} \n")

            
    except Exception as e:
        print(e)
        print(f"Error: {str(e)}")



'''
FOR MONGOLIA
IGNORES HEADINGS BEING CAPTURED BUT IMAGES AFTER THE NEW HEADINGS ARE BAD,
WITHOUT THIS WE ARE GETTING IMAGES BUT ALSO GETTING MORE IMAGES
'''

ignore_text = "УЛСЫН БҮРТГЭЛД АВСАН БАРААНЫ ТЭМДЭГ" # FOR MONGOLIA

# EXTRACTING COORDINATES OF TEXT FROM THE PDF
def define_coordinates_from_pdf_for_application_screenshots_mongolia(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
    # Load the JSON file containing the previously extracted text (if it exists)
    try:
        with open(extracted_text_json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
      
    except FileNotFoundError:
        # Handle the case where the file is not found
        print("[-] Existing file not found")
        return
    except Exception as e:
        # Handle other exceptions (e.g., file read errors) and print the error message
        print(e)
        return

    # Extract text from the PDF and store it in extracted_text_dict
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize variables to store the minimum and maximum coordinates
        min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

        # Iterate through each page in the PDF
        for page_number, page in enumerate(pdf.pages, start=1):
            # Initialize a dictionary to store extracted text for the current page
            extracted_text_dict[str(page_number)] = {
                "page_number": page_number,
                "extracted_texts": []
            }
            print("[*] page number:", page_number)
            print("----------------------")

            # Retrieve the current page (0-based index)
            page = pdf.pages[page_number - 1]  # Pages are 0-based index

            # Extract words from the page with their bounding box coordinates
            words_with_bounding_box = page.extract_words()

            # Initialize a dictionary to group words into lines based on y-coordinates
            lines = {}
            for word in words_with_bounding_box:
                # Round y-coordinate to handle floating-point inaccuracies
                y0 = round(word["top"], 2)
                y1 = round(word["bottom"], 2)
                if (y0, y1) in lines:
                    # Append word data to an existing line
                    lines[(y0, y1)]["text"].append(word["text"])
                    lines[(y0, y1)]["x0"].append(word["x0"])
                    lines[(y0, y1)]["x1"].append(word["x1"])
                else:
                    # Create a new line entry
                    lines[(y0, y1)] = {
                        "text": [word["text"]],
                        "x0": [word["x0"]],
                        "x1": [word["x1"]],
                    }

            # Sort lines by y-coordinates
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])

            # Iterate through existing data entries
            for page_data_key, page_data in existing_data.items():
                # Skip this entry if it has no 'content_data'
                if not page_data.get("content_data"):
                    continue

                # Iterate through content entries for the current page
                for content_entry in page_data["content_data"]:
                    
                    # Skip processing if the extracted text matches the ignored text
                    if '\n'.join(content_entry['text']) == ignore_text:
                        continue
                        
                    # Get the start and end patterns
                    start = content_entry["text"][0]
                    end = content_entry["text"][-1]

                    # Initialize a flag to track if a match is found
                    match = False

                    # Initialize variables to calculate the minimum and maximum coordinates
                    min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

                    # Iterate through sorted lines
                    for (y0, y1), line_info in sorted_lines:
                        text = " ".join(line_info["text"])

                        if match:
                            # to get the maximum coordinates of the text
                            # determine the smallest x0 and y0 coordinates (the top-left corner) and 
                            # largest x1 and y1 coordinates (the bottom-right corner) for a text block
                            # These are then used to calculate the overall coordinates for the entire text extracted between the "start" and "end" patterns.
                            min_x0 = min(min_x0, min(line_info["x0"]))
                            min_y0 = min(min_y0, y0)
                            max_x1 = max(max_x1, max(line_info["x1"]))
                            max_y1 = max(max_y1, y1)

                         # Compare text to the start pattern
                        start_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in start.split(" ") if i]

                        # Mark a match when the start pattern is found
                        if start_found and not match:
                            match = True

                        # Compare text to the end pattern
                        end_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in end.split(" ") if i]

                        if end_found and match:
                            # Add the extracted text and its coordinates to the dictionary
                            extracted_text_dict[str(page_number)]["extracted_texts"].append({
                                "extracted_text": content_entry['text'],
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1,
                            })
                            # Print a message indicating that the text has been successfully extracted
                            match = False
                            print("[+] extracted the text => ",
                                  '\n'.join(content_entry['text']), "\n")

                            # Update the content_data entry with coordinates
                            content_entry["coordinates"] = {
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1
                            }
                            break

    # Save the modified JSON file with coordinates added
    with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4, separators=(',', ': '))

    # Save the defined coordinates to a new JSON file with formatting
    with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
        json.dump(extracted_text_dict, output_json_file, ensure_ascii=False, indent=4, separators=(',', ': '))


def extract_and_save_image_for_application_screenshots_mongolia(pdf_file, coordinates_file, output_folder, resolution=200):
    padding = 14.5
    
    # Initialize a set to keep track of pages that have been processed
    processed_pages = set()
    
    # try:
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF file
    pdf_document = fitz.open(pdf_file)

    # Load coordinates from the JSON file
    with open(coordinates_file, "r", encoding='utf-8') as json_file:
        coordinates_data = json.load(json_file)

    # Initialize a list to store extracted image data for each page
    extracted_images_per_page = {}
    for key, entry in coordinates_data.items():
        
        page_number = entry["page_number"]
        
        # Check if the page has already been processed
        if page_number in processed_pages:
            continue  # Skip this page as it's already processed

        page = pdf_document[page_number - 1]
        page_width = page.rect.width  # Get the page width

        for i, text in enumerate(entry["extracted_texts"]):
            
            x0 = text["x0"] - padding
            y0 = text["y0"] - 30
            x1 = page_width - 40  # USING PAGE WIDTH TO AVOID ERROR OF MISSING DATA 
            y1 = text["y1"] + padding
            
            # Add debugging prints
            print(f"Section {i} - x0: {x0}, y0: {y0}, x1: {x1}, y1: {y1}")
            
            page = pdf_document[page_number - 1] 
            rect = fitz.Rect(x0, y0, x1, y1)
#               print(rect)
            image = page.get_pixmap(
                matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect)

            # Example check before processing each rectangle
            if x0 < 0 or y0 < 0 or x1 <= x0 or y1 <= y0:                    
                continue

            # SAVE THE EXTRACTED IMAGE
            image_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.png")
            image.save(image_filename)
            print(f"Extracted image saved as {image_filename}")

            # Now, convert the PNG image to GIF format using Pillow
            gif_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.gif")
            image_pil = Image.open(image_filename)
            image_pil.save(gif_filename, "GIF")

            print(f"Converted PNG to GIF: {gif_filename}")

            # Encode the image as a base64 string
            with open(image_filename, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Get just the filename without the path
            base_filename = os.path.basename(image_filename)

            # Create a dictionary with the base filename as the key and base64 data as the value
            image_data = {
                base_filename: base64_image
            }

            # Save the base64 data in a JSON file
            base64_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.json")
            with open(base64_filename, "w") as json_file:
                json.dump(image_data, json_file, indent=4)

            # Append the base64 data to the original coordinates_data
            text["base64"] = base64_image
            
            # After successfully saving an image for a section, mark the page as processed
            processed_pages.add(page_number)
            break  # Break the loop after processing the first section of the page

    # Save the updated coordinates_data back to the coordinates file
    with open(coordinates_file, "w", encoding='utf-8') as json_file:
        json.dump(coordinates_data, json_file, indent=4, ensure_ascii=False)

    # Now, outside of the for-loop, after all processing is done, we report the skipped rectangles
    for page, count in skipped_rectangles.items():
        print(f"SKIPPED {count} RECTANGLES ON PAGE {page} of {pdf_file_path}")

    # WRITE THE MISSED RECTANGLES IN A .TXT FILE
    with open(f'skipped_rectangles_in_{pdf_file_path}.txt', 'w') as f:
        for page, count in skipped_rectangles.items():
            f.write(f"Page {page}: Skipped {count} \n")

            
    # except Exception as e:
    #     print(e)
    #     print(f"Error: {str(e)}")


def process_bhutan_pdf(pdf_file):
    # Bhutan-specific processing
    pdf_path = pdf_file
    extracted_text_json_path = f"{pdf_file}_result_of_segmented_text.json"
    output_json_path = f"{pdf_file}_defined_coordinates.json"

    define_coordinates_from_pdf_for_application_screenshots_bhutan(pdf_path, extracted_text_json_path, output_json_path)

    coordinates_file = output_json_path
    output_folder = f"OUTPUT_SCREENSHOTS_OF_APPLICATIONS_FOR_{pdf_file}"
    resolution = 200
    extract_and_save_image_for_application_screenshots_bhutan(pdf_file, coordinates_file, output_folder, resolution)

def process_mongolia_pdf(pdf_file):
    # Mongolia-specific processing
    pdf_path = pdf_file
    extracted_text_json_path = f"{pdf_file}_result_of_segmented_text.json"
    output_json_path = f"{pdf_file}_defined_coordinates.json"

    define_coordinates_from_pdf_for_application_screenshots_mongolia(pdf_path, extracted_text_json_path, output_json_path)

    coordinates_file = output_json_path
    output_folder = f"OUTPUT_SCREENSHOTS_OF_APPLICATIONS_FOR_{pdf_file}"
    resolution = 200
    extract_and_save_image_for_application_screenshots_mongolia(pdf_file, coordinates_file, output_folder, resolution)

if __name__ == "__main__":
    pdf_file_path = "BT20211006-98.pdf"  # Replace with the path to your PDF file

    # Call the main processing function based on the PDF file prefix
    process_pdf(pdf_file_path)
