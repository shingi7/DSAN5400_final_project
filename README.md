# news_recommendation_final_project

A project for creating and offering news article recommendations to broaden readers' universe of news media. The project pulls from a variety of news sources and implements ColBERT to analyze text similarity between an input article and the collected corpus of articles. Once an article is input, the 5 most similar articles (scored by ColBERT) are returned with titles, source, and URL. These articles are also analyzed using a BERT sentiment model and are given a sentiment score 1-5 (5 being the most postiive). These article recommendations and sentiment scores are intended to be a great way to broaden a user's exposure to different outlets. Reading similar articles with a different sentiment than the input help show differing opinions on a specific topic of interest.

## Installation

**NOTE: BEFORE RUNNING, ENSURE THAT ALL COLBERT DATA AND CHECKPOINTS ARE SUCCESFULLY INSTALLED**

To do so, copy and paste **in the terminal** the following lines:

```
!git -C ColBERT/ pull || git clone https://github.com/stanford-futuredata/ColBERT.git > /dev/null 2>&1
!wget "https://downloads.cs.stanford.edu/nlp/data/colbert/colbertv2/colbertv2.0.tar.gz"
!mkdir -p checkpoints  # Create the 'checkpoints' directory if it doesn't exist
!tar -xvzf colbertv2.0.tar.gz -C checkpoints
!pip install -U pip > /dev/null 2>&1
!pip install fsspec==2024.9.0 > /dev/null 2>&1
!pip install -e ColBert/['faiss-gpu','torch'] > /dev/null 2>&1
!pip install --upgrade torch torchvision torchaudtio > /dev/null 2>&1
```

```bash
pip install news_recommendation_final_project
```

## Usage

- TODO

## Contributing

Clone and set up the repository with

```bash
git clone TODO && cd news_recommendation_final_project
pip install -e ".[dev]"
```

Install pre-commit hooks with

```bash
pre-commit install
```

Run tests using

```
pytest -v tests
```

