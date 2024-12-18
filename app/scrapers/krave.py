import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app import create_app
from app.models import db, ScrapedData
import csv

base_url = "https://kravebeauty.com/"
# go through collections
urls = ["collections/cleansers", "collections/treatments"]

# go through moisturizer and spf 
products = ["products/oat-so-simple-water-cream?view=sl-EA1148A6", "products/beet-the-sun-spf-40-sunscreen?view=sl-EA1148A6"]

driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# get product urls 
for i in range(len(urls)):
    start_url = requests.compat.urljoin(base_url, urls[i])
    driver.get(start_url)
    wait = WebDriverWait(driver, 15)  # Wait for up to 30 seconds

    try:
        # Wait for the modal close button to be visible
        modal_close_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Close dialog']"))
        )

        # Wait for the button to be clickable
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close dialog']"))
        )

        # Execute the JavaScript click
        driver.execute_script("arguments[0].click();", modal_close_button)
        print("Modal close button clicked successfully.")

    except TimeoutException:
        print("Modal close button not found or not clickable within the timeout.")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_cards = soup.find_all("div", class_ = "custom-product-card")

    for product in product_cards:
        content = product.find("div", class_= "cpc__content")
        url = content.find("a").attrs["href"]
        products.append(url)

# go through products 
product_data = []
for product in products:
    try:
        # Navigate to the product page
        url = requests.compat.urljoin(base_url, product)
        driver.get(url)
    except Exception as e:
        print(f"Error navigating to product page {product}: {e}")
        continue

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        # Wait for the modal close button to be visible
        modal_close_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Close dialog']"))
        )

        # Wait for the button to be clickable
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close dialog']"))
        )

        # Execute the JavaScript click
        driver.execute_script("arguments[0].click();", modal_close_button)
        print("Modal close button clicked successfully.")

    except TimeoutException:
        print("Modal close button not found or not clickable within the timeout.")

    try:
        # get category
        #category = soup.find("div", class_ = "metafield-rich_text_field").find("p").text

        # get name 
        name = soup.find("div", class_= "custom-product-info").find("h1").text

        # Wait for the "Ingredients" button to become clickable and click it
        ingredient_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="Accordion--1"]/button'))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ingredient_button)
        driver.execute_script("arguments[0].click();", ingredient_button)
        
    except Exception as e:
        print(f"Error clicking 'Ingredients' button for {product}: {e}")
        continue

    try:
        # Wait for the "All Ingredients" button to appear and click it
        all_ingredient_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ingredient-structure-container"]/div/button'))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", all_ingredient_button)
        driver.execute_script("arguments[0].click();", all_ingredient_button)

    except Exception as e:
        print(f"Error clicking 'View All Ingredients' button for {product}: {e}")
        continue

    try:
        list_display = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "cfm-ing-list-active"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Extract ingredients
        ingredient_list = soup.find_all("li", class_="cfm-ing-list-active")
        ingredients = []
        for ingredient in ingredient_list:
            item = ingredient.find("a").attrs["cfmi-name"]
            ingredients.append(item)
            #print(ingredient.prettify())

        # Append product data
        product_data.append({
            'brand': "Krave Beauty",
            'name': name,
            'link': url,
            #'category': category,
            'ingredients': ingredients
        })

    except Exception as e:
        print(f"Error extracting ingredients for {product}: {e}")
        continue

driver.quit()

with open('krave.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #fieldnames = ['brand', 'name', 'link', 'category', 'ingredients']
    fieldnames = ['brand', 'name', 'link', 'ingredients']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through scraped data and write each item to the CSV
    for product in product_data:
        writer.writerow({
            'brand': product['brand'],
            'name': product['name'],
            'link': product['link'],
            #'category': product['category'],
            'ingredients': product['ingredients']  
        })