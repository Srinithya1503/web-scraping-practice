import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from tqdm import tqdm

# Define headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.amazon.com/',
    'Connection': 'keep-alive',
}

def scrape_amazon_products(search_query, output_file, max_pages=5):
    search_query = search_query.replace(" ", "+")
    
    base_url = f'https://www.amazon.in/s?k={search_query}'
    all_data = []
    page = 1

    while True:
        url = f"{base_url}&page={page}"
        print(f"Fetching data from Amazon (Page {page})...")
        
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data. Error: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all product containers
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        if not products:
            print("No more products found. Stopping pagination.")
            break

        print(f"Found {len(products)} products on page {page}.")

        for product in tqdm(products, desc=f"Processing Page {page}", unit="product"):
            # Extract product name
            name_tag = product.find('h2', class_='a-size-medium a-spacing-none a-color-base a-text-normal')
            name = name_tag.text.strip() if name_tag else "N/A"

            # Extract product price
            price_whole_tag = product.find('span', class_='a-price-whole')
            price_symbol_tag = product.find('span', class_='a-price-symbol')
            price_fraction_tag = product.find('span', class_='a-price-fraction')

            if price_whole_tag:
                price = price_whole_tag.text.strip()
                if price_symbol_tag:
                    price = f"{price_symbol_tag.text.strip()}{price}"  # Add currency symbol
                if price_fraction_tag:
                    price = f"{price}.{price_fraction_tag.text.strip()}"  # Add fraction if available
            else:
                price = "N/A"

            # Extract product rating
            rating_tag = product.find('span', class_='a-icon-alt')
            rating = rating_tag.text.strip() if rating_tag else "N/A"

            # Append data to all_data
            if name != "N/A" and price != "N/A":
                all_data.append({
                    'Name': name,
                    'Price': price,
                    'Rating': rating
                })

        # Stop if max pages are reached
        if page >= max_pages:
            print("Reached maximum pages limit. Stopping pagination.")
            break
        
        # Random delay to avoid detection
        time.sleep(random.uniform(3, 7))

        # Move to the next page
        page += 1

    # Save data to Excel
    df = pd.DataFrame(all_data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == '__main__':
    search_query = "Lenovo laptop Intel Core i5"
    output_file = 'amazon_lenovo_laptop_intel_icore_i5_data.xlsx'
    scrape_amazon_products(search_query, output_file, max_pages=10)  # Increase max_pages as needed
