from OpenaiAPI.OpenaiAPICall import *
from unittest.mock import patch

# Mock helper function to generate responses, that returns predefined values
def mock_generate_response(state, message):
    # Simulated return value for user's input
    mock_response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": f"This is a mock response from ChatGPT for user input \"{message}\"."
                }
            }
        ]
    }
    # Avoids real API requests during testing
    with patch("openai.ChatCompletion.create") as mock_request:
        mock_request.return_value = mock_response
        result = generate_response(state, message)
        return result

# Mock helper function to evaluate responses, that returns predefined values
def mock_classify_response(message):
    # Simulated evaluation for user's input with predefined response
    if(message == "YES"):
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"YES"
                    }
                }
            ]
        }
    # Simulated evaluation for user's input with predefined response
    elif(message == "NO"):
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"NO"
                    }
                }
            ]
        }
    # Simulated evaluation for user's input with predefined response
    else:
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"UNKNOWN"
                    }
                }
            ]
        }

    # Avoids real API requests during testing
    with patch("openai.ChatCompletion.create") as mock_request:
        mock_request.return_value = mock_response
        result = call_OpenaiAPI(message)
        return result