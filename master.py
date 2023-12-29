import sys
import logging
import cv2
import numpy as np
import json
from pprint import pprint


logger = logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# reading and writing files
from pathlib import Path

# application specific modules
import core_pdf_to_images
import core_process_pdf
import core_text_extraction
import core_extract_logo
import core_parse_table
import core_sections_seperator
import core_regex_extractor


def generate_directory_paths(directory_identifer_code: str) -> dict:
    """generates pathlib objects for multiple stages"""

    # master directory
    directory_master_str = f'output_docs/{directory_identifer_code}'
    directory_master_path = Path(directory_master_str)
    directory_master_path.mkdir(parents=True, exist_ok=True) #TODO exists_ok should be false for this


    directory_sections_str = f'output_docs/{directory_identifer_code}/sections'
    directory_sections_path = Path(directory_sections_str)
    directory_sections_path.mkdir(parents=True, exist_ok=True)

    # final result
    directory_result_str = f'output_docs/{directory_identifer_code}/result'
    directory_result_path = Path(directory_result_str)
    directory_result_path.mkdir(parents=True, exist_ok=True)

    paths = {
        'directory_sections_path': directory_sections_path,
        'directory_master_path': directory_master_path,
        'directory_result_path': directory_result_path,
    }

    return paths


def read_files_from_directory_ascending(directory_path: str, file_format: str) -> list:
    # retrieve all jpg files and sort them by their numerical value extracted from the filename
    sorted_files = sorted(directory_path.glob(f'*.{file_format}'), key=lambda x: int(Path(x).stem))
    return sorted_files



def main(parameters: dict):
    """main entrypoint"""
    

    """

        generate directory and file
        paths for multiple stages

    """

    # read input pdf file
    try:
        input_pdf_path = Path(parameters['paths']['input_pdf_path'])
    except:
        logger.fatal('cannot load input pdf')
        sys.exit()


    # generate paths
    try:
        directory_paths = generate_directory_paths(parameters['paths']['unique_identifier_code'])
    except:
        logger.debug('could not generate directories')
        sys.exit()
    else:
        logger.info('generated directories')
    

    # working on sections
    sections_processing_metadata = core_sections_seperator.split_pdf_sections(str(input_pdf_path), parameters['sections'], directory_paths['directory_sections_path'])
    
    if sections_processing_metadata is None:
        logger.debug('could not identify and seperate sections...exiting')
        sys.exit()
    else:
        logger.debug(f'identifed and parsed sections: {sections_processing_metadata}')


    """

        PDFs are divided into two basic types
        at a conceptual level - table based 
        and all others.

        table based pdfs do not require a lot of 
        manipulation - as of now

        hence, these are processed differently
        - idea is to be more efficient

    """
    files_in_section_directory = read_files_from_directory_ascending(directory_paths['directory_sections_path'], 'pdf')

    generated_sections_roi_paths = []

    for i_file in files_in_section_directory:
        # process a table based file
        if parameters['layout']['is_tabular_format'] == True:
            logger.info('processing a table based pdf')
            result = core_parse_table.main()

        # process a non-table based file
        else:
            logger.info('processing a general pdf')

            # generate a new directory for storing data generated for each section
            ind_section_dir_str = f"output_docs/{parameters['paths']['unique_identifier_code']}/section_{i_file.stem}"
            ind_section_dir_str_path = Path(ind_section_dir_str)
            ind_section_dir_str_path.mkdir(parents=True, exist_ok=True)

            # processing pdf
            roi_result, section_directory_roi = core_process_pdf.main(i_file, parameters['layout'], ind_section_dir_str)

            generated_sections_roi_paths.append(section_directory_roi)


    for index, i_section in enumerate(generated_sections_roi_paths):
        section_roi_jpg = read_files_from_directory_ascending(i_section, 'jpg')
        # extracting text, entities, and logos from each roi    
        final_result = []
        for index, i in enumerate(section_roi_jpg):

            i_data = {
                'file': None,
                'text': None,
                'entities': None,
                'logo_base64': None,
                'logo_img_path': None
            }
            
            roi_file = str(i)
            i_data['file'] = roi_file

            # extracting text raw text form image via ocr
            roi_text = core_text_extraction.extract_text_from_image(i)
            if roi_text is not None:
                i_data['text'] = roi_text

                # extracting entities from raw text based on config regexes
                section_1_json_structure = parameters['json_structure'][0]['trademarks']
                roi_entities = core_regex_extractor.extract_entities(roi_text, section_1_json_structure)
                if roi_entities:
                    i_data['entities'] = roi_entities


            directory_logos_path = Path(i_section)
            directory_logos_path = directory_logos_path.parent / 'logos'
            directory_logos_path.mkdir(parents=True, exist_ok=True)

            # extract logo
            logo_base64_encoded_str, logo_out_file_path = core_extract_logo.extract_logo(i, logo_parameters=parameters['logo'], directory_logos_path = directory_logos_path)

            if parameters['logo']['get_base64'] == True:
                if logo_base64_encoded_str:
                    i_data['logo_base64']= logo_base64_encoded_str
            
            if logo_out_file_path:
                i_data['logo_img_path'] = logo_out_file_path
            
            final_result.append(i_data)


        with open(f'RESULT_SECTION_{index}L.json', 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False)




if __name__ == "__main__":

    try:
        with open('configs_json/vc_errata.json', 'r') as json_in_handler:
            config_json = json.load(json_in_handler)
    except:
        logger.fatal('Cannot import config file')
    else:

        logger.info('successfully loaded config file')

    main(config_json)
            
            




