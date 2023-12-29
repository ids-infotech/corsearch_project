import fitz  # PyMuPDF, imported as fitz for backward compatibility reasons
from pathlib import Path
from master import logger


def convert_pdf_to_images(input_pdf_path, images_save_directory):
    """
        reads an input file - pdf
        converts every page to an image
        writes images to a directory
    """
    try:
        doc = fitz.open(input_pdf_path)
    except Exception as e:
        print(e)
        logger.debug('could not load PDF for images converstion')
        return False
    else:
        logger.info('successfully loaded PDF for images conversion')

        try:
            for i, page in enumerate(doc, 1):
                page_as_image = page.get_pixmap()
                page_as_image_out_path = str(images_save_directory / f'{i}.jpg')
                page_as_image.save(page_as_image_out_path)
        except Exception as e:
            print(e)
            logger.debug('could not convert PDF pages to images')
            return False
        else:
            return True

if __name__ == "__main__":
    convert_pdf_to_images(r"D:\IDS Infotech\ids-cosearch-unshared\input_docs\vc\VC20221212-28.pdf", "D:\IDS Infotech\ids-cosearch-unshared\trial_output_new_pdf")