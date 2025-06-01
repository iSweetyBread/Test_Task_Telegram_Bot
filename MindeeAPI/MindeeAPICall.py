import requests
from GetKey import *
from enum import Enum

# Retrieves secured API key
token = get_key("mindee_api_key")

# Enum to define document types clearly
class DocTypes(Enum):
    passport = 1
    vehicle_id = 2

# Call to the MindeeAPI
def call_MindeeAPI(file_path, doc_type):
    # Choosing the correct MindeeAPI Endpoint, or raising an error, if it wasn't determined
    if doc_type == DocTypes.passport:
        url = "https://api.mindee.net/v1/products/mindee/passport/v1/predict"
    elif doc_type == DocTypes.vehicle_id:
        url = "https://api.mindee.net/v1/products/CUSTOM_VEHICLE_DOC/v1/predict"
    else:
        raise ValueError("Unsupported document type")

    # Authorization token
    headers = {
        "Authorization": f"Token {token}"
    }

    # Opens the image file in binary mode and prepares it for submission
    with open(file_path, "rb") as file:
        files = {
            "document": file
        }
        response = requests.post(url, files=files, headers=headers)

    # Returns the API response as a JSON object
    return response.json()

# Helper function to extract required information
def extract_info(result, doc_type):
    # Dictionary for all required data fields
    data = {
        "name": "",
        "surname": "",
        "date_of_birth": "",
        "car_make": "",
        "car_model": "",
        "car_year": "",
        "car_registration": "",
    }

    # Exrtacts data based on the type of the document
    if doc_type == DocTypes.passport:
        fields = result["document"]["inference"]["prediction"]
        data["name"] = fields.get("given_names", [""])[0]
        data["surname"] = fields.get("surname", "")
        data["date_of_birth"] = fields.get("birth_date", {}).get("value", "")
    elif doc_type == DocTypes.vehicle_id:
        fields = result["document"]["inference"]["prediction"]
        data["car_make"] = fields.get("make", "")
        data["car_model"] = fields.get("model", "")
        data["car_year"] = fields.get("year", "")
        data["car_registration"] = fields.get("registration_number", "")

    # Outputs populated dictionary
    return data