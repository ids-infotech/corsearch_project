import re
import json
import fitz  # PyMuPDF

def extract_registration_numbers(pdf_text):
    registration_numbers = []

    # Updated regular expression to handle (111) values on the next line
    for match in re.finditer(r"\(111\)\s*(\d+)", pdf_text):
        registration_number = match.group(1)
        registration_numbers.append({"registrationNumber": registration_number})

    return registration_numbers

# Load PDF text (replace 'your_pdf_path.pdf' with the actual path)
with fitz.open("MG20220230-102.pdf") as pdf_document:
    pdf_text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text()

# Extract registration numbers from PDF
result = extract_registration_numbers(pdf_text)

# Save registration numbers to a JSON file
with open("registration_numbers.json", "w") as output_file:
    json.dump(result, output_file, indent=4)

# Display the result
print("Registration numbers extracted and saved to registration_numbers.json")
