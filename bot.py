import os
import pandas as pd
import pymongo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ContextTypes, ConversationHandler
)
from dotenv import load_dotenv
from db import Database
import openai
import json

# Load environment variables
load_dotenv()

MONGODB_USR = os.getenv("MONGODB_USR")
MONGODB_PWD = os.getenv("MONGODB_PWD")

# Constants for conversation states
START_PAGE, END_PAGE, ENGAGE, COMMENT = range(4)

class LinkedInBot:
    def __init__(self):
        self.application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
        self.target_audience_loaded = False
        self.current_profile_index = 0
        self.profiles = []
        self.comment_flag = False
        # Connect to the MongoDB collection
        self.collection = Database('Communities', 'Github_In_Profile').collection

        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('help', self.help))
        self.application.add_handler(CommandHandler('engage', self.engage))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

        self.application.add_handler(CallbackQueryHandler(self.handle_buttons))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = (
            "Welcome to the LinkedIn Engagement Bot!\n"
            "Run /engage to begin engaging with your leads."
        )
        await update.message.reply_text(message)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = (
            "/start - Start the bot\n"
            "/help - List of commands\n"
            "/engage - Engage with loaded profiles"
        )
        await update.message.reply_text(message)


    async def engage(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

        collection = self.collection
        if collection is None:
            await update.message.reply_text("Failed to retrieve profiles from the database.")
            return

        self.profiles = list(collection.find().limit(20))
        self.current_profile_index = 0
        self.current_post_index = 0

        await self.show_profile(update, context)

    async def show_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        profile = self.profiles[self.current_profile_index]
        keyboard = [
            [InlineKeyboardButton("Prev", callback_data='prev'), InlineKeyboardButton("Next", callback_data='next')],
            [InlineKeyboardButton("Create Comment and Like", callback_data='comment_like')],
            [InlineKeyboardButton("Switch Lead", callback_data='switch_lead')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.message:
            await update.message.reply_text(
                f"{profile['firstName']} {profile['lastName']}" + "\n" +
                f"{profile['headline']}" + "\n" +
                f"Profile URL: \n{profile['profile_url'].split('?')[0]}",
                reply_markup=reply_markup
            )
        else:
            await update.callback_query.message.edit_text(
                f"{profile['firstName']} {profile['lastName']}" + "\n" +
                f"{profile['headline']}" + "\n" +
                f"Profile URL: \n{profile['profile_url'].split('?')[0]}",
                reply_markup=reply_markup
            )

    async def handle_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        if query.data == 'prev':
            self.current_profile_index = max(0, self.current_profile_index - 1)
        elif query.data == 'next':
            self.current_profile_index = min(len(self.profiles) - 1, self.current_profile_index + 1)
        elif query.data == 'comment_like':
            self.comment_flag = True
            await query.message.reply_text("Please write your comment.")
        elif query.data == 'switch_lead':
            self.comment_flag = False

        await self.show_profile(update, context)

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.comment_flag:
            comment_text = update.message.text
            # Use OpenAI API to handle the conversation and submit comments
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Comment on the post: {comment_text}",
                max_tokens=100
            )
            await update.message.reply_text(response.choices[0].text.strip())
            self.comment_flag = False

    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    bot = LinkedInBot()
    bot.run()
