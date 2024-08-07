import os
import pandas as pd
import pymongo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ContextTypes, ConversationHandler
)
from dotenv import load_dotenv
from db import Database
from utils import escape_markdown_v2
from ai import create_new_thread_and_run, create_message_in_thread, run_message_thread
import openai
import json, time


# Load environment variables
load_dotenv()

MONGODB_USR = os.getenv("MONGODB_USR")
MONGODB_PWD = os.getenv("MONGODB_PWD")

# Constants for conversation states
START_PAGE, END_PAGE, ENGAGE, COMMENT = range(4)

class LinkedInBot:
    def __init__(self):
        self.application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
        print("Bot initialized.")
        self.current_thread_id = None
        self.current_run_id = None
        self.profiles = []
        self.conversing_with_ai = False
        self.database = Database('Communities', 'Acct_Execs_Connected')
        # Connect to the MongoDB collection
        self.collection = self.database.collection

        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('help', self.help))
        self.application.add_handler(CommandHandler('engage', self.engage))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = (
            "Run /engage to begin engaging with your leads."
        )
        await update.message.reply_text(message)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = (
            "/start - Start the bot\n"
            "/help - List of commands\n"
            "/engage - Engage with AI"
        )
        await update.message.reply_text(message)


    async def engage(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Begin chatting with AI")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        assistant_id = "asst_wkqXfyEb0cArvqZsyumlmvoY"
        if self.conversing_with_ai:
            comment_text = update.message.text
            # Use OpenAI API to handle the conversation and submit comments
            create_message_in_thread(self.current_thread_id, "user", comment_text)
            message = run_message_thread(self.current_thread_id, assistant_id)
            await update.message.reply_text(text=f'\n\n{escape_markdown_v2(message)}\n\n', parse_mode=ParseMode.MARKDOWN_V2)
            time.sleep(2)
        else:
            msg = update.message.text
            self.conversing_with_ai = True
            data = create_new_thread_and_run(assistant_id, msg)
            self.current_thread_id = data[1]
            resp_msg = data[0]
            await update.message.reply_text(resp_msg)




    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    bot = LinkedInBot()
    bot.run()
