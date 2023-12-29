import re
import json
from paddleocr import PaddleOCR
from pathlib import Path

from pprint import pprint
from master import logger

try:
    ocr = PaddleOCR(use_angle_cls=True, lang='french')
except Exception as e:
    logger.fatal(str(e))
else:
    logger.info('Successfully loaded OCR Reader')


def extract_text_from_image(image_path) -> str:
    try:
        result_ocr = ocr.ocr(str(image_path), cls=True)
    except:
        logger.DEBUG('Could not read text from image')
        return None
    else:
        extracted_text = []

        try:
            for line_block in result_ocr:
                for line in line_block:
                    # Extract only the text part
                    extracted_text.append(line[1][0])  # line[1][0] is the text
        except:
            return None

        if len(extracted_text) > 0:
            result = ' '.join([i.strip() for i in extracted_text])
            logger.info('extracted text successfully')
            return result
        else:
            logger.info('no text extracted')
            return None


def populate_json_structure(structure, data):
    if isinstance(structure, dict):
        for key, value in structure.items():
            if isinstance(value, (dict, list)):
                populate_json_structure(value, data)
            elif key in data:
                structure[key] = data[key]
    elif isinstance(structure, list):
        for item in structure:
            populate_json_structure(item, data)



def extract_entities_regex(text, regex_patterns):

    with open('configs_json/vc.json', 'r') as f:
        parameters = json.load(f)

    json_structure = parameters['json_structure']

    extracted_data = {}
    for key, pattern in regex_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                extracted_data[key] = match.group(2)
            except:
                extracted_data[key] = match.group()

    # copy to avoid modifying the original structure
    populated_structure = json_structure.copy()

    populate_json_structure(populated_structure, extracted_data)
    return populated_structure


if __name__ == "__main__":
    pass
