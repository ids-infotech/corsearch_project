# corsearch_project
Corsearch - script development creating for config &amp; pdf-extraction

# ADDED SCRIPT TO EXTRACT APPLICATIONS AND THEIR SCREENSHOTS FOR MONGOLIA
It needs some more tuning, handles most of the errors

# AN UPDATED VERSION OF THE MERGED SCRIPT WAS ADDED WITH ERROR HANDLING
1. It is a .ipynb file (jupyter notebook),
2. It skips the invalid rectangles,
3. It also creates a new .txt file that has information about the missed rectangles.

# A MERGED SCRIPT WAS UPLOADED on 6/11/2023,
1. Variable names need to be edited, - DONE
2. The variable names need to be dynamic, - DONE
3. How can we have one output JSON instead of creating one and then using it in the next function? - NO CHANGES
4. Pass the information as variables instead of creating and passing JSON files? - NO CHANGES
5. What would be the best approach to do this?
-------------------------------------------------------------------------------




PLEASE CHANGE THE NAME OF PDF_PATH IF YOU TRY TO RUN THESE ON A DIFFERENT PDF FILE. 
RIGHT NOW IT WORKS FOR BHUTAN. 
A PDF IS ADDED (BT20230612-108.pdf) TO TRY IT ON, BUT IT SHOULD WORK ON ALL BHUTAN PDFs AS THEY ARE SIMILAR


# FOR IMAGE EXTRACTION OF APPLICATIONS.
# SCRIPT_1 (read_pdf_and_get_text_of_applications.py) 
1. This Script takes a PDF file as input and creates a JSON file of the applications.
2. The Output JSON file is based on the PDF file name,
3. This Output JSON is later used to get coordinates of the text of applications.

-------------------------------------------------------------------------------

# SCRIPT_2 (get_coordinates_of_applications_based_on_text.py)
1. This Script takes the Output JSON file of Script_1 as the input file.
2. Based on the extracted text of applications given in the output of the previous script we get coordinates of the text of application.
3. The coordinates are updated in the output of SCRIPT_1 and a new JSON file is also created.
4. The new JSON file is called defined_coordinates_of_(PDF_NAME)_applications.
5. The defined_coordinates_of_(PDF_NAME)_applications is then used to take screenshots of the applications.

-------------------------------------------------------------------------------

# SCRIPT_3(read_coordinates_and_take_screenshots.py) 
1. This script uses the defined_coordinates_of_(PDF_NAME)_applications.JSON file,
2. It then takes screenshots based on the coordinates provided in the JSON file.
3. It saves the images in a folder called OUTPUT-SCREENSHOTS_OF_APPLICATIONS_IN_(PDF_NAME),
4. The images are saved in 3 formats, .PNG, .GIF and BASE64. Using the Name of the PDF with the page number and the section number as the name of the image file.
5. The Base64 of the image is also added in the defined_coordinates_of_(PDF_NAME)_applications.JSON
