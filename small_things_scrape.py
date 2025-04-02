import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Set up undetected Chrome driver
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Function to scroll the page
def scroll_page():
    for _ in range(random.randint(3, 7)):
        driver.execute_script("window.scrollBy(0, 400);")
        time.sleep(random.uniform(1, 3))

# Function to scrape questions from a single page
def scrape_page(url):
    driver.get(url)
    time.sleep(random.uniform(5, 10))
    scroll_page()

    question_links = []
    question_titles = []

    try:
        question_containers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.entry-inner')))
        for container in question_containers:
            try:
                link_element = container.find_element(By.CSS_SELECTOR, 'a')
                title = link_element.text.strip()
                question_url = link_element.get_attribute('href')

                if question_url and title:
                    question_titles.append(title)
                    question_links.append(question_url)
            except Exception as e:
                print(f"Error extracting link: {e}")
    except Exception as e:
        print(f"Error fetching question list: {e}")

    return question_titles, question_links

# Function to scrape content from individual question pages
def scrape_question_pages(question_titles, question_links):
    scraped_data = []
    for title, question_url in zip(question_titles, question_links):
        try:
            time.sleep(random.uniform(10, 20))
            driver.get(question_url)
            scroll_page()

            question_text = ""
            try:
                paragraphs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.entry-body p')))
                question_text = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
            except Exception as e:
                print(f"Error extracting text for {title}: {e}")

            scraped_data.append(f"Question: {title}\nLink: {question_url}\nText:\n{question_text}\n" + "="*80)
        except Exception as e:
            print(f"Error scraping question: {e}")
    
    return scraped_data

# Main scraping logic with pagination
base_url = "https://schaechter.asmblog.org/schaechter/talmudic_questions/"
page_number = 1
all_scraped_data = []

while True:
    current_url = f"{base_url}page/{page_number}/" if page_number > 1 else base_url
    print(f"Scraping page: {current_url}")
    
    titles, links = scrape_page(current_url)
    
    if not links:  # Stop if no more links are found (end of pagination)
        print("No more pages to scrape.")
        break
    
    all_scraped_data.extend(scrape_question_pages(titles, links))
    page_number += 1

# Save to file
with open("talmudic_questions_all_pages.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_scraped_data))

driver.quit()
print("Scraping completed. Data saved to talmudic_questions_all_pages.txt")
