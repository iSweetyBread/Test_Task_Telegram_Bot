import threading
from collections import defaultdict
from GetKey import *
import telebot
from telebot import types
from DocumentProcessing import process_doc
from enum import Enum
from MindeeAPI.MindeeAPICall import *
from MindeeAPI.MindeeAPIMockup import *
from OpenaiAPI.OpenaiAPICall import *
from OpenaiAPI.OpenaiAPIMockup import *


#---------------------------\/ Important Initial Parts \/---------------------------

# Assigning mock functions to replace API calls
generate_response = mock_generate_response
classify_response = mock_classify_response
call_MindeeAPI = mock_call_MindeeAPI

# Placeholder responses for different stages of the conversation. Made for clarity in testing.
# To remove in prod
placeholder_responses={
    1:"Hi, I'm a bot made to help you with creating your car insurance policy.\nPlease, send the photo of your passport and vehicle identification document.",
    2:"Unsupported input type at this stage",
    3:"Please, send one more photo",
    4:"Thanks! Your photos are being processed",
    5:"Oops, too many photos",
    6:"Please, confirm the information above",
    7:"The price is 100 us dollars. Do you agree?",
    8:"Thanks for you purchase! If you want to, you can start the process from the beginning",
    9:"Sorry, I don't understand you",
    10:"Thanks! Proceeding to the next step",
    11:"Please, send the photo of your passport and vehicle identification document again",
    12:"Thanks! Generating your document...",
    13:"Sorry, but the price is fixed",
    14:"Starting the process again",
    15:"Sorry, I don't have any other functions"
}

# Initializing the telegram bot with a secured token
token = get_key("telegrambot_api_key")
bot = telebot.TeleBot(token)

# Dictionaries to keep track of user specific data
user_state = {}
user_images = {}
user_data = {}

# For handling multiple images sent as an album
media_groups = defaultdict(list)
media_group_timers = {}
delay = 2

# Enum to define user states clearly. State description can be found in UserStates.txt
class UserState(Enum):
    state1 = 1
    state2 = 2
    state3 = 3
    state4 = 4


#---------------------------\/ Message Handlers \/---------------------------

# Handles the /start command sent by the user
@bot.message_handler(commands=['start'])
def start_message(message):
    # Initializes user specific storages
    user_id = message.from_user.id
    user_state[user_id] = UserState.state1
    user_images[user_id] = []

    # Generates and sends an OpenAI response
    reply = generate_response(user_state[user_id], '*user has just started the process*')
    bot.send_message(message.chat.id, reply)

    # Additional placeholder response for clarity in testing
    # To remove in prod
    bot.send_message(message.chat.id, placeholder_responses[1])

# Handles all messages with images
@bot.message_handler(func=lambda m: True, content_types=['photo'])
def handle_image(message):
    # Gets current user id and state
    user_id = message.from_user.id
    state = user_state.get(user_id)

    # Ensures, that the user is in correct state to send images. If not, exits handler earlier
    if state != UserState.state1:
        # Generates and sends an OpenAI response informing the user about incorrect state
        reply = generate_response(user_state[user_id], '*user sends a photo in a state, when they are not supposed to*')
        bot.send_message(message.chat.id, reply)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.send_message(message.chat.id, placeholder_responses[2])
        return


    media_group_id = message.media_group_id
    #If image is part of an album (media group)
    if media_group_id:
        # Appends message to the corresponding media group list
        media_groups[media_group_id].append(message)

        # Resets timer for a specific group
        if media_group_id in media_group_timers:
            media_group_timers[media_group_id].cancel()

        # Starts timer for a specific group to ensure, that the group is handled correctly
        media_group_timers[media_group_id] = threading.Timer(delay, process_media_group, args=(media_group_id, user_id, message))
        media_group_timers[media_group_id].start()
    # If image is not a part of an album (media group)
    else:
        # Ensures the existence of user specific image store and stores the image of the highest resolution
        user_images.setdefault(user_id, [])
        user_images[user_id].append(message.photo[-1].file_id)

        #If only one image was received
        if len(user_images[user_id]) == 1:
            # Generates and sends an OpenAI response prompting the user to send one more image
            reply = generate_response(user_state[user_id], '*user sends one photo, when the required amount is two*')
            bot.reply_to(message, reply)

            # Additional placeholder response for clarity in testing
            # To remove in prod
            bot.reply_to(message.chat.id, placeholder_responses[3])
        # If two images were received
        elif len(user_images[user_id]) == 2:
            # Generates and sends an OpenAI response thanking the user
            reply = generate_response(user_state[user_id], '*user sends two photos*')
            bot.reply_to(message, reply)

            # Additional placeholder response for clarity in testing
            # To remove in prod
            bot.reply_to(message, placeholder_responses[4])

            # Proceeds to the next stage of the workflow
            state2_intro(user_id, message)
        # If too many images were received
        else:
            # Generates and sends an OpenAI response informing the user about the problem
            reply = generate_response(user_state[user_id], '*user sends too many photos*')
            bot.reply_to(message, reply)

            # Additional placeholder response for clarity in testing
            # To remove in prod
            bot.reply_to(message, placeholder_responses[5])

            # Resets user specific image storage
            user_images[user_id] = []

# Handles all messages with any other input except for images or text
@bot.message_handler(func=lambda m: True, content_types=['audio', 'video', 'document', 'sticker', 'voice', 'video_note', 'location', 'contact'])
def handle_other(message):
    # Generates and sends an OpenAI response informing the user about the problem
    reply = generate_response(user_state[message.from_user.id], '*user sends unsupported input type*')
    bot.reply_to(message, reply)

    # Additional placeholder response for clarity in testing
    # To remove in prod
    bot.reply_to(message, placeholder_responses[2])

# Handles all messages with text
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    # Gets current user id and state
    user_id = message.from_user.id
    state = user_state.get(user_id)

    # Routing the message to appropriate handler based on the current user state
    match state:
        case UserState.state1:
            text_state1_response(message)
        case UserState.state2:
            text_state2_response(message)
        case UserState.state3:
            text_state3_response(message)
        case UserState.state4:
            text_state4_response(message)


#---------------------------\/ Helper Functions \/---------------------------

# Helps to process images sent by the specific user
def process_image(user_id):
    # Storage for the final set of data
    result_final = {}

    # Retrieves the list of image files uploaded by specific user
    user_files = user_images[user_id]
    # Expected document types
    doc_types = [DocTypes.passport, DocTypes.vehicle_id]

    for i, file_id in enumerate(user_files):
        # Assigns the expected doc type based on the image index, or "UNKNOWN" if out of range
        doc_type = doc_types[i] if i < len(doc_types) else "UNKNOWN"
        # Downloads and processes each image. Uses API call and helper function contained in MindeeAPICall/MindeeAPICall.py
        image = bot.download_file(bot.get_file(file_id).file_path)
        result = call_MindeeAPI(image, doc_type)
        extracted_data = extract_info(result, doc_type)
        # Merges the extracted data into the final dictionary
        for key in extracted_data:
            current_value = result_final.get(key, '')
            new_value = extracted_data[key]
            result_final[key] = current_value if current_value else new_value

    return result_final

# Helps to process images inside an album (media group) sent by the specific user
def process_media_group(media_group_id, user_id, message):
    # Retrieves and removes the list of messages for specific media group
    messages = media_groups.pop(media_group_id, [])
    # Cancels the timer for specific media group
    media_group_timers.pop(media_group_id, None)

    # Ensures, that the user is in correct state to send images. If not, exits handler earlier
    if user_state.get(user_id) != UserState.state1:
        return

    # If exactly two images were sent in the media group
    if len(messages) == 2:
        # Initializes user specific image list
        user_images.setdefault(user_id, [])
        # Extracts file IDs from the highest resolution image in each message
        for msg in messages:
            user_images[user_id].append(msg.photo[-1].file_id)
        # Generates and sends an OpenAI response confirming receipt of two images
        reply = generate_response(user_state[user_id], '*user sends two photos*')
        bot.reply_to(message, reply)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[4])

        # Proceeds to the next stage of the workflow
        state2_intro(user_id, message)
    # If more than two images were sent in the media group
    else:
        # Generates and sends an OpenAI response informing the user about the problem
        reply = generate_response(user_state[user_id], '*user sends too many photos*')
        bot.reply_to(message, reply)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[5])

        # Resets user specific image storage
        user_images[user_id] = []


#---------------------------\/ Workflow Transition Functions \/---------------------------

# Transition into state 2
def state2_intro(user_id, message):
    # Moves the user into state 2
    user_state[user_id] = UserState.state2
    # Processes and stores images
    data = process_image(user_id)
    user_data[user_id] = data

    # Initializes the message to display extracted information for user confirmation
    msg_text = ""

    # Builds the message to display extracted information for user confirmation
    for key in data:
        msg_text = msg_text + key + ": " + data[key] + "\n"
    # Sends the message to display extracted information for user confirmation
    bot.send_message(message.chat.id, msg_text)

    # Creates a reply keyboard with YES and NO options for confirmation
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton(text='YES')
    no_button = types.KeyboardButton(text='NO')
    markup.add(yes_button, no_button)

    # Generates and sends an OpenAI response acknowledging user's images
    reply = generate_response(user_state[user_id], '*user has just sent the photos*')
    bot.send_message(message.chat.id, reply, reply_markup=markup)

    # Additional placeholder response for clarity in testing
    # To remove in prod
    bot.send_message(message.chat.id, placeholder_responses[6])

# Transition into state 3
def state3_intro(user_id, message):
    # Moves the user into state 3
    user_state[user_id] = UserState.state3

    # Creates a reply keyboard with YES and NO options for confirmation
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton(text='YES')
    no_button = types.KeyboardButton(text='NO')
    markup.add(yes_button, no_button)

    # Generates and sends an OpenAI response acknowledging user's confirmation
    reply = generate_response(user_state[user_id], '*user has just confirmed the information*')
    bot.send_message(message.chat.id, reply, reply_markup=markup)

    # Additional placeholder response for clarity in testing
    # To remove in prod
    bot.send_message(message.chat.id, placeholder_responses[7], reply_markup=markup)

# Transition into state 4
def state4_intro(user_id, message):
    # Moves the user into state 3
    user_state[user_id] = UserState.state4
    # Creates and sends a car insurance policy for a specific user
    process_doc(user_data[user_id])
    with open('FinalDocument.pdf', 'rb') as file:
        bot.send_document(message.chat.id, file)

    # Creates a reply keyboard with YES and NO options for confirmation
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton(text='YES')
    no_button = types.KeyboardButton(text='NO')
    markup.add(yes_button, no_button)

    # Generates and sends an OpenAI response acknowledging the end of the workflow
    reply = generate_response(user_state[user_id], '*user has just finished the process*')
    bot.send_message(message.chat.id, reply, reply_markup=markup)

    # Additional placeholder response for clarity in testing
    # To remove in prod
    bot.send_message(message.chat.id, placeholder_responses[8], reply_markup=markup)


#---------------------------\/ Text Message Handlers \/---------------------------

# Handler for text messages in state 1
def text_state1_response(message):
    # Stores user's message
    input = message.text
    # Generates and sends an OpenAI response informing the user about the problem
    reply = generate_response(user_state[message.from_user.id], input)
    bot.reply_to(message, reply)

    # Additional placeholder response for clarity in testing
    # To remove in prod
    bot.reply_to(message, placeholder_responses[9])

# Handler for text messages in state 2
def text_state2_response(message):
    # Stores user's message
    input = message.text
    # Evaluates user's message into three categories: 'YES', 'NO', 'UNKNOWN'
    response = classify_response(input)
    # If user's message evaluated as 'YES'
    if (response == 'YES'):
        # Generates and sends an OpenAI response acknowledging user's confirmation
        reply = generate_response(user_state[message.from_user.id], 'YES')
        # Removes previous reply keyboard
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, reply, reply_markup=markup)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[10], reply_markup=markup)

        # Proceeds to the next stage of the workflow
        state3_intro(message.from_user.id, message)
    # If user's message evaluated as 'NO'
    elif (response == 'NO'):
        # Generates and sends an OpenAI response prompting the user to resend images
        reply = generate_response(user_state[message.from_user.id], 'NO')
        # Removes previous reply keyboard
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, reply, reply_markup=markup)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[11], reply_markup=markup)

        # Reverts user to the previous stage of the workflow
        user_state[message.from_user.id] = UserState.state1
        # Resets user specific image storage
        user_images[message.from_user.id] = []
    # If user's message evaluated as 'UNKNOWN'
    else:
        # Generates and sends an OpenAI response informing about the problem
        reply = generate_response(user_state[message.from_user.id], input)
        bot.reply_to(message, reply)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[9])

# Handler for text messages in state 3
def text_state3_response(message):
    # Stores user's message
    input = message.text
    # Evaluates user's message into three categories: 'YES', 'NO', 'UNKNOWN'
    response = classify_response(input)
    # If user's message evaluated as 'YES'
    if (response == 'YES'):
        # Generates and sends an OpenAI response acknowledging user's consent
        reply = generate_response(user_state[message.from_user.id], 'YES')
        # Removes previous reply keyboard
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, reply, reply_markup=markup)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[12], reply_markup=markup)

        # Proceeds to the next stage of the workflow
        state4_intro(message.from_user.id, message)
    # If user's message evaluated as 'NO'
    elif (response == 'NO'):
        # Generates and sends an OpenAI response informing about the fixed price
        reply = generate_response(user_state[message.from_user.id], 'NO')
        # Removes previous reply keyboard
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, reply, reply_markup=markup)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[13], reply_markup=markup)
    # If user's message evaluated as 'UNKNOWN'
    else:
        # Generates and sends an OpenAI response informing about the problem
        reply = generate_response(user_state[message.from_user.id], input)
        bot.reply_to(message, reply)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[9])

# Handler for text messages in state 4
def text_state4_response(message):
    # Stores user's message
    input = message.text
    # Evaluates user's message into three categories: 'YES', 'NO', 'UNKNOWN'
    response = classify_response(input)
    # If user's message evaluated as 'YES'
    if (response == 'YES'):
        # Generates and sends an OpenAI response acknowledging user's decision
        reply = generate_response(user_state[message.from_user.id], 'YES')
        # Removes previous reply keyboard
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, reply, reply_markup=markup)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[14], reply_markup=markup)

        # Sends user into the beginning of the workflow
        start_message(message)
    # If user's message evaluated as 'NO'
    elif (response == 'NO'):
        # Generates and sends an OpenAI response acknowledging user's decision
        reply = generate_response(user_state[message.from_user.id], 'NO')
        # Removes previous reply keyboard
        markup = types.ReplyKeyboardRemove()
        bot.reply_to(message, reply, reply_markup=markup)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[15], reply_markup=markup)
    # If user's message evaluated as 'UNKNOWN'
    else:
        # Generates and sends an OpenAI response informing about the problem
        reply = generate_response(user_state[message.from_user.id], input)
        bot.reply_to(message, reply)

        # Additional placeholder response for clarity in testing
        # To remove in prod
        bot.reply_to(message, placeholder_responses[9])

# Ensures the continuous work of the bot
bot.polling(none_stop=True, interval=0)