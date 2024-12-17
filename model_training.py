# Code adapted from the COLBERT Github Readme

## NOTE: This .py folder can be used for training the ColBert model and searching for 
## similar articles to the corpus, but only if a proper GPU is present. Our team, 
## Due to these contraints used the .ipynb file seen in the same folder on google
## colab to train the model.

## NOTE: BEFORE RUNNING, ENSURE THAT ALL COLBERT COMMANDS FROM README ARE RUN

import os

import pandas as pd
import logging
import sys; sys.path.insert(0, 'ColBERT/')

try: # When on google Colab, let's install all dependencies with pip.
    import google.colab
except Exception:
  import sys; sys.path.insert(0, 'ColBERT/')
  try:
    from colbert import Indexer, Searcher
  except Exception:
    print("If you're running outside Colab, please make sure you install ColBERT in conda following the instructions in our README. You can also install (as above) with pip but it may install slower or less stable faiss or torch dependencies. Conda is recommended.")
    assert False

# ColBERT Imports
import colbert
from colbert import Indexer, Searcher
from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert.data import Queries, Collection

# Read in the article data that we will train ColBert on
article_df = pd.read_csv('articles_with_text.csv')
article_df['doc_id'] = range(len(article_df))

articles_subset = article_df[['doc_id', 'article_text_raw', 'url', 'titles']]
articles = articles_subset['article_text_raw'].tolist()
metadata = articles_subset[['doc_id', 'url', 'titles']].set_index('doc_id').to_dict(orient='index')

# Define the inputs for training the Colbert Checkpoint

nbits = 2   # encode each dimension with 2 bits
doc_maxlen = 300 # truncate passages at 300 tokens

index_name = f'dsan5400_project_nbits={nbits}'

# Train the Colbert Checkpoint
checkpoint = 'colbert-ir/colbertv2.0'

with Run().context(RunConfig(nranks=1, experiment='DSAN5400')):
    config = ColBERTConfig(doc_maxlen=doc_maxlen, nbits=nbits, kmeans_niters=4)
    indexer = Indexer(checkpoint=checkpoint, config=config)
    logging.info(f"Starting indexing process for {len(articles)} articles...")
    indexer.index(name=index_name, collection=articles, overwrite=True)
    logging.info("Indexing complete.")

# CREATE A SEARCHER OBJECT THAT CAN BE USED FOR FINDING SIMILAR ARTICLES
# To create the searcher using its relative name (i.e., not a full path), set
# experiment=value_used_for_indexing in the RunConfig.
with Run().context(RunConfig(experiment='DSAN5400')):
    searcher = Searcher(index=index_name, collection=articles)