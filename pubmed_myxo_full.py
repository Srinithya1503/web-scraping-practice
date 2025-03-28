import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

# Base URLs
PUBMED_BASE_URL = "https://pubmed.ncbi.nlm.nih.gov"
EUTILS_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Search query
QUERY = "myxobacteria+AND+genome"

# Headers to prevent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Dictionary to store extracted details
articles_data = {"PMID": [], "Title": [], "Authors": [], "Journal": [], "DOI": [], "Article_Link": [], "Abstract": []}

# Start scraping with pagination
page = 1
while True:
    search_url = f"{PUBMED_BASE_URL}/?term={QUERY}&sort=date&size=10&page={page}"
    print(f"Fetching page {page}: {search_url}...")

    response = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract articles
    articles = soup.find_all("article", class_="full-docsum")
    if not articles:
        print("No more articles found. Stopping pagination.")
        break

    for index, article in enumerate(articles):
        try:
            # Extract PMID
            pmid_tag = article.get("data-pmid")
            pmid = pmid_tag.strip() if pmid_tag else "No PMID"

            # Extract Title
            title_tag = article.find("a", class_="docsum-title")
            title = title_tag.text.strip() if title_tag else "No Title Found"

            # Extract Authors
            authors_tag = article.find("span", class_="docsum-authors full-authors")
            authors = authors_tag.text.strip() if authors_tag else "No Authors Found"

            # Extract Journal
            journal_tag = article.find("span", class_="docsum-journal-citation full-journal-citation")
            journal = journal_tag.text.strip() if journal_tag else "No Journal Found"

            # Extract DOI
            doi = "No DOI Found"
            citation_text = journal_tag.text if journal_tag else ""
            if "doi: " in citation_text:
                doi = citation_text.split("doi: ")[-1].strip()

            # Extract Article Link
            article_link = title_tag["href"] if title_tag else "No Link"
            full_article_link = f"{PUBMED_BASE_URL}{article_link}" if article_link.startswith("/") else article_link

            # Fetch the article page to get the abstract
            article_response = requests.get(full_article_link, headers=HEADERS)
            article_soup = BeautifulSoup(article_response.text, "html.parser")

            abstract_tag = article_soup.find("div", class_="abstract-content selected")
            abstract = abstract_tag.text.strip() if abstract_tag else "No Abstract Found"

            # If no abstract found, try fetching via API
            if abstract == "No Abstract Found" and pmid != "No PMID":
                efetch_params = {
                    "db": "pubmed",
                    "id": pmid,
                    "retmode": "xml"
                }
                api_response = requests.get(EUTILS_EFETCH, params=efetch_params)
                api_soup = BeautifulSoup(api_response.text, "xml")
                abstract = api_soup.find("AbstractText").text.strip() if api_soup.find("AbstractText") else "No Abstract Found"

            # Store data
            articles_data["PMID"].append(pmid)
            articles_data["Title"].append(title)
            articles_data["Authors"].append(authors)
            articles_data["Journal"].append(journal)
            articles_data["DOI"].append(doi)
            articles_data["Article_Link"].append(full_article_link)
            articles_data["Abstract"].append(abstract)

            # Print article details
            print("\n====================")
            print(f"PMID: {pmid}")
            print(f"Title: {title}")
            print(f"Authors: {authors}")
            print(f"Journal: {journal}")
            print(f"DOI: {doi}")
            print(f"Article Link: {full_article_link}")
            print(f"Abstract: {abstract[:300]}...")  # Truncated abstract for readability
            print("====================\n")

            time.sleep(2)  # Pause to prevent blocking

        except Exception as e:
            print(f"❌ Error scraping article {index + 1} on page {page}: {e}")
            continue

    page += 1  # Move to next page

# Save to Excel
df = pd.DataFrame(articles_data)
excel_filename = "pubmed_myxobacteria_genome.xlsx"
df.to_excel(excel_filename, index=False, engine="openpyxl")
print(f"\n✅ Data saved to {excel_filename}")
