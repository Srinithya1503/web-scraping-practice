import requests
import time
import pandas as pd
from bs4 import BeautifulSoup

# Base URLs
PMC_BASE_URL = "https://www.ncbi.nlm.nih.gov/pmc"
EUTILS_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Search query
QUERY = "myxobacteria+AND+genome"

# Headers to prevent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Dictionary to store extracted details
articles_data = {"PMCID": [], "Title": [], "Authors": [], "DOI": [], "Article_Link": [], "Abstract": []}

# Start scraping with pagination (first 5 pages only)
for page in range(1, 6):  # Limit to first 5 pages
    search_url = f"{PMC_BASE_URL}/?term={QUERY}&page={page}"
    print(f"Fetching page {page}: {search_url}...")

    response = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract articles
    articles = soup.find_all("div", class_="rprt")
    if not articles:
        print("No more articles found. Stopping pagination.")
        break

    for index, article in enumerate(articles):
        try:
            # Extract PMCID
            pmcid_tag = article.find("dd")
            pmcid = pmcid_tag.text.strip() if pmcid_tag else "No PMCID"

            # Extract Title
            title_tag = article.find("div", class_="title").find("a")
            title = title_tag.text.strip() if title_tag else "No Title Found"

            # Extract Authors
            authors_tag = article.find("div", class_="desc")
            authors = authors_tag.text.strip() if authors_tag else "No Authors Found"

            # Extract DOI
            doi_tag = article.find("span", class_="doi")
            doi = doi_tag.text.replace("doi:\u00a0", "").strip() if doi_tag else "No DOI Found"

            # Extract Article Link
            article_link = title_tag["href"] if title_tag else "No Link"
            full_article_link = f"{PMC_BASE_URL}{article_link}" if article_link.startswith("/articles") else article_link

            # Fetch the article page to get the abstract (if possible)
            article_response = requests.get(full_article_link, headers=HEADERS)
            article_soup = BeautifulSoup(article_response.text, "html.parser")

            # Try extracting abstract from the article page
            abstract_section = (
                article_soup.find("section", class_="abstract") or
                article_soup.find("div", class_="abstr") or
                article_soup.find("div", class_="abstract")
            )
            if abstract_section:
                abstract_text = " ".join(p.text.strip() for p in abstract_section.find_all(["p", "div"]))
            else:
                abstract_text = None  # Mark as None to try API later

            # If no abstract found, use NCBI E-utilities API
            if not abstract_text and pmcid != "No PMCID":
                efetch_params = {
                    "db": "pmc",
                    "id": pmcid,
                    "retmode": "xml"
                }
                api_response = requests.get(EUTILS_EFETCH, params=efetch_params)
                api_soup = BeautifulSoup(api_response.text, "xml")
                abstract_text = api_soup.find("abstract").text.strip() if api_soup.find("abstract") else "No Abstract Found"

            # Store data
            articles_data["PMCID"].append(pmcid)
            articles_data["Title"].append(title)
            articles_data["Authors"].append(authors)
            articles_data["DOI"].append(doi)
            articles_data["Article_Link"].append(full_article_link)
            articles_data["Abstract"].append(abstract_text)

            print(f"✅ Scraped: {title[:50]}...")  # Show first 50 chars of title
            time.sleep(2)  # Pause to prevent blocking

        except Exception as e:
            print(f"❌ Error scraping article {index + 1} on page {page}: {e}")
            continue

# Save to Excel
df = pd.DataFrame(articles_data)
excel_filename = "pmc_myxobacteria_genome_first_5_pages.xlsx"
df.to_excel(excel_filename, index=False, engine="openpyxl")
print(f"\n✅ Data saved to {excel_filename}")
