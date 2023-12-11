import fitz  # PyMuPDF

# Load PDF text (replace 'your_pdf_path.pdf' with the actual path)
with fitz.open("MG20220230-102.pdf") as pdf_document:
    pdf_text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pdf_text += page.get_text()

# Save extracted text to a plain text file
with open("text.txt", "w", encoding="utf-8") as output_file:
    output_file.write(pdf_text)

print("Extracted text saved to extracted_text.txt")
