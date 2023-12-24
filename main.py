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
    # First, replace literal '\n' with actual newline characters
    text = text.replace('\\n', '\n')

    # Escape Markdown special characters except for newline characters
    markdown_chars = r'[\*_\[\]()~`>#\+\-=|{}\.!]'
    escaped_text = re.sub(markdown_chars, lambda m: '\\' + m.group(0), text)

    return escaped_text


# Async function to handle API requests
async def handle_api_request(message, delete=False, image_url=None):
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
            # Determine if the message is a text or photo with caption
            query_text = message.caption if message.content_type == 'photo' else message.text

            data = {
                "message_id": message_id,
                "query": query_text,
            }
            if image_url:  # Add image information if available
                data["image"] = True
                data["image_url"] = image_url

            async with session.post(f"{BASE_API_URL}/conversations/{user_id}", headers=headers, json=data) as response:
                if response.status == 200:
                    async for line in response.content.iter_any():
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line:
                            yield decoded_line
                else:
                    yield "Sorry, there was an error processing your request."


# Function to handle incoming messages
@bot.message_handler(content_types=['text', 'photo'])
def handle_text(message):
    # Detect if the message is a delete message command
    delete_command = message.text.strip() in ['/delete', '/clear'] if message.text else False

    # Determine if the message contains an image and/or caption
    image_url = None
    if message.content_type == 'photo':
        # Get file information of the largest size image
        file_info = bot.get_file(message.photo[-1].file_id)
        image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

    # Asynchronously process the response
    async def process_response():
        last_chunk_received = False
        message_to_update = None
        full_response_text = ""  # Initialize an empty string to store the full response

        async for response in handle_api_request(message, delete=delete_command, image_url=image_url):
            # Append the new chunk to the full response
            formatted_response = escape_markdown(response)
            full_response_text += formatted_response if full_response_text else formatted_response

            if message_to_update:
                # Update the message with the concatenated text
                bot.edit_message_text(chat_id=message.chat.id,
                                      message_id=message_to_update.message_id,
                                      text=full_response_text,
                                      parse_mode='MarkdownV2',
                                      disable_web_page_preview=True)
            else:
                # Send the first chunk as a new message
                message_to_update = bot.send_message(message.chat.id,
                                                     full_response_text,
                                                     parse_mode='MarkdownV2',
                                                     disable_web_page_preview=True)

            if not last_chunk_received:
                bot.send_chat_action(message.chat.id, 'typing')
                last_chunk_received = True

    # Show 'typing' action initially
    bot.send_chat_action(message.chat.id, 'typing')
    asyncio.run(process_response())


if __name__ == '__main__':
    print("Bot started")
    bot.polling(none_stop=True)
