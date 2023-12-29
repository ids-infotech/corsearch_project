import fitz
from pathlib import Path
from master import logger

from pprint import pprint


def get_sections_header_first_page(original_pdf_path, section_info):
    try:
        doc = fitz.open(original_pdf_path)
    except Exception as e:
        logger.debug(f"Error opening PDF: {e}")
        return None

    section_info = section_info[0]
    search_result = None

    for page_num, page in enumerate(doc, start=1):
        # Define the clip area as the top half of the page
        top_half_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height / 2)

        # Search within the top half of the page
        areas = page.search_for(section_info['full_text'], clip=top_half_rect)

        if areas:
            search_result = [{'section_id': section_info['section_id'], 'start_page': page_num}]
            break

    doc.close()
    return search_result


def get_sections(original_pdf_path, section_info):
    try:
        doc = fitz.open(original_pdf_path)
    except Exception as e:
        logger.debug(f"Error opening PDF: {e}")
        return None
        
    # Dictionary to keep track of the highest page number for each section
    highest_pages = {}

    for i, page in enumerate(doc, start=1):
        for section in section_info:
            section_id = section['section_id']
            areas = page.search_for(section['full_text'])

            if areas:
                logger.info(f"Section ID {section_id} found at page {i}")
                if section_id not in highest_pages or i > highest_pages[section_id]['start_page']:
                    highest_pages[section_id] = {'section_id': section_id, 'start_page': i}

    doc.close()

    if len(highest_pages) == 0:
        logger.info('no sections found')
        return None
    else:
        # Sort the result based on section_id
        sorted_result = sorted(highest_pages.values(), key=lambda x: x['section_id'])
        return sorted_result



def split_pdf_sections(original_pdf_path, section_config,  target_directory):

    section_title_location = section_config['section_title_location']
    section_info = section_config['sections_info']
    section_skip_pages_start = section_config['skip_pages_start']


    if section_title_location == 'specific_pages':
        sections = get_sections(original_pdf_path, section_info)
    elif section_title_location == 'header_firstpage':
        sections = get_sections_header_first_page(original_pdf_path, section_info)
    else:
        logger.debug('not implemented - section location')
        return None
    
    if sections is None:
        return None

    # Open the original PDF
    try:
        doc = fitz.open(original_pdf_path)
    except Exception as e:
        logger.debug(f"Error opening PDF: {e}")
        return

    # Sort sections by start_page to ensure correct slicing
    sections = sorted(sections, key=lambda x: x['start_page'])

    for index, section in enumerate(sections):
        # Determine start and end pages for this section

        if section_skip_pages_start is None:
            start_page = section['start_page'] - 1  # fitz is 0-indexed
        else:
            start_page = section['start_page'] - 1 + section_skip_pages_start

        end_page = sections[index + 1]['start_page'] - 1 if index + 1 < len(sections) else len(doc)

        # Create a new document for this section
        section_doc = fitz.open()
        for page_num in range(start_page, end_page):
            section_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # Save the new document
        section_filename = f"{section['section_id']}.pdf"
        section_path = target_directory / section_filename
        section_doc.save(str(section_path))
        section_doc.close()

    doc.close()

    result_out = {}
    result_out['section_metadata'] = sections

    return result_out


if __name__ == "__main__":
    pass









