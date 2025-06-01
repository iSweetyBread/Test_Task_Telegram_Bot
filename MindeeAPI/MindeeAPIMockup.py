from MindeeAPI.MindeeAPICall import *

# Mock call to the MindeeAPI, that returns predefined values
def mock_call_MindeeAPI(image, doc_type):
    # Simulated return values for passport document
    if doc_type == DocTypes.passport:
        return {
            "document": {
                "inference": {
                    "prediction": {
                        "given_names": ["John"],
                        "surname": "Doe",
                        "birth_date": {"value": "1985-07-13"}
                    }
                }
            }
        }
    # Simulated return values for vehicle id document
    elif doc_type == DocTypes.vehicle_id:
        return {
            "document": {
                "inference": {
                    "prediction": {
                        "make": "Toyota",
                        "model": "Corolla",
                        "year": "2012",
                        "registration_number": "ABC1234",
                    }
                }
            }
        }
    # Simulated return values for unknown document
    else:
        return {
            "document": {
                "inference": {
                    "prediction": {}
                }
            }
        }