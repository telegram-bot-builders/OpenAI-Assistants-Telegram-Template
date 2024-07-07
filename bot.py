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
from li_scraper import run_linkedin_scraper, get_run_results
from ai import create_new_thread_and_run_initial_analysis, create_message_in_thread, run_message_thread
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
        self.target_audience_loaded = False
        self.current_profile_index = 0
        self.current_post_index = 0
        self.current_thread_id = None
        self.current_run_id = None
        self.profiles = []
        self.current_posts = []
        self.conversing_with_ai = False
        self.database = Database('Communities', 'Luxury_Weddings_ATL_Alpharetta')
        # Connect to the MongoDB collection
        self.collection = self.database.collection

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

        # get the profiles but make sure has_been_engaged_with is False and a limit of 20
        self.profiles = list(collection.find(
            {'has_been_engaged_with': False}
        ).limit(20))
        self.current_profile_index = 0
        self.current_post_index = 0

        await self.show_profile(update, context)

    async def show_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        profile = self.profiles[self.current_profile_index]
        keyboard = []
        if self.conversing_with_ai:
            keyboard = [
                [InlineKeyboardButton("Replied To Post (Tap when true)", callback_data='replied_to_post')],
                [InlineKeyboardButton("Prev Post", callback_data='prev_post'), InlineKeyboardButton("Next Post", callback_data='next_post')],
                [InlineKeyboardButton("Redo Analysis", callback_data='engage_with_post')],
                [InlineKeyboardButton("Prev Lead", callback_data='prev_lead'), InlineKeyboardButton("Next Lead", callback_data='next_lead')],
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Scrape Posts", callback_data='scrape_posts')],
                [InlineKeyboardButton("Prev Post", callback_data='prev_post'), InlineKeyboardButton("Next Post", callback_data='next_post')],
                [InlineKeyboardButton("Engage With Post", callback_data='engage_with_post')],
                [InlineKeyboardButton("Prev Lead", callback_data='prev_lead'), InlineKeyboardButton("Next Lead", callback_data='next_lead')],

            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        post_content = "No posts scraped yet."
        if 'recent_posts_apify_key' in profile:
            self.current_posts = get_run_results(profile['recent_posts_apify_key'])
            if len(self.current_posts) > 0:
                post_content = f"Posted {self.current_posts[self.current_post_index]['timeSincePosted']}: \n{self.current_posts[self.current_post_index]['text']}\n\nURL: \n{self.current_posts[self.current_post_index]['url']}"
        if update.message:
            await update.message.reply_text(
                f"{profile['firstName']} {profile['lastName']}" + "\n" +
                f"Location: {profile['location']}" + "\n" +
                f"{profile['headline']}" + "\n" +
                f"Profile URL: \n{profile['profile_url'].split('?')[0]}" + "\n" +
                f"\nPOST: \n{post_content}",
                reply_markup=reply_markup
            )
        else:
            await update.callback_query.message.edit_text(
                f"{profile['firstName']} {profile['lastName']}" + "\n" +
                f"Location: {profile['location']}" + "\n" +
                f"{profile['headline']}" + "\n" +
                f"Profile URL: \n{profile['profile_url'].split('?')[0]}" + "\n" +
                f"\nPOST: \n{post_content}",
                reply_markup=reply_markup
            )

    async def handle_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        if query.data == 'prev_post':
            self.current_post_index = max(0, self.current_post_index - 1)
        elif query.data == 'next_post':
            self.current_post_index = min(len(self.profiles) - 1, self.current_post_index + 1)
        elif query.data == 'scrape_posts':
            lead_info = self.database.find_lead_by_profile_url(self.profiles[self.current_profile_index]['profile_url'])
            if 'recent_posts_apify_key' in lead_info:
                await query.message.reply_text("Posts already scraped.")
                return
            # Use the LinkedIn scraper to load the recent posts of the current profile
            data_id = run_linkedin_scraper(self.profiles[self.current_profile_index]['profile_url'])
            # save the data_id to the profile
            if self.database.add_recent_posts_apify_key_to_lead(self.profiles[self.current_profile_index]['profile_url'], data_id):
                await query.message.reply_text("We have initiated a bot to scrape the LinkedIn Profile.")
                time.sleep(2)
                await query.message.reply_text("Scraping posts...")
            else:
                await query.message.reply_text("Failed to scrape posts.")
        elif query.data == 'engage_with_post':
            
            # gather the info for create_new_thread_and_run_initial_analysis
            lead = self.profiles[self.current_profile_index]
            post = self.current_posts[self.current_post_index]
            lead_name = f"{lead['firstName']} {lead['lastName']}"
            lead_loc = lead['location']
            lead_headline = lead['headline']
            time_since_posted = post['timeSincePosted']
            post_text = post['text']
            assistant_id = "asst_aCkydg8wjPVbC1TfAiy610Vz"
            # create a new thread and run initial analysis
            message, self.current_thread_id, self.current_run_id = create_new_thread_and_run_initial_analysis(assistant_id, lead_name, lead_loc, lead_headline, time_since_posted, post_text)
            # set the conversing_with_ai flag to True
            self.conversing_with_ai = True
            await query.message.reply_text(message)
        elif query.data == 'prev_lead':
            self.current_profile_index = max(0, self.current_profile_index - 1)
            self.current_post_index = 0
        elif query.data == 'next_lead':
            self.current_profile_index = min(len(self.profiles) - 1, self.current_profile_index + 1)
            self.current_post_index = 0
        elif query.data == 'replied_to_post':
            # update the document in the collection to reflect that the user has replied to a post by the lead
            update_status = self.database.update_lead_engagement_status(self.profiles[self.current_profile_index]['profile_url'], True)
            if update_status:
                await query.message.reply_text("Successfully updated the engagement status.\n\nMoving to the next post by lead...")
                # reset the conversing_with_ai flag to False and increment the current_post_index
                self.conversing_with_ai = False
                self.current_post_index = min(len(self.current_posts) - 1, self.current_post_index + 1)
                time.sleep(2)
            else:
                await query.message.reply_text("Failed to update the engagement status.")
                time.sleep(2)
        try:
            await self.show_profile(update, context)
        except Exception as e:
            print(e)
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if self.conversing_with_ai:
            comment_text = update.message.text
            # Use OpenAI API to handle the conversation and submit comments
            create_message_in_thread(self.current_thread_id, "user", comment_text)
            assistant_id = "asst_aCkydg8wjPVbC1TfAiy610Vz"
            message = run_message_thread(self.current_thread_id, assistant_id)
            await update.message.reply_text(message)
            time.sleep(2)
            await self.show_profile(update, context)

    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    bot = LinkedInBot()
    bot.run()
