import re
import json
import fitz  # PyMuPDF

def extract_data_from_pdf(pdf_text):
    data_entries = []

    for match in re.finditer(r"\(111\)\s*(\d+)", pdf_text):
        registration_number = match.group(1)

        # Find corresponding (220) entry for each (111) entry
        match_220 = re.search(r"\(220\)\s*([\d/]+)", pdf_text[match.end():])
        application_date = match_220.group(1) if match_220 else ""

        data_entries.append({"registrationNumber": registration_number, "applicationDate": application_date})

    return data_entries

# Load PDF text (replace 'your_pdf_path.pdf' with the actual path)
with fitz.open("MG20220230-102.pdf") as pdf_document:
    pdf_text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text()

# Extract data from PDF
result = extract_data_from_pdf(pdf_text)

# Save data to a JSON file
with open("extracted_data.json", "w") as output_file:
    json.dump(result, output_file, indent=4)

# Display the result
print("Data extracted and saved to extracted_data.json")
