import pdfplumber
import json

def define_coordinates_from_pdf(pdf_path, extracted_text_json_path, output_json_path):
    extracted_text_dict = {}
    # Load the JSON file containing the previously extracted text (if it exists)
    try:
        with open(extracted_text_json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        print("[-] Existing file not found")
        return
    except Exception as e:
        print(e)
        return

    # Extract text from the PDF and store it in extracted_text_dict
    with pdfplumber.open(pdf_path) as pdf:
        min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

        for page_number, page in enumerate(pdf.pages, start=1):
            extracted_text_dict[str(page_number)] = {
                "page_number": page_number,
                "extracted_texts": []
            }
            print("[*] page number:", page_number)
            print("----------------------")

            # lines
            page = pdf.pages[page_number - 1]  # Pages are 0-based index

            # Extract words with bounding box coordinates
            words_with_bounding_box = page.extract_words()

            # Group words into lines based on y-coordinates
            lines = {}
            for word in words_with_bounding_box:
                # Round y-coordinate to handle floating-point inaccuracies
                y0 = round(word["top"], 2)
                y1 = round(word["bottom"], 2)
                if (y0, y1) in lines:
                    lines[(y0, y1)]["text"].append(word["text"])
                    lines[(y0, y1)]["x0"].append(word["x0"])
                    lines[(y0, y1)]["x1"].append(word["x1"])
                else:
                    lines[(y0, y1)] = {
                        "text": [word["text"]],
                        "x0": [word["x0"]],
                        "x1": [word["x1"]],
                    }

            # Sort lines by y-coordinates
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])

            # Loop through each key (representing page numbers) and content data in the existing JSON data
            for page_data_key, page_data in existing_data.items():
                # Skip the iteration if there is no 'content_data' for the page
                if not page_data.get("content_data"):
                    continue
                
                # Loop through each content entry in the 'content_data'
                for content_entry in page_data["content_data"]:
                    # Get the first and last words of the text snippet to match against
                    start = content_entry["text"][0]
                    end = content_entry["text"][-1]

                    match = False   # Initialize the match flag as False

                    # Reset the coordinates to the extremes before checking for a new match
                    min_x0, min_y0, max_x1, max_y1 = float('inf'), float('inf'), -float('inf'), -float('inf')

                    # Iterate over each line sorted by y-coordinate
                    for (y0, y1), line_info in sorted_lines:
                        # Combine words in the line to form the text string
                        text = " ".join(line_info["text"])

                        if match:
                            # If a match has been found, continue to update the coordinates
                            # to include all lines that are part of the text block
                            # to get the maximum coordinates of the text
                            min_x0 = min(min_x0, min(line_info["x0"]))
                            min_y0 = min(min_y0, y0)
                            max_x1 = max(max_x1, max(line_info["x1"]))
                            max_y1 = max(max_y1, y1)

                        # comparing texts
                        # Check if the current line's text matches the starting text
                        # The comparison is case-insensitive and ignores newline characters
                        start_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in start.split(" ") if i]

                        # If start is found and we haven't matched before, set match to True
                        if start_found and not match:
                            match = True

                        # comparing texts
                        # Check if the current line's text matches the ending text
                        end_found = [i.replace("\n", '').lower() for i in text.split(" ") if i] == [
                            i.replace("\n", '').lower() for i in end.split(" ") if i]

                        # If end is found and we have a match, finalize the coordinates
                        if end_found and match:
                            # Add the extracted text with its coordinates to the dictionary
                            extracted_text_dict[str(page_number)]["extracted_texts"].append({
                                "extracted_text": '\n'.join(content_entry['text']),
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1,
                            })
                            match = False   # Reset match for the next content entry
                            print("[+] extracted the text => ",
                                  '\n'.join(content_entry['text']), "\n")

                            # Update the content_data entry with coordinates
                            content_entry["coordinates"] = {
                                "x0": min_x0,
                                "y0": min_y0,
                                "x1": max_x1,
                                "y1": max_y1
                            }
                            # Once the end is found, break out of the loop as the coordinates
                            # for the current text block have been fully captured
                            break

    # Save the modified JSON file with coordinates added
    # This the previous JSON file with all the data
    # We can remove the coordinates from the previous input JSON file
    # But maybe its needed to add the base64, these coordinates can be used to match the 'coordinates' 
    with open(extracted_text_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, indent=4, separators=(',', ': '))

    # Save the defined coordinates to a new JSON file with formatting
    # This JSON is later used to take screenshots
    with open(output_json_path, 'w', encoding='utf-8') as output_json_file:
        json.dump(extracted_text_dict, output_json_file, indent=4, separators=(',', ': '))


# EXAMPLE USAGE
# Replace with the path to your PDF file
pdf_path = "BT20230612-108.pdf"  
# This is the JSON input file
extracted_text_json_path = "BT20230612-108.pdf_text_of_applications.json"  
# This file is created as the output
output_json_path = f"defined_coordinates_of_{pdf_path}_applications.json"  
# Call the function while using these parameters
define_coordinates_from_pdf(pdf_path, extracted_text_json_path, output_json_path)