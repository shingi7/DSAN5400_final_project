import requests
import time
import json

import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ArticleCollector():
    def __init__(self, API_KEY, urls=None, titles=None, descriptions=None,
                 dates=None, sources=None):
        
        self.API_KEY = API_KEY
        self.urls = urls
        self.titles = titles
        self.descriptions = descriptions
        self.dates = dates
        self.sources = sources

    def _collect_urls(self):
        '''Internal function used to collect all article URLs from a NewsAPI pull'''
        # Make a list of the URLs from the pull
        urls = [article['url'] for article in self.articles]

        # Add to the current list of URLs if it exists, or create a new list if not
        if self.urls:
            self.urls = self.urls + urls
        else:
            self.urls = urls

    def _collect_descriptions(self):
        '''Internal function used to collect all article descriptions from a NewsAPI pull'''
        # Make a list of the Descriptions from the pull
        descriptions = [article['description'] for article in self.articles]

        # Add to the current list of descriptions if it exists, or create a new list if not
        if self.descriptions:
            self.descriptions = self.descriptions + descriptions
        else:
            self.descriptions = descriptions
    
    def _collect_titles(self):
        '''Internal function used to collect all article titles from a NewsAPI pull'''
        # Make a list of the titles from the pull
        titles = [article['title'] for article in self.articles]

        # Add to the current list of descriptions if it exists, or create a new list if not
        if self.titles:
            self.titles = self.titles + titles
        else:
            self.titles = titles

    def _collect_publishing_dates(self):
        '''Internal function used to collect all article publishing dates from a NewsAPI pull'''
        # Make a list of the dates from the pull
        publishing_dates = [article['publishedAt'] for article in self.articles]

        # Add to the current list of descriptions if it exists, or create a new list if not
        if self.dates:
            self.dates = self.dates + publishing_dates
        else:
            self.dates = publishing_dates

    def _collect_sources(self):
        '''Internal function used to collect all article publishing sources from a NewsAPI pull'''
        # Make a list of the dates from the pull
        sources = [article['source']['name'] for article in self.articles]

        # Add to the current list of descriptions if it exists, or create a new list if not
        if self.sources:
            self.sources = self.sources + sources
        else:
            self.sources = sources

    def make_api_call(self, keyword, start_date, end_date, domain, page=1):
        '''Function for pulling articles from NewsAPI given specific inputs for the request, and returns the urls returned'''
        # Define the base URL and Parameters for the request
        url = 'https://newsapi.org/v2/everything?'
        parameters = {
            'q': keyword, 
            'from': start_date,
            'to': end_date,
            'apiKey': self.API_KEY,
            'domains':domain,
            'page':page
        }

        # Make the API call
        response = requests.get(url, params=parameters)

        # Ensure a valid response
        if response.status_code == 200:
            # Save the API response and the article information
            total_response = response.json()
            self.api_response = total_response

            articles = total_response['articles']
            self.articles = articles

            # Save all the information from the API call
            self._collect_urls()
            self._collect_titles()
            self._collect_descriptions()
            self._collect_publishing_dates()
            self._collect_sources()          

        else:
            print("Failed to pull a valid response from the NewsAPI. Check inputs")

    def make_article_df(self):
        '''Converts all the article information stored in the class instance and converts to a DataFrame for returning'''
        df = pd.DataFrame({
            'url':self.urls,
            'titles':self.titles,
            'descriptions':self.descriptions,
            'publishing_date':self.dates,
            'source':self.sources
        })

        self.df = df
        return df
         


class ArticleScraper():
    '''A class to scrape article text from different mainstream political news websites.'''
    
    def __init__(self):
        pass

    def _make_soup(self, url):
        # Get the HTML Soup from the url via a GET request
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        return soup


    def scrape_fox_article(self, url):
        '''Scrapes article text from foxnews.com given a url'''
    
        soup = self._make_soup(url)
        
        # Filter down to just the article body
        article_body = soup.find('div', {'class':'article-body'})

        if article_body:
            # Segment by paragraph
            paragraphs = article_body.find_all('p')

            # Loop through each paragraph
            for para in paragraphs:
                # There are in text ads and other non article related objects that we can remove with .decompose()
                for span in para.find_all('span'):
                    span.decompose()
                for span in para.find_all('strong'):
                    span.decompose()
                for i in para.find_all('i'):
                    i.decompose()
                for d in para.find_all('div', {'class':'info'}):
                    d.decompose()


            # Combine all our article related objects into one text and return. here we also filter out all caps paragraphs
            # Which never actually belong to the article text.
            full_article_text = '\n'.join([para.text for para in paragraphs if para.text.upper() != para.text])

            return full_article_text
        
        else:
            print("The given URL is not connecting to an article. Double check the URL and inspect the page if necessary.")
            return None

    def scrape_CNN_article(self, url):
        '''Scrapes article text from cnn.com given a url'''

        soup = self._make_soup(url)

        # Filter down to just the article body
        article_body = soup.find('div', {'class':'article__content-container'})

        if article_body:
            # Segment by paragraph
            paragraphs = article_body.find_all('p', {'data-editable':'text'})

            # Rebuild the article from the paragraphs
            full_article_text = '\n'.join([' '.join(para.text.split()) for para in paragraphs])

            # Remove common finishers that sometimes but dont always appear
            finishers = ['This story has been updated with additional information.']

            for finisher in finishers:
                full_article_text = full_article_text.replace(finisher, '')

            return full_article_text
        
        else:
            print("The given URL is not connecting to an article. Double check the URL and inspect the page if necessary.")

    
    def scrape_washingtonpost_article(self, url, POST_NAME, POST_PASS):
        '''Scrapes article text from Washingtonpost.com using Selenium to log in'''
        try: # Fails if login is required
            # Get the HTML Soup from the url via a GET request, including a timeout
            response = requests.get(url, timeout=3)
            html_content = response.text

        except requests.exceptions.Timeout:
            # We need to log in to Washington Post, so we provide our cookies
            driver = webdriver.Chrome()
            driver.get(url)
            
            # Click on the sign in button
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@data-qa='sc-account-button']"))
            ).click()

            # Insert email username
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            ).send_keys(POST_NAME)

            # Click on next button to get to password
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@data-test-id='sign-in-btn']"))
            ).click()

            # Insert password
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='password']"))
            ).send_keys(POST_PASS)

            # Click to sign in
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@data-test-id='sign-in-btn']"))
            ).click()
            
            time.sleep(5)
            html_content = driver.page_source

        soup = BeautifulSoup(html_content, 'html.parser')

        # Filter down to just the article body
        article_body = soup.find('div', {'class':'meteredContent grid-center'})

        if article_body:
            # Segment by paragraph
            paragraphs = article_body.find_all('p', {'data-el':'text'})

            # Rebuild the article from the paragraphs
            full_article_text = '\n'.join([' '.join(para.text.split()) for para in paragraphs])

            return full_article_text
        
        else:
            print("The given URL is not connecting to an article. Double check the URL and inspect the page if necessary.")
            print(url)
            return None

    def scrape_breitbart(self, url):
        '''Scrapes article text from breitbart.com'''
        soup = self._make_soup(url)

        # Filter down to just the article body
        article_body = soup.find('div', {'class':'entry-content'})    

        if article_body:
            # Segment by paragraph
            paragraphs = article_body.find_all('p')

            # Rebuild the article from the paragraphs
            full_article_text = '\n'.join([''.join(para.text) for para in paragraphs])

            return full_article_text
        
        else:
            print("The given URL is not connecting to an article. Double check the URL and inspect the page if necessary.")
            print(url)
            return None
        
    def scrape_bbc_article(self, url):
        '''scrapes article text from bbc.com'''
        soup = self._make_soup(url)

        # Filter down to just the article body
        article_body = soup.find('article')

        if article_body:
            # Segment by paragraph
            paragraphs = article_body.find_all('p')

            # Rebuild the article from the paragraphs
            full_article_text = '\n'.join([''.join(para.text) for para in paragraphs])

            return full_article_text
        
        else:
            print("The given URL is not connecting to an article. Double check the URL and inspect the page if necessary.")
            print(url)
            return None
        
    def scrape_reuters_article(self, url):
        '''REUTERS KEEPS THROWING CAPCHA TESTS AT SELENIUM AND IS UNHAPPY WITH SCRAPING, MIGHT NOT BE ABLE TO SCRAPE WITHOUT
           MORE COMPLICATED MEASURES'''
        
        # Reuters loads with javascript, so we use selenium to scrape 
        driver = webdriver.Chrome()
        driver.get(url)

        # Wait for the page to load
        time.sleep(3)
        # WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.XPATH, "//*[@data-testid='ArticleBody']"))
        #     )
        
        # Collect the HTML
        html_content = driver.page_source

        # And convert to soup as usual
        soup = BeautifulSoup(html_content, 'html.parser')


        # Filter down to just the article body
        article_body = soup.find('div', {'data-testid':'ArticleBody'})
        print(soup)

        if article_body:
            # Segment by paragraph
            paragraphs = article_body.find_all('div', {'data-testid':lambda x: 'paragraph-' in x})

            # Rebuild the article from the paragraphs
            full_article_text = '\n'.join([''.join(para.text) for para in paragraphs])

            return full_article_text
        
        else:
            print("The given URL is not connecting to an article. Double check the URL and inspect the page if necessary.")
            print(url)
            return None
        
    def scrape_ap_article(self, url):
        '''scrapes article text from apnews.com'''
         # Get the HTML Soup from the url via a GET request
        soup = self._make_soup(url)

        # Filter down to just the article body
        article_body = soup.find('div', {'class':'RichTextStoryBody RichTextBody'})

        if article_body:
            # Segment by paragraph
            paragraphs = article_body.find_all('p')

            # Rebuild the article from the paragraphs
            full_article_text = '\n'.join([''.join(para.text) for para in paragraphs])

            return full_article_text
        
        else:
            print("The given URL is not connecting to an article. Double check the URL and inspect the page if necessary.")
            print(url)
            return None
        
    def scrape_politico_article(self, url):
        '''scrapes article text from politico using selenium to accept privacy agreement'''
        # Page loads with JS, so use selenium again
        driver = webdriver.Chrome()
        driver.get(url)

        # click the agree to privacy terms button if it appears
        try:
            WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@title='Agree']"))
            ).click()
        except:
            WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@class='sidebar-grid__container']"))
            )

        # Collect the HTML
        html_content = driver.page_source
        
        # And convert to soup as usual
        soup = BeautifulSoup(html_content, 'html.parser')

        # Segment by paragraph. We do not filter to the article body, as it is split into multiple
        # pieces in the HTML, and the paragraphs are unique in their class name
        paragraphs = soup.find_all('div', {'class':'sidebar-grid__content article__content'})

        # Rebuild the article from the paragraphs
        full_article_text = '\n'.join([''.join(para.text) for para in paragraphs])

        return full_article_text
        
            
        
            



            