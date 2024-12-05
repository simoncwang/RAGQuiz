# Web Scraping following tutorial from 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager
from openai import OpenAI
import shutil
import os
from selenium.webdriver.common.by import By

# Obtain the version of ChromeDriver compatible with the browser being used
options = Options()
options.add_argument("--headless")
driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrapeURL(link):
    # use selenium to scrape the url provided
    wait = WebDriverWait(driver, 10)
    driver.get(link)

    # get_url = driver.current_url
    # wait.until(EC.url_to_be(link))

    # if get_url == link:
    #     page_source = driver.page_source

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    page_source = driver.page_source

    # use BeautifulSoup to parse the html content
    soup = BeautifulSoup(page_source,features="html.parser")
    return soup.get_text()
