"""
    Reference:
    https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/table-analysis/join_tables.ipynb

"""

import fitz

from pprint import pprint
import pandas as pd


def extract_table_data(pdf_path):
    
    doc = fitz.open(pdf_path)
    table_column_names = None
    all_extracted_text = []
    for page in doc:
        page_table = page.find_tables()

        # found a page without table - stop processing further
        if page_table == []:
            break

        tab = page_table[0]
        header = tab.header
        external = header.external
        names = header.names
        if page.number == 0:
            table_column_names = names

        # elif external == False and names != table_column_names:
        #     all_extracted_text.extend(names)
            
        extracted_text = tab.extract()
        if not external:
            extracted_text = extracted_text[:]
        
        all_extracted_text.extend(extracted_text)


    df_combined_result = pd.DataFrame(all_extracted_text, columns=table_column_names)
    df_as_dict_combined_result = df_combined_result.to_dict(orient='records')

    return df_as_dict_combined_result


def process_text(records: list):

    records_remapped_to_spec = []

    key_mapping = {'APPLICATION NUMBER': 'applicationNumber', 'FILING DATE' : 'applicationDate', 'APPLICANT': 'ownerName', 'DESCRIPTION OF MARK' : 'verbalElements', 'CLASS (ES)':'niceClass', 'PRIORITY DETAILS' : 'priorityNumber'}
    for i in records:
        i_remapped_dict = {key_mapping[key]: value for key, value in i.items() if key in key_mapping}
        records_remapped_to_spec.append(i_remapped_dict)

    return records_remapped_to_spec


def main():
    return True


if __name__ == "__main__":
    x =  extract_table_data('input_docs/vc/VC20230221-04.pdf')
    pprint(x)
    pprint(process_text(x))
