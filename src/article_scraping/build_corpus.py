import json
import requests

from article_scraper import NewsScraper


# Load keys
with open('../../keys.json') as f:
    keys = json.load(f)

NEWS_API_KEY = keys["NEWSAPI_KEY"]
POST_NAME = keys['POST_USERNAME']
POST_PASS = keys["POST_PASSWORD"]

# Pull article info from NewsAPI
url = 'https://newsapi.org/v2/everything?'
parameters = {
    'q': 'election', # query phrase
    'from': '2024-11-15',
    'to': '2024-11-18',
    'apiKey': NEWS_API_KEY,
    'domains':'foxnews.com'
}

response = requests.get(url, params=parameters)