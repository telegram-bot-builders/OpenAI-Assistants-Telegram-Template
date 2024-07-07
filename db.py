from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.user_table = database
        self.client = self._connect_to_server()
        self.collection = self._connect_to_database()

    def _connect_to_server(self):
        MONGODB_PWD = os.getenv('MONGODB_PWD')
        MONGODB_USER = os.getenv('MONGODB_USR')
        uri = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PWD}@cluster0.gzf2exs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        return MongoClient(uri, server_api=ServerApi('1'))
    
    def _connect_to_database(self):
        db = self.client[self.database]
        return db[self.table]

    def upload_new_community(self, csv_file_path, collection_name):
        try:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(csv_file_path)

            # Create the collection or clear existing documents if the collection exists
            collection = self.client[self.database][collection_name]
            collection.delete_many({})  # Clear existing documents

            # Prepare the documents to be inserted
            documents = df.apply(lambda row: {
                'profile_url': row['profileUrl'],
                'firstName': row['firstName'],
                'lastName': row['lastName'],
                'headline': row['headline'],
                'location': row['location'],
                'has_been_engaged_with': False,
                'last_post_engaged_with_url': None
            }, axis=1).to_list()

            # Insert the documents into the collection
            collection.insert_many(documents)
            print(f"Uploaded {len(documents)} profiles to the collection '{collection_name}'.")

        except FileNotFoundError:
            print(f"Error: The file '{csv_file_path}' was not found.")
        except pd.errors.EmptyDataError:
            print("Error: The CSV file is empty.")
        except pd.errors.ParserError:
            print("Error: The CSV file could not be parsed.")
        except pymongo.errors.PyMongoError as e:
            print(f"Error: An error occurred while interacting with MongoDB: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # method that finds a document in the collection by the profile_url, and adds a list of recent posts
    def add_recent_posts_apify_key_to_lead(self, profile_url, recent_posts_apify_key):
        # Find the document by the profile_url using error handling
        try:
            document = self.collection.find_one({'profile_url': profile_url})
            if document is None:
                raise ValueError(f"Error: No document found with the profile_url '{profile_url}'.")

            # Update the document with the recent posts
            self.collection.update_one({'profile_url': profile_url}, {'$set': {'recent_posts_apify_key': recent_posts_apify_key}})
            print(f"Added recent posts to the document with the profile_url '{profile_url}'.")
            return True

        except pymongo.errors.PyMongoError as e:
            print(f"Error: An error occurred while interacting with MongoDB: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
        
    # method that finds a document in the collection by the profile_url and returns the document
    def find_lead_by_profile_url(self, profile_url):
        try:
            document = self.collection.find_one({'profile_url': profile_url})
            if document is None:
                raise ValueError(f"Error: No document found with the profile_url '{profile_url}'.")
            return document

        except pymongo.errors.PyMongoError as e:
            print(f"Error: An error occurred while interacting with MongoDB: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    # method that finds a document in the collection by the profile_url and updates the has_been_engaged_with to True
    def update_lead_engagement_status(self, profile_url, status=True):
        try:
            document = self.collection.find_one({'profile_url': profile_url})
            if document is None:
                raise ValueError(f"Error: No document found with the profile_url '{profile_url}'.")

            # Update the document with the recent posts
            self.collection.update_one({'profile_url': profile_url}, {'$set': {'has_been_engaged_with': status}})
            print(f"Updated the engagement status of the document with the profile_url '{profile_url}'.")
            return True

        except pymongo.errors.PyMongoError as e:
            print(f"Error: An error occurred while interacting with MongoDB: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

if __name__ == '__main__':
    _db = Database("Communities", "Luxury_Weddings_ATL_Alpharetta")

    try:
        _db.client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        # upload a new community with the command below
        _db.upload_new_community('linkedin-CYL-Luxury-Weddings-ATL-Alpharetta.csv', 'Luxury_Weddings_ATL_Alpharetta')
    except Exception as e:
        print(e)
        pass