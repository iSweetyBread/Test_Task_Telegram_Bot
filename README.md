# Test Telegram Bot for Car Insurance Sales

It is a simple Telegram bot that assists users in purchasing car insurance by processing user-
submitted documents, interacting through AI-driven communications, and confirming transaction
details. This project integrates with OpenAI, Mindee (OCR), and uses mock services for testing.

## Features

- Conversational interaction powered by OpenAI (mocked for testing)
- Document image processing via Mindee OCR (mocked for testing)
- Extracts key user data from passport and vehicle ID
- Generates a final insurance document as a PDF
- Supports Telegram media groups and keyboard interactions
- Fully stateful session management per user

>IMPORTANT NOTE: As of this release, the AI functions are not available. The AI responses are mocked to illustrate the workflow logic.
## Setup Instructions

1. Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all required dependencies.

```bash
pip install pyTelegramBotAPI openai xhtml2pdf jinja2 requests
```
2. Configure your API keys for OpenAI API, Mindee API and Telegram API in a `APIconfig.json` file.

Example:
```python
{
  "openai_api_key": "[your_api_key]",
  "mindee_api_key": "[your_api_key]",
  "telegrambot_api_key": "[your_api_key]"
}
```
3. Run the bot.
```python
python main.py
```

## Bot workflow
1. User starts the bot with `/start`

User is greeted by the bot and is prompted to send images of their passport and vehicle identification document.

2. Bot confirms when **two** valid photos are received

User can send them either in an album - two at the same time - or user can send two images in two separate messages. Sending more will cause the bot to explain this problem to the user and reset this stage.

3. MindeeAPI processes the given images and sends the information gathered to the bot. Bot then sends this information to the user for confirmation.

If the user agrees, bot proceeds to the next stage of the workflow. If the user disagrees, bot prompts the user to send images one more time and reverts to the previous step of the workflow.

4. Bot shows fixed price and asks if the user agrees to this price.

If the user agrees, bot proceeds to the next stage of the workflow. If the user disagrees, bot explains, that the price is fixed and cannot be changed. Then bot waits for user to agree to the price.

5. Bot generates the `FinalDocument.pdf` file with all of the information gathered and confirmed by the user. Then, bot sends this file to the user.
6. Bot asks, whether the user wants to restart the process.

If the user agrees, bot reverts to the first stage. If the user disagrees, bot explains, that he can't do anything else and thanks the user for the purchase.

>Note: The user's responses are classified by the OpenaiAPI to determine, if the user agrees or not. This also means, that the bot handles other responses - in this case bot explains, that it can't understand those responses and asks the user to stick to the determined workflow. For simplicity, user can also use keys with 'YES' or 'NO', instead of answering with text.

## Links

The bot can be found [here](t.me/TestInsurance2025_bot)

The source code can be found [here](https://github.com/iSweetyBread/Test_Task_Telegram_Bot)
## License

[MIT](https://choosealicense.com/licenses/mit/)
