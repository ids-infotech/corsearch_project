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
import core_pdf_to_images as m_pti
import core_pre_process_pdf as m_ppp
import core_text_extraction as m_te
import core_extract_logo as m_el
import core_parse_table
import core_sections_seperator


def generate_directory_paths(directory_identifer_code: str) -> dict:
    """generates pathlib objects for multiple stages"""

    # master directory
    directory_master_str = f'output_docs/{directory_identifer_code}'
    directory_master_path = Path(directory_master_str)
    directory_master_path.mkdir(parents=True, exist_ok=True) #TODO exists_ok should be false for this

    directory_sections_str = f'output_docs/{directory_identifer_code}/sections'
    directory_sections_path = Path(directory_sections_str)
    directory_sections_path.mkdir(parents=True, exist_ok=True)

    # directory input file as images of each page
    directory_images_str = f'output_docs/{directory_identifer_code}/page_images'
    directory_images_path = Path(directory_images_str)
    directory_images_path.mkdir(parents=True, exist_ok=True)

    # with cropped header and footer
    directory_cropped_str = f'output_docs/{directory_identifer_code}/cropped'
    directory_cropped_path = Path(directory_cropped_str)
    directory_cropped_path.mkdir(parents=True, exist_ok=True)

    # with vertically stacked
    # in case of two columm, these contain vertically stacked left and right of individual page
    # in case of one column, these contain the same page without any modifications
    directory_stacked_str = f'output_docs/{directory_identifer_code}/vertically_stacked'
    directory_stacked_path = Path(directory_stacked_str)
    directory_stacked_path.mkdir(parents=True, exist_ok=True)

    # with rois
    directory_rois_str = f'output_docs/{directory_identifer_code}/rois'
    directory_rois_path = Path(directory_rois_str)
    directory_rois_path.mkdir(parents=True, exist_ok=True)

    # storing logos
    directory_logos_str = f'output_docs/{directory_identifer_code}/logos'
    directory_logos_path = Path(directory_logos_str)
    directory_logos_path.mkdir(parents=True, exist_ok=True)

    # final result
    directory_result_str = f'output_docs/{directory_identifer_code}/result'
    directory_result_path = Path(directory_result_str)
    directory_result_path.mkdir(parents=True, exist_ok=True)

    paths = {
        'directory_sections_path': directory_sections_path,
        'directory_master_path': directory_master_path,
        'directory_images_path': directory_images_path,
        'directory_cropped_path': directory_cropped_path,
        'directory_stacked_path': directory_stacked_path,
        'directory_rois_path': directory_rois_path,
        'directory_result_path': directory_result_path,
        'directory_logos_path': directory_logos_path,
        'directory_result_path': directory_result_path
    }

    return paths



def main(parameters: dict):
    """main entrypoint"""
    

    """

        generate directory and file
        paths for multiple stages

    """

    # generate paths
    try:
        directory_paths = generate_directory_paths(parameters['paths']['unique_identifier_code'])
    except:
        logger.debug('could not generate directories')
        sys.exit()
    else:
        logger.info('successfully generated directories')


    try:
        input_pdf_path = Path(parameters['paths']['input_pdf_path'])
    except:
        logger.fatal('cannot load input pdf')
        sys.exit()
    else:

        # working on sections
        sections_processing_metadata = core_sections_seperator.split_pdf_sections(str(input_pdf_path), parameters['sections'], directory_paths['directory_sections_path'])
        
        if sections_processing_metadata is None:
            logger.debug('could not identify and seperate sections...exiting')
            sys.exit()
        else:
            logger.debug(f'identifed and parsed sections: {sections_processing_metadata}')
            sys.exit()

        if parameters['layout']['is_tabular_format'] == True:
            result = core_parse_table.main()
        else:
            pdf_converted_to_images = m_pti.convert_pdf_to_images(input_pdf_path, directory_paths['directory_images_path'])
            if pdf_converted_to_images == False:
                logger.info('exiting')
            else:
                logger.info('successfully converted pdf to images')

                # extract section info
                logger.info('extracting section info')

                # -------------------------------------------- #
                # CROPPING
                # -------------------------------------------- #
                logger.info('initiated cropping')
                images_file_paths = [file_path for file_path in directory_paths['directory_images_path'].glob('*.jpg')]

                # process first page
                image_file_path_first_page = images_file_paths[0]
                first_page_header_and_footer_removed = m_ppp.manual_remove_header_footer(str(image_file_path_first_page), parameters['layout']['target_pages_first']['header_height'], parameters['layout']['target_pages_first']['footer_height'])
                out_first_page_file = directory_paths['directory_cropped_path'] / image_file_path_first_page.name
                cv2.imwrite(str(out_first_page_file), first_page_header_and_footer_removed)

                # process target pages
                for image_file_path in  images_file_paths[1:-1]:
                    image_without_header_and_footer = m_ppp.manual_remove_header_footer(str(image_file_path), parameters['layout']['target_pages_middle']['header_height'], parameters['layout']['target_pages_middle']['footer_height'])
                    out_image_file = directory_paths['directory_cropped_path'] / image_file_path.name
                    cv2.imwrite(str(out_image_file), image_without_header_and_footer)

                # process last page
                image_file_path_last_page = images_file_paths[-1]
                last_page_header_and_footer_removed = m_ppp.manual_remove_header_footer(str(image_file_path_last_page), parameters['layout']['target_pages_last']['header_height'], parameters['layout']['target_pages_last']['footer_height'])
                out_last_page_file = directory_paths['directory_cropped_path'] / image_file_path_last_page
                cv2.imwrite(str(out_last_page_file), last_page_header_and_footer_removed)

                logger.info('finished cropping')


                # -------------------------------------------- #
                # STACKING
                # -------------------------------------------- #
                
                logger.info('initiatintg horizontal stacking')

                # based on number of columns, pre-process and vertically stack individual pages
                # single column layout
                images_for_horizontal_stacking = []
                if parameters['layout']['nos_columns'] == 1:
                    
                    logger.info('initiating stacking for one column layut')
    
                    cropped_path = directory_paths['directory_cropped_path']
                    # Retrieve all jpg files and sort them by their numerical value extracted from the filename
                    sorted_files_cropped = sorted(cropped_path.glob('*.jpg'), key=lambda x: int(Path(x).stem))

                    for ifp in sorted_files_cropped:
                        logger.info('Processing image with 1 column layout')
                        temp_image = cv2.imread(str(ifp))
                        images_for_horizontal_stacking.append(temp_image)
                        temp_image_path = directory_paths['directory_stacked_path'] / ifp.name
                        cv2.imwrite(str(temp_image_path), temp_image)

                # two column layout
                elif parameters['layout']['nos_columns'] == 2:

                    logger.info('initiating stacking for two column layout')

                    for image_file_path in directory_paths['directory_cropped_path'].glob('*.jpg'):
                        logger.info('processing image with 2 column layout')
                        two_column_image_stacked = m_ppp.convert_two_column_to_single_column_layout(str(image_file_path))
                        two_column_image_stacked_path = directory_paths['directory_stacked_path'] / image_file_path.name
                        images_for_horizontal_stacking.append(two_column_image_stacked)
                        cv2.imwrite(str(two_column_image_stacked_path), two_column_image_stacked)

                else:
                    logger.debug('TODO need to implement')

                logger.info('finished horizontal stacking')

                logger.info('initiating vertical stacking')
                target_width_for_final_stacking = images_for_horizontal_stacking[0].shape[1]
                # resized_for_final_stacking = [cv2.resize(img, (target_width_for_final_stacking, int(img.shape[0] * target_width_for_final_stacking / img.shape[1]))) for img in images_for_horizontal_stacking]

                resized_for_final_stacking = []
                for i, img in enumerate(images_for_horizontal_stacking):
                    resized_img = cv2.resize(img, (target_width_for_final_stacking, int(img.shape[0] * target_width_for_final_stacking / img.shape[1])))
                    cv2.imwrite(f'dev1/{i}.jpg', resized_img)
                    resized_for_final_stacking.append(resized_img)

                # final_stacked_image = np.concatenate(resized_for_final_stacking, axis=0)
                final_stacked_image = np.vstack(resized_for_final_stacking)
                final_stacked_image_path = directory_paths['directory_stacked_path'] / 'final_stacked.jpg'
                if not cv2.imwrite(str(final_stacked_image_path), final_stacked_image):
                    raise Exception("Could not write image")

                logger.info('finished vertical stacking')


                # -------------------------------------------- #
                # ROI EXTEACTION
                # -------------------------------------------- #

                logger.info('identifyfing and separating rois')
                # generate rois
                final_bounding_box_image, rois = m_ppp.get_rois(str(final_stacked_image_path))
                cv2.imwrite(str(directory_paths['directory_rois_path'] / 'final_bb.jpg'), final_bounding_box_image)

                logger.info('rois identification and seperation complete')


                data_for_df = []

                for index, i in enumerate(rois):
                    roi_file_path = directory_paths['directory_rois_path'] / f'roi_{index}.jpg'
                    cv2.imwrite(str(roi_file_path), i)

                    i_data = {
                        'file': None,
                        'text': None,
                        'entities': None,
                        'logo_base64': None,
                        'logo_img_path': None
                    }

                    roi_file = str(roi_file_path)
                    i_data['file'] = roi_file

                    # extracting raw text from roi image
                    roi_text = m_te.extract_text_from_image(i)
                    if roi_text:
                        i_data['text'] = roi_text

                    # extracting entities from raw text based on config regexes
                    roi_entities = m_te.extract_entities_regex(roi_text, parameters['regex_patterns'])
                    if roi_entities:
                        i_data['entities'] = roi_entities

                    # extracting logo from roi image
                    logo_base64_encoded_str, logo_out_file_path = m_el.extract_logo(roi_file_path, logo_parameters=parameters['logo'], directory_logos_path = directory_paths['directory_logos_path'])
                    
                    if parameters['logo']['get_base64'] == True:
                        if logo_base64_encoded_str:
                            i_data['logo_base64']= logo_base64_encoded_str
                    
                    if logo_out_file_path:
                        i_data['logo_img_path'] = logo_out_file_path

                    data_for_df.append(i_data)

                with open(directory_paths['directory_result_path'] / f'{parameters["paths"]["unique_identifier_code"]}_result.json', 'w') as json_out_handler:
                    json.dump(data_for_df, json_out_handler)


if __name__ == "__main__":

    try:
        with open('configs_json/vc.json', 'r') as json_in_handler:
            config_json = json.load(json_in_handler)
    except:
        logger.fatal('Cannot import config file')
    else:

        logger.info('successfully loaded config file')

    main(config_json)
