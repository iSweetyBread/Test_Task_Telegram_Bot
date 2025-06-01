import openai
from GetKey import *

# Retrieves secured API key
openai.api_key = get_key("openai_api_key")

# Call to the OpenaiAPI
def call_OpenaiAPI(prompt):
    # Stores the API response based on the given parameters of LLM model and the prompt
    response = openai.ChatCompletion.create(
        model="gpt-4",
        input=f"{prompt}"
    )
    # Returns the content of the first response message
    return response['choices'][0]['message']['content']

# Helper function to generate responses
def generate_response(state, input):
    # Detailed prompt including the current state and user input
    prompt = (
        f"You are a helpful Telegram bot assisting a user in '{state}'."
        f"State descriptions are described below:"
        f"State 1 - greeting the user; describing the purpose of the bot, as a tool to generate car insurance document; prompting the user to send the photo of a passport and a photo of a vehicle identification document"
        f"State 2 - asking the user to confirm the information taken from the photos; if the user accepts, then proceeding to the next state; if the user declines, then prompting the user to send the photos again"
        f"State 3 - giving the user the fixed price of 100 us dollars; asking the user to accept the price; if the user agrees, telling the user, that the insurance policy is being generated and will be available as soon as possible; if the user disagrees, then explaining to the user, that the price is fixed and cannot be changed under any circumstances"
        f"State 4 - thanking the user for the purchase of the car insurance; asking the user, if they would like to restart the process for another insurance document; if the user agrees, telling the user, that the process will restart in a moment; if the user disagrees, telling the user, that the bot does not have any other functionalities, wishing the user a good day and saying goodbye"
        f"if the user's input is empty, you must explain the part of the process, the user is in right now"
        f"The user just said: '{input}'. "
        f"Respond politely and concisely with a friendly tone."
    )

    # Returns the response based on the detailed prompt
    return call_OpenaiAPI(prompt)

# Helper function to evaluate user inputs into three categories: 'YES', 'NO', 'UNKNOWN'
def classify_response(input):
    # Detailed prompt including the user's input
    prompt = (
        "You are an assistant that classifies user replies into one of three categories: "
        "'YES' if the user agrees, 'NO' if the user disagrees, or 'UNKNOWN' if unclear.\n"
        f"User input: \"{input}\"\n"
        "Respond only with one word: YES, NO, or UNKNOWN."
    )
    # Receives and normalizes the LLM's response
    classification = call_OpenaiAPI(prompt)
    classification = classification.strip().upper()

    # Validates the result. If result is unexpected, evaluates it into 'UNKNOWN'
    if classification not in ['YES', 'NO', 'UNKNOWN']:
        classification = 'UNKNOWN'
    # Returns the evaluation
    return classification