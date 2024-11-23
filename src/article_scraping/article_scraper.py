import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


post_name = 'INSERT USERNAME'
post_pass = 'INSERT PASSWORD'


class NewsScraper():
    '''A class to scrape article text from different mainstream political news websites.'''
    
    def __init__(self):
        pass

    def _make_soup(url):
        # Get the HTML Soup from the url via a GET request
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        return soup


    def scrape_fox_article(self, url):
        '''Scrapes article text from foxnews.com given a url'''
    
        soup = _make_soup(url)
        
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

        soup = _make_soup(url)

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

    
    def scrape_washingtonpost_article(self, url):
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
            ).send_keys(post_name)

            # Click on next button to get to password
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@data-test-id='sign-in-btn']"))
            ).click()

            # Insert password
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='password']"))
            ).send_keys(post_pass)

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
        soup = _make_soup(url)

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
        soup = _make_soup(url)

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
        soup = _make_soup(url)

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
        
            
        
            



            