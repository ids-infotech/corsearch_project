import cv2
import os
import pytesseract
import base64

# Path to the folder containing images
folder_path = r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images\pdf_ss"
output_folder = r"D:\python_projects\Corsearch\new files\Saint Vincent and the Grenadines VC\2023\sv_images\pdf_ss\application_ss"  # Define the folder to save cropped images

# DPI of the images
input_dpi = 72

# Path to Tesseract executable (change this based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to split images based on horizontal black lines
def split_images_with_horizontal_lines(folder, output_folder):
    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):  # Adjust for other image formats if needed
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

            # Split the image based on horizontal lines
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

                    # SAVING THE IMAGE IN BASE64 FORMAT
                    # with open(cropped_img, "rb") as image_file:
                    #     base64_image = base64.b64encode(image_file.read()).decode('utf-8')

                    # # Update JSON data with base64 for both valid and invalid coordinates
                    # page_data['binaryContent'] = base64_image

                    # base64_filename = os.path.join(output_folder, f"{os.path.basename(pdf_file)}page{page_number}img{image_counter}{image_filename_suffix}_base64.json")
                    # with open(base64_filename, "w") as json_file:
                    #     json.dump({os.path.basename(cropped_img): base64_image}, json_file, indent=4)

# Call the function
split_images_with_horizontal_lines(folder_path, output_folder)