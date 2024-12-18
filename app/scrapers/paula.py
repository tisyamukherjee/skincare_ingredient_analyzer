import requests
from bs4 import BeautifulSoup
import requests.compat
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from app import create_app
from app.models import db, ScrapedData
import csv
import time

# Function to check for the "Next Page" button
def check_next_page():
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next Page"]')
        return next_button
    except NoSuchElementException:
        return None

def close_popup_if_present(driver):
    try:
        # Wait for the close button of the popup to be visible and clickable
        close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[aria-label="Close Dialog"]')))
        close_button.click()
        print("Popup closed.")
    except TimeoutException:
        print("No popup appeared.")
    except NoSuchElementException:
        print("Close button not found.")

start_url = "https://www.paulaschoice.com/skin-care-products"
base_url = "https://www.paulaschoice.com/"

driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 5)

driver.get(start_url)
time.sleep(5)

brand = "Paula's Choice"

# get product urls one page at a time 
product_urls = []
soup = BeautifulSoup(driver.page_source, "html.parser")

while True:
    products = soup.find_all("div", class_= "ProductListstyles__Tile-sc-12w7nlo-2 dQuBnx")
    for product in products:
        url = product.find("a")["href"]
        url = requests.compat.urljoin(base_url, url)
        product_urls.append(url)
    
    next_button = check_next_page()
    if next_button:
        try:
            next_button.click()
            time.sleep(3)  # Wait for the next page to load
        except TimeoutException:
            print("Failed to load next page. Exiting.")
            break
    else:
        print("No more pages found.")
        break

# go through each product 
product_data = []
for url in product_urls:
    driver.get(url)
    close_popup_if_present(driver)

    # # Wait for the element to be clickable
    # ingredient_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//h2[text()="Ingredients"]/ancestor::span[@role="button"]')))
    # # Optionally, click the element
    # driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ingredient_tab)
    # driver.execute_script("arguments[0].click();", ingredient_tab)
    try:
        # Wait for the Ingredients tab to be clickable
        ingredient_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//h2[text()="Ingredients"]/ancestor::span[@role="button"]'))
        )
        
        # Scroll the element into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ingredient_tab)
        
        # Click the Ingredients tab
        driver.execute_script("arguments[0].click();", ingredient_tab)
        print(f"Successfully clicked the Ingredients tab on {url}")
    
    except TimeoutException:
        print(f"Timeout: Ingredients tab not found or clickable on {url}")
        continue  # Skip to the next URL
    
    except Exception as e:
        print(f"An error occurred on {url}: {e}")
        continue  # Skip to the next URL

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # get product name
    name = soup.find("div", class_= "large2 normalcase").get_text()

    # get ingredients
    ingredient_list = soup.find("ul", {"aria-label": "All Ingredients"})

    if not ingredient_list:
        continue

    ingredient_items = ingredient_list.find_all("li")
    ingredients = []
    for ingredient in ingredient_items:
        item = ingredient.find("div").get_text()
        ingredients.append(item)
    
    product_data.append({
                'brand': brand,
                'name': name,
                'link': url,
                'ingredients': ingredients
            })

driver.quit()

with open('paula.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['brand', 'name', 'link', 'ingredients']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through scraped data and write each item to the CSV
    for product in product_data:
        writer.writerow({
            'brand': product['brand'],
            'name': product['name'],
            'link': product['link'],
            'ingredients': product['ingredients']  
        })

