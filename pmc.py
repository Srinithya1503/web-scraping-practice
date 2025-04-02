import requests
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Base URL for PMC search
BASE_URL = "https://www.ncbi.nlm.nih.gov/pmc"
QUERY = "(myxobacteria) AND genome"
SEARCH_URL = f"{BASE_URL}/?term={quote(QUERY)}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Store extracted data
articles_data = {"PMCID": [], "Title": [], "Authors": [], "DOI": [], "Article_Link": [], "Abstract": []}

def extract_articles(driver, page_num):
    """Extracts articles from a PMC search result page using Selenium."""
    print(f"🔍 Fetching Page {page_num}...")

    try:
        # Wait for the results to load (adjust timeout as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rslt"))
        )

        # Extract the HTML source
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        articles = soup.find_all("div", class_="rslt")
        if not articles:
            print("No articles found on this page.")
            return False  # No more pages

        for article in articles:
            try:
                # Extract PMCID
                pmcid_tag = article.find("dd")
                pmcid = pmcid_tag.text.strip() if pmcid_tag else "No PMCID"

                # Extract Title & Article Link
                title_tag = article.find("div", class_="title").find("a")
                title = title_tag.text.strip() if title_tag else "No Title Found"
                article_link = urljoin(BASE_URL, title_tag["href"]) if title_tag else "No Link"

                # Extract Authors
                authors_tag = article.find("div", class_="desc")
                authors = authors_tag.text.strip() if authors_tag else "No Authors Found"

                # Extract DOI
                doi_tag = article.find("span", class_="doi")
                doi = doi_tag.text.replace("doi: ", "").strip() if doi_tag else "No DOI Found"

                # Fetch the article page to get the abstract
                article_response = requests.get(article_link, headers=HEADERS)
                article_response.raise_for_status()
                article_soup = BeautifulSoup(article_response.text, "html.parser")

                # Extract Abstract
                abstract_section = article_soup.find("section", class_="abstract") or \
                                   article_soup.find("div", class_="abstr") or \
                                   article_soup.find("div", class_="abstract")
                abstract_text = " ".join(p.text.strip() for p in abstract_section.find_all(["p", "div"])) if abstract_section else "No Abstract Found"

                # Store data
                articles_data["PMCID"].append(pmcid)
                articles_data["Title"].append(title)
                articles_data["Authors"].append(authors)
                articles_data["DOI"].append(doi)
                articles_data["Article_Link"].append(article_link)
                articles_data["Abstract"].append(abstract_text)

                print(f"Scraped: {title}")  # Full title displayed
                
                time.sleep(random.uniform(1, 3))  # Randomized sleep to avoid blocking

            except Exception as e:
                print(f"Error scraping article: {e}")

        return True  # More pages might exist

    except Exception as e:
        print(f"Error extracting articles: {e}")
        return False

# Set up Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode

# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get(SEARCH_URL)
    page_num = 1
    
    while page_num <= 50:  # Limit to 2 pages for testing
        if not extract_articles(driver, page_num):
            break

        try:
            # Find and click the "Next" button
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "next"))
            )
            next_button.click()
            page_num += 1
            time.sleep(random.uniform(2, 4))  # Wait for the next page to load

        except Exception as e:
            print(f"No more 'Next' button found: {e}")
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Save data to Excel
    df = pd.DataFrame(articles_data)
    df.to_excel("pmc_myxobacteria_aricles_50_pages.xlsx", index=False, engine="openpyxl")
    print("\n✅ Data saved to pmc_myxobacteria_articles_50_pages.xlsx")
    driver.quit()  # Close the browser window
