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
import time 

base_url = "https://www.peachandlily.com"
start_url = "https://www.peachandlily.com/collections/"

driver_path = '/opt/homebrew/bin/chromedriver'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10)

# get all categories 
driver.get(start_url)
category_list = driver.find_elements(By.XPATH, '//*[@id="sidebar-menu"]/div[2]/div/ul/li[a]')
category_list = category_list[:12]
category_urls = []

for category in category_list:
   url = category.find_element(By.TAG_NAME, "a").get_attribute("href")
   url = url.replace("#", "/")
   category_urls.append(url)

product_urls = []
for url in category_urls:
   driver.get(url)
   product_cards = driver.find_elements(By.CLASS_NAME, 'provider-wrapper')
   for product in product_cards:
        product_url = product.find_element(By.TAG_NAME, "a").get_attribute("href")
        product_url = requests.compat.urljoin(base_url, product_url)
        product_urls.append(product_url)

product_data = []
for product in product_urls:
    ingredients = ""
    try:
        # Navigate to the product page
        driver.get(product)

        # get brand name 
        brand = driver.find_element(By.CLASS_NAME, 'info__vendor').text
        # get product name  
        name = driver.find_element(By.CLASS_NAME, 'info__header-title').text
        # get category 
        #category = driver.find_element(By.CLASS_NAME, 'info__headline').text

        # Click the "Ingredient" tab
        try:
            ingredient_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[1]/ul/li[3]/a'))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ingredient_tab)
            driver.execute_script("arguments[0].click();", ingredient_tab)
        except Exception as e:
            print(f"Error clicking 'Ingredient Tab' for product {product}: {e}")
            continue  # Skip to the next product if this fails

        # Click the "View All Ingredients" tab
        try:
            view_all = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'ingredients__all'))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", view_all)
            driver.execute_script("arguments[0].click();", view_all)
        except Exception as e:
            # print(f"Error clicking 'View All Ingredients' tab for product {product}: {e}")
            ingredients = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div/div/div[1]/div[3]/div[2]/div/div/div[2]/div[3]/div/div/div/div').text  
        
        # Extract the ingredients
        try:
            time.sleep(5)
            ingredients = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'all-ingredients'))
            ).text
        except Exception as e:
            print(f"Error extracting ingredients for product {product}: {e}")

        if ingredients == "See individual product pages for full ingredient lists.": 
            continue
        elif ingredients == "See full ingredient list on packaging.":
            continue 
        # Append product data
        product_data.append({
            'brand': brand,
            'name': name,
            'link': product,
            #'category': category,
            'ingredients': ingredients
        })

    except Exception as e:
        print(f"An unexpected error occurred for product {product}: {e}")
    
driver.quit()

with open('peachandlily.csv', 'w', newline='', encoding='utf-8') as csvfile:
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

