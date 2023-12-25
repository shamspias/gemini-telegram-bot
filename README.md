# Gemini Telegram Bot

## Overview

Gemini Telegram Bot is crafted in Python, leveraging the `telebot` library for Telegram interactions, `aiohttp` for
asynchronous API communication, and `dotenv` for efficient environment variable management. It's designed to process
both text and image messages, offering Markdown formatted responses and efficient API communication for varied
functionalities.

## Requirements

- Python 3.x
- `telebot` library
- `aiohttp` library
- `python-dotenv` library

## Installation

1. Clone the repository or download the Gemini Bot code.
2. Install the required packages:
   ```
   pip install pyTelegramBotAPI aiohttp python-dotenv
   ```
3. Create a `.env` file containing your Telegram bot token (`TELEGRAM_BOT_TOKEN`), the base API URL (`BASE_API_URL`),
   and the API key (`API_KEY`).

## Usage

1. Launch the bot:
   ```
   python main.py
   ```
2. Engage with the bot on Telegram by sending either text or photo messages.

## Features

- Processes both text and photo messages.
- Supports Markdown for enhanced message presentation.
- Asynchronous handling of API requests for smooth operation.
- Customizable API integration for a range of functionalities.
- Special command recognition (e.g., `/delete`, `/clear`).

## Note

For optimal functionality, ensure a valid Telegram bot token and a properly configured API service.

## API Code
- [Langchain Gemini API](https://github.com/shamspias/langchain-gemini-api)