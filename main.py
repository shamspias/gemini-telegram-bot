import os
import requests
import telebot
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Replace with your token from BotFather
BASE_API_URL = os.getenv('BASE_API_URL')  # Base URL for the API
API_KEY = os.getenv('API_KEY')

bot = telebot.TeleBot(TOKEN)


# Function to handle API requests
def handle_api_request(message, delete=False):
    user_id = str(message.from_user.id)
    message_id = str(message.message_id)

    if delete:
        # Send DELETE request
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
        }
        response = requests.delete(f"{BASE_API_URL}/delete/{user_id}", headers=headers)
        return "Conversation deleted." if response.status_code == 200 else "Error in deletion."
    else:
        # Send POST request with stream=True for handling streaming response

        data = {
            "message_id": message_id,
            "query": message.text,
            "conversation_id": user_id
        }
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
        }
        response = requests.post(f"{BASE_API_URL}/conversations/{user_id}", headers=headers, json=data, stream=True)

        if response.status_code == 200:
            response_text = ''
            try:
                for line in response.iter_lines():
                    if line:
                        response_text += line.decode('utf-8')
            except requests.exceptions.ChunkedEncodingError as e:
                # Handle potential errors during streaming
                return f"Error while streaming response: {e}"

            return response_text if response_text else "No response received from the API or the response is empty."
        else:
            return "Sorry, there was an error processing your request."


# Handle incoming messages
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Detect if the message is a delete command
    delete_command = message.text.strip() in ['/delete', '/clear']

    # Send API request and get the response
    response = handle_api_request(message, delete=delete_command)

    # Send the response to the user
    bot.send_message(message.chat.id, response)


if __name__ == '__main__':
    print("Bot started")
    bot.polling(none_stop=True)
