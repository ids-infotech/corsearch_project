import re
import json
from typing import Any, Dict

def extract_entities(input_text: str, json_structure: Dict[str, Any]) -> Dict[str, Any]:
    def extract_recursively(node):
        if isinstance(node, dict):
            return {key: extract_recursively(value) for key, value in node.items()}
        elif isinstance(node, str):
            match = re.search(node, input_text, re.IGNORECASE)
            return match.group() if match else None
        return node

    return extract_recursively(json_structure)


if __name__ == "__main__":
    pass

# # Example usage
# json_structure = {
#     "trademarks": {
#         "applicationNumber": "Numéro\\s+de\\s+dépôt\\s+.\\s+(\\w+/\\w+/\\s+\\d+/\\d+)",
#         # ... rest of the structure ...
#     }
# }


# input_text = "some text containing the information to be extracted based on the regex patterns"

# extracted_data = extract_entities(input_text, json_structure)
# print(json.dumps(extracted_data, indent=4))