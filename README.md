# LinkedIn Lead Engagement Telegram Bo## Purpose

The LinkedIn Lead Engagement Telegram Bot is designed to streamline the process of engaging with targeted LinkedIn leads. By leveraging a database of pre-scraped LinkedIn profiles, this bot enables users to efficiently cycle through leads and generate meaningful comments and messages using the OpenAI Assistants API. This tool is ideal for professionals looking to enhance their LinkedIn engagement strategy and drive higher levels of interaction and connection with potential clients or partners.

## Benefits

1. **Efficiency**: Automate the process of engaging with LinkedIn leads, saving time and effort.
2. **Consistency**: Ensure consistent and professional communication with leads using AI-generated comments.
3. **Scalability**: Easily manage and engage with a large number of leads with AI intervention.
4. **Personalization**: Tailor interactions based on lead data, increasing the chances of meaningful connections.
5. **Integration**: Seamlessly integrates with Telegram for a user-friendly experience.

## Current Features

- Load targeted LinkedIn leads from a database.
- Cycle through leads to review and engage with them.
- Generate comments and messages using the OpenAI Assistants API.

## Planned Features

- Send comments directly through Telegram.
- Track engagement and responses.

## Installation and Running Instructions

### Prerequisites

- Python 3.7+
- Telegram Bot API Token
- OpenAI API Key
- MongoDB Database with LinkedIn Leads

### Steps

1. **Clone the Repository**

   ```sh
   git clone https://github.com/telegram-bot-builders/LinkedIn-GenAI-Engagement-Bot.git ttb-engagement-bot
   cd tbb-engagement-bot
   ```

2. **Install Dependencies**

   Ensure you have `pip` installed. Run the following command to install required packages:

   ```sh
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**

   Create a `.env` file in the root directory of the project and add the following variables:

   ```env
   TELEGRAM_API_TOKEN=<your-telegram-bot-api-token>
   OPENAI_API_KEY=<your-openai-api-key>
   MONGODB_USR=<your-mongodb-username>
   MONGODB_PWD=<your-mongodb-pwd>
   APIFY_API_KEY=<your-apify-api-key>
   ```

4. **Setup Database**

   Ensure your SQLite database with LinkedIn leads is correctly set up. The database should have a table with the necessary fields for storing lead information.

5. **Run the Bot**

   Execute the bot by running the following command:

   ```sh
   python bot.py
   ```

6. **Interacting with the Bot**

   Open your Telegram app and start a conversation with your bot. Use the provided commands to start cycling through leads and generating comments.

### File Overview

- **ai.py**: Contains the integration with the OpenAI Assistants API for generating comments and messages.
- **bot.py**: Main bot script that handles interaction with Telegram and orchestrates the flow.
- **db.py**: Database interaction layer for fetching and updating LinkedIn leads.
- **li_scraper.py**: (Optional) Script for scraping LinkedIn profiles and populating the database.
- **utils.py**: Utility functions used across the bot.

### Commands

- `/start`: Initializes the bot and provides initial instructions.
- `/engage`: Begins engaging with the leads
- `/help`: Displays help information and available commands.
