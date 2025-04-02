from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv


# Set up ChromeDriver
CHROME_DRIVER_PATH = "C:\\Users\\srinithya\\Desktop\\lenovo\\chromedriver.exe"
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service)

# Open IMDb Top 250 page
url = "https://www.imdb.com/chart/top/"
driver.get(url)

# Wait for the page to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ipc-metadata-list"))
)

# Get movie elements
movie_list = driver.find_elements(By.CSS_SELECTOR, "ul.ipc-metadata-list li.ipc-metadata-list-summary-item")

# List to store extracted data
movie_data = []

# Loop through each movie
for idx, movie in enumerate(movie_list[:250], start=1):  # Extract all 250 movies
    try:
        # Extract title
        title = movie.find_element(By.CSS_SELECTOR, "h3.ipc-title__text").text.strip()
        title = title.split('. ', 1)[-1]  # Removes the numbering before the movie title

        # Extract rating (Updated Selector)
        try:
            rating = movie.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--rating").text.strip()
        except:
            rating = "N/A"  # Handle missing ratings

        # Extract votes (Updated Selector)
        try:
            vote_count = movie.find_element(By.CSS_SELECTOR, "span.ipc-rating-star--voteCount").text.strip()
        except:
            vote_count = "N/A"

        print(f" {title} - Rating: {rating} - Votes: {vote_count}")

        # Store data
        movie_data.append({"Title": title, "IMDb Rating": rating, "Vote Count": vote_count})

    except Exception as e:
        print(f" Error processing movie {idx}: {e}")

# Save to DataFrame
df = pd.DataFrame(movie_data)
df.to_csv("IMDb_Top_250_with_votes.tsv", index=False, encoding="utf-8", sep='\t')

print("Data saved to IMDb_Top_250_with_votes.csv")

# Close the driver
driver.quit()
