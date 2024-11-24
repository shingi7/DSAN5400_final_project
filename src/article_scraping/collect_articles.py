import json
import requests

from article_collection import ArticleCollector

# Load keys
with open('../../keys.json') as f:
    keys = json.load(f)
NEWS_API_KEY = keys["NEWSAPI_KEY3"]
POST_NAME = keys['POST_USERNAME']
POST_PASS = keys["POST_PASSWORD"]

# Define function inputs
keywords = ['election', 'government', 'economy', 'trump', 'kamala']
pages = [n for n in range(1, 6)]
domains = ['aljazeera.com', 'washingtonpost.com','foxnews.com',
           'bbc.co.uk', 'cnn.com', 'breitbart.com', 'cnn.com']


# Create the collection object
collector = ArticleCollector(API_KEY=NEWS_API_KEY)

# ### PULL THE MAJORITY OF ARTICLES FROM NEWSAPI ###

# # Loop through the input combinations, collecting article info on each, and stopping 
# # if no further articles are found
# for domain in domains:
#     for keyword in keywords:
#         stories_collected = 0
#         for page in pages:

#             # Check how many stories have been collected
#             if collector.urls:
#                 stories_collected = len(collector.urls)
            
#             collector.make_api_call(keyword=keyword,
#                                     start_date='2024-11-23',
#                                     end_date='2024-10-25',
#                                     domain=domain,
#                                     page=page)
            
#             # If no more stories were collected on the most recent call, break to the next keyword
#             if len(collector.urls) == stories_collected:
#                 break


# ### FOLLOW UP WITH WASHINGTON POST ARTICLE COLLECTION ###
# collector.scrape_wpost('data/wpost.html')

### FOLLOW UP WITH AP ARTICLE COLLECTION ###
collector.scrape_ap('data/AP.html')



### FINISH BY BUILDING AND SAVING THE DATAFRAME OF ARTICLES ###
collector.make_article_df(save=True)











