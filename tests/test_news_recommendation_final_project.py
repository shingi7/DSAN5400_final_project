import pandas as pd
import re
import subprocess
import sys

try:
    from transformers import pipeline
except ImportError:
    print("transformers library not found. Installing it now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers"])
    from transformers import pipeline

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

# Sentiment analysis pipeline
pipe2 = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment", truncation=True)     

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
    scores = []
    for index in indices:
        title = df.iloc[index]['titles']
        source = df.iloc[index]['source']
        text = clean_texts.iloc[index]
        sentiment = sentiment_pipeline(text)[0]
        label = sentiment['label']

        # print(f"Title: {title}")
        # print(f"Source: {source}")
        # print(f"Score: {label}\n")
        scores.append(label)
    return scores

# Example usage
def test_scores():
    # Load DataFrame
    df = pd.read_csv("src/article_scraping/data/articles_with_text.csv")

    clean_texts = df['article_text_raw'].apply(clean_text)

    # Sample indices for testing
    tests = pd.read_csv("tests/indices_test.csv")
    indices = tests['index_1'].to_list()

    scores = process_indices(df, clean_texts, indices, pipe2)

    assert(scores[0] == scores[1])


