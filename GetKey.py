import json

# Helper function, that retrieves API keys from config file
def get_key(name, filepath="APIconfig.json"):
    # Opens and reads the config file
    with open(filepath) as json_file:
        config = json.load(json_file)
    # Returns the API key based on the name of the API
    return config.get(name)