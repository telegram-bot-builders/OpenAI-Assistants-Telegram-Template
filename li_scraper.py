from dotenv import load_dotenv
import os, requests, json
import pprint
load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY")
ACTOR_RUN_URL = f"https://api.apify.com/v2/acts/curious_coder~linkedin-post-search-scraper/runs?token={APIFY_API_KEY}"

def run_linkedin_scraper(profile_url):
    print("Running LinkedIn Scraper")
    print("Profile URL: ", profile_url.split("?")[0])
    # read in cookie from cookie.json
    with open("cookie.json") as f:
        cookie = json.load(f)

    # Prepare the Actor input
    run_input = {
    "cookie": cookie,
    "deepScrape": True,
    "filters.fromMembers": [
        profile_url.split("?")[0]
    ],
    "maxDelay": 60,
    "minDelay": 15,
    "startPage": 1,
    "endPage": 1,
    "strictMode": False,
    }
    response = requests.post(ACTOR_RUN_URL, json=run_input)
    data = response.json()
    return data["data"]["defaultDatasetId"]
    

def get_run_results(dataset_id):
    ACTOR_GET_RUN_URL = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_API_KEY}"
    response = requests.get(ACTOR_GET_RUN_URL)
    data = response.json()
    # data is a list of objects. extract from each object the url, text, timeSincePosted and return that object
    extracted_data = []
    for item in data:
        extracted_item = {
            "url": item["url"],
            "text": item["text"],
            "timeSincePosted": item["timeSincePosted"]
        }
        extracted_data.append(extracted_item)
    
    return extracted_data

if __name__ == "__main__":
    pprint.pprint(get_run_results("ed29KDzMpkOznXPRH"))