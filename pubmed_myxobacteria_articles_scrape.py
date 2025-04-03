from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Initialize WebDriver
driver = webdriver.Chrome()
driver.maximize_window()

search_url = "https://pubmed.ncbi.nlm.nih.gov/?term=myxobacteria+genome&sort=date&size=200"
driver.get(search_url)
time.sleep(5)

articles_data = {"PMID": [], "Title": [], "Authors": [], "Journal": [], "DOI": [], "Article_Link": [], "Abstract": []}

page_num = 1
max_pages = 2  # Limiting to the first two pages

while page_num <= max_pages:
    print(f"\nScraping page {page_num}...\n")

    # Wait for articles to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "docsum-wrap")))
    articles = driver.find_elements(By.CLASS_NAME, "docsum-wrap")

    if not articles:
        print("No articles found on this page!")
        break

    total_articles = len(articles)
    print(f"Found {total_articles} articles on page {page_num}.")

    for index in range(total_articles):
        try:
            # Refresh article elements to avoid stale references
            articles = driver.find_elements(By.CLASS_NAME, "docsum-wrap")
            if index >= len(articles):
                print(f"Skipping article {index + 1}, it no longer exists.")
                continue

            article = articles[index]

            # Extract Title & Article Link
            title_tag = article.find_element(By.CLASS_NAME, "docsum-title")
            title = title_tag.text.strip()

            # Get href attribute and check if it's a relative or absolute URL
            href = title_tag.get_attribute("href")
            if href.startswith("/"):  # Relative path
                article_link = "https://pubmed.ncbi.nlm.nih.gov" + href
            else:  # Absolute URL
                article_link = href

            print(f"Article link: {article_link}")

            # Extract PMID
            pmid_element = article.find_elements(By.CLASS_NAME, "docsum-pmid")
            pmid = pmid_element[0].text.strip() if pmid_element else "No PMID"

            # Extract Authors
            authors_element = article.find_elements(By.CLASS_NAME, "docsum-authors")
            authors = authors_element[0].text.strip() if authors_element else "No Authors Found"

            # Extract Journal & Citation
            journal_element = article.find_elements(By.CLASS_NAME, "full-journal-citation")
            journal = journal_element[0].text.strip() if journal_element else "No Journal Found"

            # Extract DOI
            citation_element = article.find_elements(By.CLASS_NAME, "docsum-journal-citation")
            citation_text = citation_element[0].text if citation_element else ""
            doi = citation_text.split("doi: ")[1].strip() if "doi: " in citation_text else "No DOI Found"

            # Open article link in a new tab to extract Abstract
            driver.execute_script("window.open(arguments[0]);", article_link)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)

            try:
                print("Attempting to extract abstract...")
                # Wait for the abstract element to load using the correct selector
                abstract_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div#eng-abstract > p"))
                )
                abstract = abstract_element.text.strip()

                # Print the first 50 words of the abstract
                abstract_words = abstract.split()
                first_50_words = ' '.join(abstract_words[:50])
                print(f"First 50 words of abstract: {first_50_words}...")

            except Exception as e:
                abstract = "No Abstract Found"
                print(f"Error extracting abstract: {e}")
                print(f"Current URL: {driver.current_url}")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

            # Store data
            articles_data["PMID"].append(pmid)
            articles_data["Title"].append(title)
            articles_data["Authors"].append(authors)
            articles_data["Journal"].append(journal)
            articles_data["DOI"].append(doi)
            articles_data["Article_Link"].append(article_link)
            articles_data["Abstract"].append(abstract)

        except IndexError:
            print(f"IndexError: Skipping article {index + 1} (out of range).")
        except Exception as e:
            print(f"Error scraping article {index + 1}: {e}")

    # Break after the first two pages
    if page_num >= max_pages:
        print("\nReached the maximum number of pages. Exiting...\n")
        break

    # Click "Next" button if available
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next page']"))
        )
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(5)
        page_num += 1
    except:
        print("\n No more pages found. Exiting...\n")
        break

# Save to Excel
df = pd.DataFrame(articles_data)
df.to_excel("PubMed_Myxobacteria_articles_data.xlsx", index=False)
print("\n Data saved to PubMed_Myxobacteria_articles_data.xlsx")

# Close WebDriver
driver.quit()
