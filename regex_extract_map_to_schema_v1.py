import re
from collections import defaultdict
import json
from pprint import pprint


# sample text from which data is to be extracted
sample_text = """
Applicant Kia Motors Corporation
Agent Rosann N. Knights-Bollers Regal Chambers
Address for Service Regal Building, 2nd Floor, Middle Street Kingstown
Application Number 64/2021
Filing Date February 05, 2021
Class(es)
Goods
9
Downloadable computer software for providing remote vehicle diagnosis, vehicle
maintenance information, entertainment in the form of audio and visual displays in
vehicles, third-party communication in vehicles, navigation function, and audio and
visual display in vehicles; downloadable DVR sideloading software application for
downloading DVR-recorded content for viewing on smartphones; downloadable
computer application software for vehicles; downloadable computer application
software for mobile phones for use in the operation and management of vehicles;
downloadable computer application software for use on smart phones for the provision
of information relating to vehicle trip information history, parking location management,
trip information, vehicle health management, driving information, and third-party
promotional data in the form of advertising for drivers; computer application software
"""

# removing multi-line and extra whitespoce between words
sample_text = ' '.join([word.strip() for word in sample_text.split()])


# define regex patterns for each field
regex_patterns = {
    "applicationNumber": r"(\d+)\/(\d{4})",
    "applicationDate": r"\D*\d{1,2},\s\d{4}",
    "ownerName": r"Applicant\\s*\n(\\D+)(?=Agent)",
    "representativeName": r"Address for Service\s*\n(\D*)(?=Application\s*Number)",
    "representativeAddress": r"xxxx",
    "representative_country": r"xxxx",
    "verbalElements": r"xxxx",
    "deviceElements": r"xxxx",
    "niceClass": r"(\s+\d{1,2}\s+)",
    "goodServiceDescription": r"Class\(es\)\s*([\s\S]*?)Applicant",
    "colors": r"Colour\sClaim:\s(\D*)",
    "priorityNumber": r"Number:\s*([\s\S]*?)Country",
    "priorityDate": r"Date:\s(\S*\D*\d*,\s*\d*)",
    "priorityCountry": r"Country:\s*([\s\S]*?)\n",
    "disclaimer": r"xxxx",
    "representativeName": r"xxxx",
    "representativeAddress": r"xxxx",
    "representativeCountry": r"xxxx"
}

# extract data using regex
extracted_data = {}
for key, pattern in regex_patterns.items():
    match = re.search(pattern, sample_text, re.IGNORECASE)
    if match:
        extracted_data[key] = match.group()


# map extracted data to the JSON schema
# note that the keys should match the first parameter of get() for consitency
# the second value of get is to put a default value in case there is no match
json_structure = {
    "trademark": {
        "publicationEvents": {
            "publicationEvent": {
                "applicationNumber": extracted_data.get("applicationNumber", ""),
                "applicationDate": extracted_data.get("applicationDate", "")
            }
        },
        "owners": {
            "owner": {
                "name": extracted_data.get("ownerName", None)
            }
        },

        "representatives": {
            "representative": {
                "name": extracted_data.get("representativeName", None),
                "address": extracted_data.get("representativeAddress", ""),
                "country": extracted_data.get("representativeCountry", "")
            }
        },

        "verbalElements": extracted_data.get("verbalElements", ""),
        "deviceElements": extracted_data.get("deviceElements", ""),
        "classifications": {
            "niceClass": extracted_data.get("niceClass", ""),
            "goodServiceDescription": extracted_data.get("goodServiceDescription", ""),
        },
        "priorities": {
            "priority": {
                "number": extracted_data.get("priorityNumber", ""),
                "date": extracted_data.get("priorityDate", ""),
                "country": extracted_data.get("priorityCountry", "")
            }
        },

        "colors": extracted_data.get("colors"),

    }
}

# writing to file
# use json.dumps() in case if you want to print it in std.out
with open('REGEX_EXTRACTION_RESULT.json', 'w') as json_out_handler:
    json.dump(json_structure, json_out_handler)
