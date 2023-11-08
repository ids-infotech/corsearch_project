import fitz  # PyMuPDF
import json
import os
from PIL import Image
import base64

def extract_and_save_image(pdf_file, coordinates_file, output_folder, resolution=200):
    # PADDING ADDED TO ADD MORE SPACE TO THE TEXT OF THE APPLICATIONS FOR BETTER VIEWING
    padding = 14.5

    try:
        # Ensure the output folder exists
        # If not then create a new folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Open the PDF file
        pdf_document = fitz.open(pdf_file)
        
        # Load coordinates from the JSON file
        # Defined_coordinates.json
        with open(coordinates_file, "r") as json_file:
            coordinates_data = json.load(json_file)
        
        # Initialize a list to store extracted image data for each page
        extracted_images_per_page = {}
        for key, entry in coordinates_data.items():
            page_number = entry["page_number"]
            for i, text in enumerate(entry["extracted_texts"]):
                x0 = text["x0"] - padding
                y0 = text["y0"] - padding
                x1 = text["x1"] + padding
                y1 = text["y1"] + padding
                page = pdf_document[page_number - 1]
                rect = fitz.Rect(x0, y0, x1, y1)
                image = page.get_pixmap(
                    matrix=fitz.Matrix(resolution / 72.0, resolution / 72.0), clip=rect
                )
                
                # SAVE THE EXTRACTED IMAGE IN A VARIABLE
                # SAVING IT IN A .PNG FORMAT
                # THE NAME OF THE IMAGE SAVED IS PDF_FILE_NAME + PAGE_NUMBER + SECTION_ON_PAGE
                # IT STARTS COUNTING FROM 0, THE FIRST SECTION ON A PAGE WOULD BE 0
                image_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.png")
                image.save(image_filename)
                # PRINT STATEMENT TO CHECK THE IMAGE SAVED
                print(f"Extracted image saved as {image_filename}")

                # Now, convert the PNG image to GIF format using Pillow library
                # USING THE image_filename variable to save it in a GIF format
                gif_filename = os.path.join(output_folder, f"{pdf_file}_page_{page_number}_section_{i}.gif")
                image_pil = Image.open(image_filename)
                # SAVING THE IMAGE IN GIF FORMAT
                image_pil.save(gif_filename, "GIF")

                # PRINT STATEMENT TO CHECK THE IMAGE SAVED
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
            
    except Exception as e:
        print(e)
        print(f"Error: {str(e)}")
        
if __name__ == "__main__":
    # PATH TO THE PDF
    pdf_file = "BT20230612-108.pdf" 
    # THIS IS THE INPUT JSON FILE WITH COORDINATES OF TEXTS
    # THE SAME FILE IS UPDATED WITH THE BASE64 OF THE IMAGES TAKEN
    coordinates_file = "defined_coordinates_of_BT20230612-108.pdf_applications.json"
    # THE OUTPUT FOLDER THAT STORES THE PICTURE OF APPLICATIONS
    # PICTURES ARE SAVED IN GIF, PNG AND BASE64 FORMAT 
    output_folder = f"OUTPUT_SCREENSHOTS_OF_APPLICATIONS_in_{pdf_file}"
    # RESOLUTION OF THE IMAGE TAKEN
    # HIGHER RESOLUTION WILL INCREASE THE IMAGE FILE SIZE
    resolution = 200
    extract_and_save_image(pdf_file, coordinates_file, output_folder, resolution)
