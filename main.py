import os
import re
import aiohttp
import asyncio
import telebot
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Replace with your token from BotFather
BASE_API_URL = os.getenv('BASE_API_URL')  # Base URL for the API
API_KEY = os.getenv('API_KEY')

bot = telebot.TeleBot(TOKEN)


def escape_markdown(text):
    # List of Markdown special characters
    markdown_chars = ['\\*', '\\_', '\\[', '\\]', '\\(', '\\)', '\\~', '\\`', '\\>', '\\#', '\\+', '\\-', '\\=', '\\|',
                      '\\{', '\\}', '\\.', '\\!']

    # Escape each special character with a backslash
    for char in markdown_chars:
        text = re.sub(char, lambda match: '\\' + match.group(0), text)

    return text


# Async function to handle API requests
async def handle_api_request(message, delete=False):
    user_id = str(message.from_user.id)
    message_id = str(message.message_id)

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY
    }
    async with aiohttp.ClientSession() as session:
        if delete:
            # Send DELETE request
            async with session.delete(f"{BASE_API_URL}/delete/{user_id}", headers=headers) as response:
                yield "Conversation deleted." if response.status == 200 else "Error in deletion."
        else:
            # Send POST request for handling streaming response
            data = {
                "message_id": message_id,
                "query": message.text,
                "conversation_id": user_id
            }
            async with session.post(f"{BASE_API_URL}/conversations/{user_id}", headers=headers, json=data) as response:
                if response.status == 200:
                    async for line in response.content.iter_any():
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line:
                            yield decoded_line
                else:
                    yield "Sorry, there was an error processing your request."


# Function to handle incoming messages
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Detect if the message is a delete message command
    delete_command = message.text.strip() in ['/delete', '/clear']

    # Asynchronously process the response
    async def process_response():
        last_chunk_received = False
        async for response in handle_api_request(message, delete=delete_command):
            # Escape Markdown characters
            formatted_response = escape_markdown(response)
            bot.send_message(message.chat.id, formatted_response, parse_mode='MarkdownV2')
            if not last_chunk_received:
                bot.send_chat_action(message.chat.id, 'typing')
                last_chunk_received = True

    # Show 'typing' action initially
    bot.send_chat_action(message.chat.id, 'typing')
    asyncio.run(process_response())


if __name__ == '__main__':
    print("Bot started")
    bot.polling(none_stop=True)
