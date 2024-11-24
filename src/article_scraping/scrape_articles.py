import time
import json

import pandas as pd

from article_collection import ArticleCollector, ArticleScraper

# Load keys
with open('../../keys.json') as f:
    keys = json.load(f)
    NEWS_API_KEY = keys["NEWSAPI_KEY3"]
    POST_NAME = keys['POST_USERNAME']
    POST_PASS = keys["POST_PASSWORD"]

scraper = ArticleScraper(POST_NAME=POST_NAME, POST_PASS=POST_PASS)

scraper_functions = {'Fox News':scraper.scrape_fox_article,
                     'CNN':scraper.scrape_CNN_article,
                     'Al Jazeera English':scraper.scrape_aljazeera_article,
                     'Washington Post':scraper.scrape_washingtonpost_article,
                     'BBC News':scraper.scrape_bbc_article,
                     'AP News':scraper.scrape_ap_article,
                     }

# Create storage for all our texts
texts = []

# Read in all the articles collected and drop duplicates
articles_df = pd.read_csv('data/corpus_info.csv')
articles_df = articles_df.drop_duplicates(subset=['url'])

# Loop through the articles collected, and scrape them based on the source and url
# Note we do this inefficiently via a for loop over an apply in case things fail during scraping
for i in range(len(articles_df)):
    time.sleep(0.5)

    # Print progress
    if i%100 == 0:
        print(i)

    # Define the source and url from the specific row
    series = articles_df.iloc[i]
    url = series.url
    source = series.source

    # Hold off on scraping Washington Post articles bc they are strange w/ selenium
    if source != 'Washington Post': 
        text = scraper_functions[source](url)
    else:
        text = 'SCRAPE LATER'

    texts.append(text)

# Append the texts to the articles df
articles_df['article_text_raw'] = texts

# Remove the cnn spanish and arabic articles
articles_df = articles_df[articles_df.url.str.contains('espanol') == False]
articles_df = articles_df[articles_df.url.str.contains('arabic') == False]

# Save the df back to machine
articles_df.to_csv('data/articles_with_text.csv', index=False)