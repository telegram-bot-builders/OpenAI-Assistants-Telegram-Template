from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("<YOUR_API_TOKEN>")

# Prepare the Actor input
run_input = {
    "searchUrl": None,
    "deepScrape": True,
    "strictMode": False,
    "startPage": 1,
    "minDelay": 2,
    "maxDelay": 5,
}

# Run the Actor and wait for it to finish
run = client.actor("kfiWbq3boy3dWKbiL").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)