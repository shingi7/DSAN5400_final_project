import json
import requests

from article_collection import ArticleCollector, ArticleScraper

# Load keys
with open('../../keys.json') as f:
    keys = json.load(f)
NEWS_API_KEY = keys["NEWSAPI_KEY2"]
POST_NAME = keys['POST_USERNAME']
POST_PASS = keys["POST_PASSWORD"]

# Define function inputs
keywords = ['election', 'government', 'economy', 'trump', 'kamala']
pages = [n for n in range(1, 6)]
domains = ['apnews.com', 'politico.com', 'aljazeera.com']

finished_sites = ['washingtonpost.com','foxnews.com', 'bbc.co.uk', 'cnn.com', 'breitbart.com', 'apnews.com']


# Create the collection object
collector = ArticleCollector(API_KEY=NEWS_API_KEY)

# Loop through the input combinations, collecting article info on each, and stopping 
# if no further articles are found
for domain in domains:
    for keyword in keywords:
        stories_collected = 0
        for page in pages:

            # Check how many stories have been collected
            if collector.urls:
                stories_collected = len(collector.urls)
            
            collector.make_api_call(keyword=keyword,
                                    start_date='2024-11-23',
                                    end_date='2024-10-25',
                                    domain=domain,
                                    page=1)
            
            # If no more stories were collected on the most recent call, break to the next keyword
            if len(collector.urls) == stories_collected:
                break

# Make a df from the collected results and save to our data folder
collector.make_article_df(save=True)











