import json

def extract_text_between_keywords(json_data):
    extracted_text = []
    current_applicant_data = []

    for item in json_data['trademark']:
        for line in item:
            if 'Applicant' in line:
                if current_applicant_data:
                    extracted_text.append(current_applicant_data[:])  # Append a copy of the current data
                    current_applicant_data = []
            current_applicant_data.append(line)
    
    # Append the last applicant data
    if current_applicant_data:
        extracted_text.append(current_applicant_data[:])  # Append a copy of the last data
    
    return extracted_text

def main():
    with open(r'D:\python_projects\Corsearch\new files\cleaned_output_without_empty.json', 'r') as json_file:
        data = json.load(json_file)
    
    extracted_text = extract_text_between_keywords(data)
    
    # Output the extracted text
    output_json = {"trademark": extracted_text}

    # Save the extracted text with similar structure as input JSON
    with open('extracted_text.json', 'w') as output_file:
        json.dump(output_json, output_file, indent=4)

if __name__ == "__main__":
    main()
