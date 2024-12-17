# ColBERT Imports
import colbert
from colbert import Indexer, Searcher
from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert.data import Queries, Collection

import pandas as pd
import logging
import re
import subprocess
import sys
import argparse

try:
    from transformers import pipeline
except ImportError:
    print("transformers library not found. Installing it now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])
    from transformers import pipeline   


# SET UP FUNCTION FOR PULLING THE MOST SIMILAR ARTICLES
# Get the index from URL
def get_article_index_by_url(url, metadata):
    for idx, metadata_info in metadata.items():
        if metadata_info['url'] == url:
            return idx
    return None


def pull_similar_articles(user_url):
    # Find the index from URL
    article_index = get_article_index_by_url(user_url, metadata)

    # Function with error handling
    if article_index is not None:
        query = articles[article_index]
        query_metadata = metadata.get(article_index, None)
        print("Showing top 5 most similar articles to: " + query_metadata['titles'])
        print(f"\n")

        # Perform the search to find the top-k passages
        results = searcher.search(query, k=6)
        indices = []
        # Print out the top-5 retrieved passages excluding the first one (result 1)
        for i, (passage_id, passage_rank, passage_score) in enumerate(zip(*results)):
            if i == 0:
                continue

            if passage_id < len(searcher.collection):
                metadata_info = metadata.get(passage_id, None)

                if metadata_info:
                    url = metadata_info['url']
                    title = metadata_info['titles']
                else:
                    url = "URL not found"
                    title = "Title not found"

                print(f"Rank: {passage_rank - 1}")
                print(f"Title: {title}")
                print(f"URL: {url}")
                print(f"Passage ID: {passage_id}")
                indices.append(passage_id)
                print(f"\n")
            else:
                print(f"Warning: Passage ID {passage_id} is out of range for the collection.")
        
        return indices
    else:
        print("No article found for the given URL.")

# Clean text function
def clean_text(text, lowercase=True, remove_punctuation=True):
    """
    Cleans the given text by optionally converting to lowercase and removing punctuation.
    
    Args:
        text (str): Input text to be cleaned.
        lowercase (bool): Whether to convert text to lowercase.
        remove_punctuation (bool): Whether to remove punctuation.
    
    Returns:
        str: Cleaned text.
    """
    if lowercase:
        text = text.lower()
    if remove_punctuation:
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text   

# Function to process specific indices
def process_indices(df, clean_texts, indices, sentiment_pipeline):
    """
    Processes specific indices from a dataframe to output sentiment scores.

    Args:
        df: DataFrame containing 'titles' and 'source'.
        clean_texts: Pre-cleaned text data.
        indices: List of row indices to process.
        sentiment_pipeline (Pipeline): Hugging Face pipeline for sentiment analysis.

    Returns:
        None: Prints results directly.
    """
    for index in indices:
        title = df.iloc[index]['titles']
        source = df.iloc[index]['source']
        text = clean_texts.iloc[index]
        sentiment = sentiment_pipeline(text)[0]
        label = sentiment['label']

        print(f"Title: {title}")
        print(f"Source: {source}")
        print(f"Score: {label}\n")

if __name__ == "__main__":

    # Define the args
    parser = argparse.ArgumentParser(description="Similiar Article Matching with Sentiment Scores Program")
    parser.add_argument("-u", "--url", type=str, default="https://www.aljazeera.com/program/the-stream/2024/11/1/what-issues-are-americans-facing-this-election", help="url to article (default is an Al-Jazeera article)")
    
    # Parse the args
    args = parser.parse_args()


    # Read in all the articles
    article_df = pd.read_csv('src/article_scraping/data/articles_with_text.csv')
    article_df['doc_id'] = range(len(article_df))
    clean_texts = article_df['article_text_raw'].apply(clean_text)

    articles_subset = article_df[['doc_id', 'article_text_raw', 'url', 'titles']]
    articles = articles_subset['article_text_raw'].tolist()
    metadata = articles_subset[['doc_id', 'url', 'titles']].set_index('doc_id').to_dict(orient='index')

    # Define the inputs for the trained model, that are also used in file naming
    nbits = 2   # encode each dimension with 2 bits
    index_name = f'dsan5400_project_nbits={nbits}'

    # SET UP THE COLBERT SEARCHER

    # To create the searcher using its relative name (i.e., not a full path), set
    # experiment=value_used_for_indexing in the RunConfig.
    with Run().context(RunConfig(experiment='DSAN5400')):
        searcher = Searcher(index=index_name, collection=articles)

    # If you want to customize the search latency--quality tradeoff, you can also supply a
    # config=ColBERTConfig(ncells=.., centroid_score_threshold=.., ndocs=..) argument.
    # The default settings with k <= 10 (1, 0.5, 256) gives the fastest search,
    # but you can gain more extensive search by setting larger values of k or
    # manually specifying more conservative ColBERTConfig settings (e.g. (4, 0.4, 4096)).

    # Sentiment analysis pipeline
    pipe2 = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment", truncation=True)      

    similar_indices = pull_similar_articles(args.url)
    process_indices(article_df, clean_texts, similar_indices, pipe2)


