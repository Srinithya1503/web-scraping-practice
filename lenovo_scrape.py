from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
# Headers to prevent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Amazon search URL for Lenovo Laptops with Intel Core i5
URL = "https://www.amazon.in/s?k=lenovo+laptop+with+intel+core+i5"
# HTTP Request
webpage = requests.get(URL, headers=HEADERS)
# Soup Object containing all data
soup = BeautifulSoup(webpage.content, "html.parser")

# Fetch links as List of Tag Objects
links = soup.find_all("a", attrs={'class': 'a-link-normal a-text-normal'})

print(len(links))

   