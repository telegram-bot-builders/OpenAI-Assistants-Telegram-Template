from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        self.user_table = "Users"
        self.client = self._connect_to_server()
        self.collection = self._connect_to_database()

    def _connect_to_server(self):
        MONGODB_PWD = os.getenv('MONGODB_PWD')
        MONGODB_USER = os.getenv('MONGODB_USR')
        uri = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PWD}@cluster0.gzf2exs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        return MongoClient(uri, server_api=ServerApi('1'))
    
    def _connect_to_database(self):
        db = self.client[self.user_table]
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

    
            

_db = Database("Communities", "Github_In_Profile")

if __name__ == '__main__':
    try:
        _db.client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        # upload a new community with the command below
        _db.upload_new_community('linkedin-people-search-scraper_5.csv', 'Github_In_Profile')
    except Exception as e:
        print(e)
        pass